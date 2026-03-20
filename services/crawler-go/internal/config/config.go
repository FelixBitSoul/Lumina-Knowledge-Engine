package config

import (
	"fmt"
	"os"

	"gopkg.in/yaml.v3"
)

// RateLimit controls how fast we crawl for a given task.
type RateLimit struct {
	RequestsPerMinute int `yaml:"requests_per_minute"`
}

type Retry struct {
	// MaxAttempts includes the first request. Example: 3 = initial try + 2 retries.
	MaxAttempts int `yaml:"max_attempts"`
	// BackoffSeconds is a simple linear backoff multiplier (attempt index * backoff).
	BackoffSeconds int `yaml:"backoff_seconds"`
	// RetryOnStatus is the list of HTTP status codes to retry on (e.g. [429, 500, 502, 503, 504]).
	RetryOnStatus []int `yaml:"retry_on_status"`
}

// Task represents a logical crawling job driven by configuration.
type Task struct {
	Name                  string    `yaml:"name"`
	Seeds                 []string  `yaml:"seeds"`
	MaxDepth              int       `yaml:"max_depth"`
	Concurrency           int       `yaml:"concurrency"`
	RequestTimeoutSeconds int       `yaml:"request_timeout_seconds"`
	AllowedDomains        []string  `yaml:"allowed_domains"`
	ContentSelector       string    `yaml:"content_selector"`
	UserAgent             string    `yaml:"user_agent"`
	Collection            string    `yaml:"collection"`
	RateLimit             RateLimit `yaml:"rate_limit"`
	Retry                 Retry     `yaml:"retry"`
}

// Config is the top-level crawler configuration.
type Config struct {
	Tasks []Task `yaml:"tasks"`
}

// Load reads YAML configuration from disk. It respects the CRAWLER_CONFIG
// environment variable for overriding the default path.
func Load(defaultPath string) (*Config, error) {
	path := os.Getenv("CRAWLER_CONFIG")
	if path == "" {
		path = defaultPath
	}

	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read config %q: %w", path, err)
	}
	fmt.Printf("load config from path: %s\n", path)

	var cfg Config
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return nil, fmt.Errorf("parse yaml %q: %w", path, err)
	}

	// Basic validation and normalization
	for i := range cfg.Tasks {
		t := &cfg.Tasks[i]
		if t.Name == "" {
			t.Name = fmt.Sprintf("task-%d", i+1)
		}
		if t.MaxDepth < 1 {
			t.MaxDepth = 1
		}
		if t.Concurrency <= 0 {
			t.Concurrency = 8
		}
		if t.RequestTimeoutSeconds <= 0 {
			t.RequestTimeoutSeconds = 15
		}
		if t.RateLimit.RequestsPerMinute <= 0 {
			t.RateLimit.RequestsPerMinute = 30
		}

		if t.Retry.MaxAttempts <= 0 {
			t.Retry.MaxAttempts = 3
		}
		if t.Retry.BackoffSeconds < 0 {
			t.Retry.BackoffSeconds = 0
		}
		if len(t.Retry.RetryOnStatus) == 0 {
			t.Retry.RetryOnStatus = []int{429, 500, 502, 503, 504}
		}
	}

	return &cfg, nil
}
