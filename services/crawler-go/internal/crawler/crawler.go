package crawler

import (
	"fmt"
	"net/url"
	"strings"
	"sync"
	"time"

	"github.com/gocolly/colly/v2"

	"github.com/FelixBitSoul/lumina/crawler/internal/brainclient"
	"github.com/FelixBitSoul/lumina/crawler/internal/config"
	"github.com/FelixBitSoul/lumina/crawler/internal/extract"
)

type Crawler struct {
	task   config.Task
	brain  *brainclient.Client
	seen   sync.Map // string -> struct{}
	logger func(format string, args ...any)
}

func New(task config.Task, brain *brainclient.Client, logger func(format string, args ...any)) *Crawler {
	if logger == nil {
		logger = func(string, ...any) {}
	}
	return &Crawler{
		task:   task,
		brain: brain,
		logger: logger,
	}
}

func (c *Crawler) Run() error {
	collector := colly.NewCollector(
		colly.Async(true),
	)

	// User agent
	if c.task.UserAgent != "" {
		collector.UserAgent = c.task.UserAgent
	}

	// Rate limiting + concurrency
	delay := time.Minute / time.Duration(c.task.RateLimit.RequestsPerMinute)
	_ = collector.Limit(&colly.LimitRule{
		DomainGlob:  "*",
		Parallelism: c.task.Concurrency,
		Delay:       delay,
	})

	collector.OnRequest(func(r *colly.Request) {
		c.logger("[Task:%s] GET %s", c.task.Name, r.URL.String())
	})

	collector.OnError(func(r *colly.Response, err error) {
		if r != nil && r.Request != nil && r.Request.URL != nil {
			c.logger("[Task:%s] [Error] %s: %v", c.task.Name, r.Request.URL.String(), err)
			return
		}
		c.logger("[Task:%s] [Error] %v", c.task.Name, err)
	})

	collector.OnResponse(func(r *colly.Response) {
		pageURL := r.Request.URL
		depth := r.Ctx.GetAny("depth").(int)

		article, err := extract.Extract(pageURL, r.Body, c.task.ContentSelector, depth < c.task.MaxDepth)
		if err != nil {
			c.logger("[Task:%s] [ExtractError] %s: %v", c.task.Name, pageURL.String(), err)
			return
		}

		if err := c.brain.Ingest(brainclient.Document{
			URL:     pageURL.String(),
			Title:   article.Title,
			Content: article.Text,
		}); err != nil {
			c.logger("[Task:%s] [IngestError] %s: %v", c.task.Name, pageURL.String(), err)
		}

		// Schedule discovered links
		if depth < c.task.MaxDepth {
			for _, link := range article.Discovered {
				c.tryVisit(collector, pageURL, link, depth+1)
			}
		}
	})

	// Visit seeds at depth 0
	for _, seed := range c.task.Seeds {
		if !isAllowedDomain(seed, c.task.AllowedDomains) {
			continue
		}
		if !c.markSeen(normalizeURL(seed)) {
			continue
		}
		u, err := url.Parse(seed)
		if err != nil {
			continue
		}
		ctx := colly.NewContext()
		ctx.Put("depth", 0)
		if err := collector.Request("GET", u.String(), nil, ctx, nil); err != nil {
			c.logger("[Task:%s] [SeedError] %s: %v", c.task.Name, seed, err)
		}
	}

	collector.Wait()
	return nil
}

func (c *Crawler) tryVisit(collector *colly.Collector, base *url.URL, raw string, depth int) {
	if depth > c.task.MaxDepth {
		return
	}
	u, err := base.Parse(raw)
	if err != nil {
		return
	}

	normalized := normalizeURL(u.String())
	if !isAllowedDomain(normalized, c.task.AllowedDomains) {
		return
	}
	if !c.markSeen(normalized) {
		return
	}

	ctx := colly.NewContext()
	ctx.Put("depth", depth)
	_ = collector.Request("GET", normalized, nil, ctx, nil)
}

func (c *Crawler) markSeen(u string) bool {
	_, loaded := c.seen.LoadOrStore(u, struct{}{})
	return !loaded
}

func normalizeURL(raw string) string {
	u, err := url.Parse(raw)
	if err != nil {
		return raw
	}
	u.Fragment = ""
	// Reduce duplicate URLs caused by trailing slashes
	if u.Path != "/" {
		u.Path = strings.TrimSuffix(u.Path, "/")
	}
	return u.String()
}

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

func ValidateTask(t config.Task) error {
	if len(t.Seeds) == 0 {
		return fmt.Errorf("task %q has no seeds", t.Name)
	}
	if t.RateLimit.RequestsPerMinute <= 0 {
		return fmt.Errorf("task %q has invalid rate_limit.requests_per_minute", t.Name)
	}
	if t.Concurrency <= 0 {
		return fmt.Errorf("task %q has invalid concurrency", t.Name)
	}
	if t.MaxDepth < 0 {
		return fmt.Errorf("task %q has invalid max_depth", t.Name)
	}
	return nil
}

