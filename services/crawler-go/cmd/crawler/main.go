package main

import (
	"fmt"

	"github.com/FelixBitSoul/lumina/crawler/internal/brainclient"
	"github.com/FelixBitSoul/lumina/crawler/internal/config"
	"github.com/FelixBitSoul/lumina/crawler/internal/crawler"
)

func main() {
	cfg, err := config.Load("config.yaml")
	if err != nil {
		fmt.Printf("[Crawler] Failed to load config: %v\n", err)
		return
	}
	if len(cfg.Tasks) == 0 {
		fmt.Println("[Crawler] No tasks configured.")
		return
	}

	brain := brainclient.New()

	logger := func(format string, args ...any) {
		fmt.Printf(format+"\n", args...)
	}

	fmt.Println(">>> Lumina Colly Crawler Started")

	for _, t := range cfg.Tasks {
		if err := crawler.ValidateTask(t); err != nil {
			logger("[Task:%s] [ConfigError] %v", t.Name, err)
			continue
		}
		logger("[Task:%s] Starting. Seeds=%d, MaxDepth=%d, Concurrency=%d, RPM=%d, Timeout=%ds, RetryMax=%d",
			t.Name,
			len(t.Seeds),
			t.MaxDepth,
			t.Concurrency,
			t.RateLimit.RequestsPerMinute,
			t.RequestTimeoutSeconds,
			t.Retry.MaxAttempts,
		)

		c := crawler.New(t, brain, logger)
		if err := c.Run(); err != nil {
			logger("[Task:%s] [RunError] %v", t.Name, err)
		}
		logger("[Task:%s] Done.", t.Name)
	}
}

