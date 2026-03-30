## crawler-go

This service crawls documentation websites and ingests cleaned text into the Python Brain API (`/ingest`).

### How it works

- **Crawler**: Go + Colly (async, rate limiting, depth-limited traversal, automatic retries)
- **Extraction**: `go-readability` for main article text with optional CSS selector override using goquery
- **Ingestion**: HTTP POST to Brain API `/ingest` with automatic collection management
- **Features**: URL normalization, duplicate prevention, configurable concurrency and rate limiting

### Run

From the repo root:

```bash
cd services/crawler-go
go run ./cmd/crawler
```

Environment variables:

- **`CRAWLER_CONFIG`**: Path to the YAML config file (defaults to `crawler-config.yaml` in this folder)
- **`BRAIN_INGEST_URL`**: Brain API ingest endpoint (defaults to `http://localhost:8000/ingest`)

### Configuration (`crawler-config.yaml`)

Top-level:

- **`tasks`**: list of crawl tasks

Task fields:

- **`name`**: task name (for logs)
- **`seeds`**: list of seed URLs
- **`max_depth`**: depth relative to seeds
  - `1` = only seeds
  - `2` = seeds + links on seed pages
- **`allowed_domains`**: domain allow-list (enforced by Colly)
- **`concurrency`**: max concurrent requests for this task
- **`rate_limit.requests_per_minute`**: approximate request rate cap
- **`request_timeout_seconds`**: per-request timeout
- **`user_agent`**: optional user agent string
- **`content_selector`**: optional CSS selector to override extracted text
- **`retry`**:
  - **`max_attempts`**: total attempts including the first request (default: 3)
  - **`backoff_seconds`**: linear backoff multiplier (attempt * backoff)
  - **`retry_on_status`**: list of HTTP status codes to retry

Example:

```yaml
tasks:
  - name: core-docs
    seeds:
      - https://go.dev/doc/
    max_depth: 1
    allowed_domains: [go.dev]
    concurrency: 8
    rate_limit:
      requests_per_minute: 60
    request_timeout_seconds: 15
    retry:
      max_attempts: 3
      backoff_seconds: 2
      retry_on_status: [429, 500, 502, 503, 504]
    user_agent: LuminaCrawler/0.1
    content_selector: article
```

### Tuning tips

- **If it feels slow**: increase `concurrency` first, then `requests_per_minute` (careful with 429s).
- **If you get blocked**: reduce RPM, use a realistic `user_agent`, consider smaller `max_depth`.
- **If extraction is poor**: set `content_selector` to a site-specific container (`main`, `article`, etc.).

### Troubleshooting

- **Many 429 responses**: lower `requests_per_minute`, increase backoff, reduce depth.
- **Timeouts**: increase `request_timeout_seconds` for slow sites.
- **Duplicates**: this crawler normalizes URLs (drops fragments, trims trailing slashes); Colly also prevents revisiting the same URL during a run.

