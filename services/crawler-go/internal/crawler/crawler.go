package crawler

import (
	"fmt"
	"net/url"
	"strings"
	"time"

	"github.com/gocolly/colly/v2"

	"github.com/FelixBitSoul/lumina/crawler/internal/brainclient"
	"github.com/FelixBitSoul/lumina/crawler/internal/config"
	"github.com/FelixBitSoul/lumina/crawler/internal/extract"
)

type Crawler struct {
	task   config.Task
	brain  *brainclient.Client
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
		colly.AllowedDomains(c.task.AllowedDomains...),
		// Colly depth starts at 1 for seeds. Our config uses depth 0 for seeds,
		// so we map config max_depth N to colly.MaxDepth(N+1).
		colly.MaxDepth(c.task.MaxDepth+1),
	)

	// User agent
	if c.task.UserAgent != "" {
		collector.UserAgent = c.task.UserAgent
	}

	collector.SetRequestTimeout(time.Duration(c.task.RequestTimeoutSeconds) * time.Second)

	// Rate limiting + concurrency
	delay := time.Minute / time.Duration(c.task.RateLimit.RequestsPerMinute)
	_ = collector.Limit(&colly.LimitRule{
		DomainGlob:  "*",
		Parallelism: c.task.Concurrency,
		Delay:       delay,
	})

	retryOn := make(map[int]struct{}, len(c.task.Retry.RetryOnStatus))
	for _, s := range c.task.Retry.RetryOnStatus {
		retryOn[s] = struct{}{}
	}

	scheduleRetry := func(r *colly.Request, reason string) {
		if r == nil || r.URL == nil {
			return
		}
		ctx := r.Ctx
		var attempt int
		if v := ctx.GetAny("retry_attempt"); v != nil {
			if i, ok := v.(int); ok {
				attempt = i
			}
		}
		attempt++
		if attempt >= c.task.Retry.MaxAttempts {
			c.logger("[Task:%s] [RetryGiveUp] %s (attempt=%d/%d): %s",
				c.task.Name, r.URL.String(), attempt, c.task.Retry.MaxAttempts, reason)
			return
		}

		ctx.Put("retry_attempt", attempt)

		backoff := time.Duration(c.task.Retry.BackoffSeconds) * time.Second * time.Duration(attempt)
		if backoff > 0 {
			c.logger("[Task:%s] [Retry] %s in %s (attempt=%d/%d): %s",
				c.task.Name, r.URL.String(), backoff, attempt, c.task.Retry.MaxAttempts, reason)
		} else {
			c.logger("[Task:%s] [Retry] %s (attempt=%d/%d): %s",
				c.task.Name, r.URL.String(), attempt, c.task.Retry.MaxAttempts, reason)
		}

		// Re-request with the same context and depth; Colly will keep depth.
		time.AfterFunc(backoff, func() {
			// We intentionally drop original request headers here; User-Agent and
			// other defaults are configured on the Collector itself.
			_ = collector.Request(r.Method, r.URL.String(), r.Body, ctx, nil)
		})
	}

	collector.OnRequest(func(r *colly.Request) {
		c.logger("[Task:%s] GET %s", c.task.Name, r.URL.String())
	})

	collector.OnError(func(r *colly.Response, err error) {
		if r != nil && r.Request != nil && r.Request.URL != nil {
			c.logger("[Task:%s] [Error] %s: %v", c.task.Name, r.Request.URL.String(), err)
			scheduleRetry(r.Request, err.Error())
			return
		}
		c.logger("[Task:%s] [Error] %v", c.task.Name, err)
	})

	collector.OnResponse(func(r *colly.Response) {
		pageURL := r.Request.URL
		// map Colly depth (seed=1) to config depth (seed=0)
		configDepth := r.Request.Depth - 1

		if _, ok := retryOn[r.StatusCode]; ok {
			scheduleRetry(r.Request, fmt.Sprintf("status=%d", r.StatusCode))
			return
		}
		if r.StatusCode < 200 || r.StatusCode >= 300 {
			// Non-success response; don't ingest.
			c.logger("[Task:%s] [HTTP] %s status=%d", c.task.Name, pageURL.String(), r.StatusCode)
			return
		}

		discoverLinks := configDepth < c.task.MaxDepth
		article, err := extract.Extract(pageURL, r.Body, c.task.ContentSelector, discoverLinks)
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

		// Schedule discovered links (Colly enforces MaxDepth + AllowedDomains too)
		if discoverLinks {
			for _, link := range article.Discovered {
				c.tryVisit(collector, pageURL, link)
			}
		}
	})

	// Visit seeds at depth 0
	for _, seed := range c.task.Seeds {
		u, err := url.Parse(normalizeURL(seed))
		if err != nil {
			continue
		}
		// Seed depth will be 1 in Colly (mapped from config depth 0).
		_ = collector.Visit(u.String())
	}

	collector.Wait()
	return nil
}

func (c *Crawler) tryVisit(collector *colly.Collector, base *url.URL, raw string) {
	u, err := base.Parse(raw)
	if err != nil {
		return
	}

	normalized := normalizeURL(u.String())
	// Colly handles allowed domains, max depth, and URL revisit prevention.
	_ = collector.Visit(normalized)
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

