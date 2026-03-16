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

// Task represents a logical crawling job driven by configuration.
type Task struct {
	Name            string    `yaml:"name"`
	Seeds           []string  `yaml:"seeds"`
	MaxDepth        int       `yaml:"max_depth"`
	Concurrency     int       `yaml:"concurrency"`
	AllowedDomains  []string  `yaml:"allowed_domains"`
	ContentSelector string    `yaml:"content_selector"`
	UserAgent       string    `yaml:"user_agent"`
	RateLimit       RateLimit `yaml:"rate_limit"`
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
		if t.MaxDepth < 0 {
			t.MaxDepth = 0
		}
		if t.Concurrency <= 0 {
			t.Concurrency = 8
		}
		if t.RateLimit.RequestsPerMinute <= 0 {
			t.RateLimit.RequestsPerMinute = 30
		}
	}

	return &cfg, nil
}

