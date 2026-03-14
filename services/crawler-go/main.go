package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"time"

	readability "github.com/go-shiori/go-readability"
	"github.com/PuerkitoBio/goquery"
	"gopkg.in/yaml.v3"
)

// Task represents a single URL to crawl with task-specific config.
type Task struct {
	URL   string
	Depth int
	Job   *CrawlTaskConfig
}

// Result carries the scraped data or an error.
type Result struct {
	URL   string
	Title string
	Error error
}

// RateLimitConfig controls how fast we crawl.
type RateLimitConfig struct {
	RequestsPerMinute int `yaml:"requests_per_minute"`
}

// CrawlTaskConfig defines a logical crawling task.
type CrawlTaskConfig struct {
	Name            string          `yaml:"name"`
	Seeds           []string        `yaml:"seeds"`
	MaxDepth        int             `yaml:"max_depth"`
	AllowedDomains  []string        `yaml:"allowed_domains"`
	ContentSelector string          `yaml:"content_selector"`
	UserAgent       string          `yaml:"user_agent"`
	RateLimit       RateLimitConfig `yaml:"rate_limit"`
}

// CrawlerConfig is the top-level YAML configuration.
type CrawlerConfig struct {
	Tasks []CrawlTaskConfig `yaml:"tasks"`
}

func loadConfig() (CrawlerConfig, error) {
	path := os.Getenv("CRAWLER_CONFIG")
	if path == "" {
		path = "config.yaml"
	}

	data, err := os.ReadFile(path)
	if err != nil {
		return CrawlerConfig{}, fmt.Errorf("failed to read config: %w", err)
	}

	var cfg CrawlerConfig
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return CrawlerConfig{}, fmt.Errorf("failed to parse yaml: %w", err)
	}

	return cfg, nil
}

// simple domain check based on hostname
func isAllowedDomain(rawURL string, allowed []string) bool {
	if len(allowed) == 0 {
		return true
	}
	u, err := url.Parse(rawURL)
	if err != nil {
		return false
	}
	host := u.Hostname()
	for _, d := range allowed {
		if host == d || host == "www."+d {
			return true
		}
	}
	return false
}

// basic token-bucket-style limiter using a ticker
type RateLimiter struct {
	ticker *time.Ticker
}

func NewRateLimiter(cfg RateLimitConfig) *RateLimiter {
	rpm := cfg.RequestsPerMinute
	if rpm <= 0 {
		// default to 30 rpm
		rpm = 30
	}
	interval := time.Minute / time.Duration(rpm)
	return &RateLimiter{
		ticker: time.NewTicker(interval),
	}
}

func (rl *RateLimiter) Wait() {
	<-rl.ticker.C
}

func (rl *RateLimiter) Stop() {
	rl.ticker.Stop()
}

func main() {
	cfg, err := loadConfig()
	if err != nil {
		fmt.Printf("[Crawler] Failed to load config: %v\n", err)
		return
	}
	if len(cfg.Tasks) == 0 {
		fmt.Println("[Crawler] No tasks defined in config. Exiting.")
		return
	}

	fmt.Println(">>> Lumina Configuration-Driven Crawler Started")

	for _, job := range cfg.Tasks {
		runTask(&job)
	}
}

// crawlURL fetches, extracts main content, sends it to Brain API and
// optionally discovers next-layer links (for BFS) when depth < MaxDepth.
func crawlURL(task Task, job *CrawlTaskConfig, client *http.Client, limiter *RateLimiter) ([]string, Result) {
	if !isAllowedDomain(task.URL, job.AllowedDomains) {
		return nil, Result{URL: task.URL, Error: fmt.Errorf("domain not allowed")}
	}

	limiter.Wait()

	// Build request with optional User-Agent
	req, err := http.NewRequest(http.MethodGet, task.URL, nil)
	if err != nil {
		return nil, Result{URL: task.URL, Error: err}
	}
	if ua := job.UserAgent; ua != "" {
		req.Header.Set("User-Agent", ua)
	}

	// Basic retry for 429 / transient errors
	var bodyBytes []byte
	for attempt := 0; attempt < 3; attempt++ {
		resp, err := client.Do(req)
		if err != nil {
			if attempt == 2 {
				return nil, Result{URL: task.URL, Error: err}
			}
			time.Sleep(time.Duration(attempt+1) * time.Second)
			continue
		}

		if resp.StatusCode == http.StatusTooManyRequests {
			resp.Body.Close()
			if attempt == 2 {
				return nil, Result{URL: task.URL, Error: fmt.Errorf("received 429 too many requests")}
			}
			time.Sleep(time.Duration(attempt+1) * time.Second)
			continue
		}

		bodyBytes, err = io.ReadAll(resp.Body)
		resp.Body.Close()
		if err != nil {
			if attempt == 2 {
				return nil, Result{URL: task.URL, Error: err}
			}
			time.Sleep(time.Duration(attempt+1) * time.Second)
			continue
		}
		// success
		break
	}
	if bodyBytes == nil {
		return nil, Result{URL: task.URL, Error: fmt.Errorf("empty body")}
	}

	parsedURL, err := url.Parse(task.URL)
	if err != nil {
		return nil, Result{URL: task.URL, Error: fmt.Errorf("invalid url: %w", err)}
	}

	// Use go-readability to extract main article content
	article, err := readability.FromReader(bytes.NewReader(bodyBytes), parsedURL)
	if err != nil {
		return nil, Result{URL: task.URL, Error: fmt.Errorf("readability failed: %w", err)}
	}

	title := article.Title
	content := article.TextContent
	discovered := []string{}

	// Optional refinement + link discovery with goquery
	if job.ContentSelector != "" || task.Depth < job.MaxDepth {
		doc, err := goquery.NewDocumentFromReader(bytes.NewReader(bodyBytes))
		if err == nil {
			if job.ContentSelector != "" {
				selected := doc.Find(job.ContentSelector).Text()
				if selected != "" {
					content = selected
				}
			}

			if task.Depth < job.MaxDepth {
				doc.Find("a[href]").Each(func(_ int, s *goquery.Selection) {
					href, ok := s.Attr("href")
					if !ok || href == "" {
						return
					}
					link, err := parsedURL.Parse(href)
					if err != nil {
						return
					}
					discovered = append(discovered, link.String())
				})
			}
		}
	}

	// Send to Brain API
	payload := map[string]string{
		"url":     task.URL,
		"title":   title,
		"content": content,
	}
	jsonData, _ := json.Marshal(payload)

	apiURL := os.Getenv("BRAIN_INGEST_URL")
	if apiURL == "" {
		apiURL = "http://localhost:8000/ingest"
	}

	apiResp, err := http.Post(apiURL, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return discovered, Result{URL: task.URL, Error: fmt.Errorf("connect AI service: %w", err)}
	}
	apiResp.Body.Close()

	return discovered, Result{URL: task.URL, Title: title, Error: nil}
}

// runTask executes a single CrawlTaskConfig: BFS over seeds up to MaxDepth,
// respecting allowed domains and rate limit. Implemented sequentially for
// simplicity and to avoid deadlocks.
func runTask(job *CrawlTaskConfig) {
	if len(job.Seeds) == 0 {
		fmt.Printf("[Task:%s] No seeds provided, skipping.\n", job.Name)
		return
	}
	if job.MaxDepth <= 0 {
		job.MaxDepth = 1
	}

	fmt.Printf("[Task:%s] Starting. Seeds=%d, MaxDepth=%d\n", job.Name, len(job.Seeds), job.MaxDepth)

	limiter := NewRateLimiter(job.RateLimit)
	defer limiter.Stop()

	client := &http.Client{Timeout: 15 * time.Second}

	seen := make(map[string]bool)
	queue := make([]Task, 0)

	// Seed initial URLs as depth 0
	for _, seed := range job.Seeds {
		if !isAllowedDomain(seed, job.AllowedDomains) {
			continue
		}
		if seen[seed] {
			continue
		}
		seen[seed] = true
		queue = append(queue, Task{URL: seed, Depth: 0, Job: job})
	}

	for len(queue) > 0 {
		task := queue[0]
		queue = queue[1:]

		discovered, res := crawlURL(task, job, client, limiter)
		if res.Error != nil {
			fmt.Printf("[Task:%s] [Error] %s: %v\n", job.Name, res.URL, res.Error)
		} else {
			fmt.Printf("[Task:%s] [Indexed] %s (%s)\n", job.Name, res.Title, res.URL)
		}

		// Enqueue newly discovered links for next depths
		nextDepth := task.Depth + 1
		if nextDepth > job.MaxDepth {
			continue
		}
		for _, u := range discovered {
			if !isAllowedDomain(u, job.AllowedDomains) {
				continue
			}
			if seen[u] {
				continue
			}
			seen[u] = true
			queue = append(queue, Task{URL: u, Depth: nextDepth, Job: job})
		}
	}

	fmt.Printf("[Task:%s] Done.\n", job.Name)
}
