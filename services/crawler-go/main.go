package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"sync"
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
	Name           string          `yaml:"name"`
	Seeds          []string        `yaml:"seeds"`
	MaxDepth       int             `yaml:"max_depth"`
	AllowedDomains []string        `yaml:"allowed_domains"`
	ContentSelector string         `yaml:"content_selector"`
	RateLimit      RateLimitConfig `yaml:"rate_limit"`
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

// runTask executes a single CrawlTaskConfig: BFS over seeds up to MaxDepth,
// respecting allowed domains and rate limit.
func runTask(job *CrawlTaskConfig) {
	if len(job.Seeds) == 0 {
		fmt.Printf("[Task:%s] No seeds provided, skipping.\n", job.Name)
		return
	}
	if job.MaxDepth <= 0 {
		job.MaxDepth = 1
	}

	fmt.Printf("[Task:%s] Starting. Seeds=%d, MaxDepth=%d\n", job.Name, len(job.Seeds), job.MaxDepth)

	taskChan := make(chan Task, 128)
	resChan := make(chan Result, 128)
	var wg sync.WaitGroup

	limiter := NewRateLimiter(job.RateLimit)
	defer limiter.Stop()

	// Worker pool
	workerCount := 4
	for i := 0; i < workerCount; i++ {
		wg.Add(1)
		go worker(i+1, taskChan, resChan, &wg, limiter)
	}

	// BFS queue
	seen := make(map[string]bool)
	var mu sync.Mutex

	go func() {
		defer close(taskChan)
		queue := make([]Task, 0)
		for _, seed := range job.Seeds {
			if !isAllowedDomain(seed, job.AllowedDomains) {
				continue
			}
			queue = append(queue, Task{URL: seed, Depth: 0, Job: job})
		}

		for len(queue) > 0 {
			task := queue[0]
			queue = queue[1:]

			mu.Lock()
			if seen[task.URL] {
				mu.Unlock()
				continue
			}
			seen[task.URL] = true
			mu.Unlock()

			taskChan <- task

			if task.Depth >= job.MaxDepth {
				continue
			}

			// For simplicity we enqueue discovered links in the worker itself by
			// posting back into the queue via a closure (not implemented here to keep Go side light).
			// In later phases, we can extend this to full link graph crawling.
		}
	}()

	go func() {
		wg.Wait()
		close(resChan)
	}()

	for res := range resChan {
		if res.Error != nil {
			fmt.Printf("[Task:%s] [Error] %s: %v\n", job.Name, res.URL, res.Error)
		} else {
			fmt.Printf("[Task:%s] [Indexed] %s (%s)\n", job.Name, res.Title, res.URL)
		}
	}

	fmt.Printf("[Task:%s] Done.\n", job.Name)
}

// worker processes tasks and sends cleaned content to the Python AI service.
func worker(id int, tasks <-chan Task, results chan<- Result, wg *sync.WaitGroup, limiter *RateLimiter) {
	defer wg.Done()
	client := http.Client{Timeout: 15 * time.Second}

	for task := range tasks {
		if !isAllowedDomain(task.URL, task.Job.AllowedDomains) {
			results <- Result{URL: task.URL, Error: fmt.Errorf("domain not allowed")}
			continue
		}

		limiter.Wait()

		resp, err := client.Get(task.URL)
		if err != nil {
			results <- Result{URL: task.URL, Error: err}
			continue
		}
		bodyBytes, err := io.ReadAll(resp.Body)
		resp.Body.Close()
		if err != nil {
			results <- Result{URL: task.URL, Error: err}
			continue
		}

		// Use go-readability to extract main article content
		parsedURL, err := url.Parse(task.URL)
		if err != nil {
			results <- Result{URL: task.URL, Error: fmt.Errorf("invalid url: %w", err)}
			continue
		}

		article, err := readability.FromReader(bytes.NewReader(bodyBytes), parsedURL)
		if err != nil {
			results <- Result{URL: task.URL, Error: fmt.Errorf("readability failed: %w", err)}
			continue
		}

		title := article.Title
		content := article.TextContent
		if task.Job.ContentSelector != "" {
			// Fallback: if user provided a selector, try to refine content with goquery.
			doc, err := goquery.NewDocumentFromReader(bytes.NewReader(bodyBytes))
			if err == nil {
				selected := doc.Find(task.Job.ContentSelector).Text()
				if selected != "" {
					content = selected
				}
			}
		}

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
			results <- Result{URL: task.URL, Error: fmt.Errorf("connect AI service: %w", err)}
			continue
		}
		apiResp.Body.Close()

		results <- Result{URL: task.URL, Title: title, Error: nil}
	}
}
