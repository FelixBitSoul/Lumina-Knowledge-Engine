# Crawler Configuration Documentation

This document provides comprehensive documentation for configuring the Go Crawler Service in the Lumina Knowledge Engine.

## 📋 Configuration Overview

The Crawler Service uses YAML-based configuration files with environment variable overrides, allowing flexible management of crawling tasks and behavior.

### Configuration File Location

- **Default Path**: `services/crawler-go/crawler-config.yaml`
- **Environment Override**: `CRAWLER_CONFIG` environment variable
- **Format**: YAML with strict schema validation

## 🏗 Configuration Structure

```yaml
tasks:
  - name: string              # Task identifier (required)
    seeds:                   # Starting URLs (required)
      - string
    max_depth: number         # Crawling depth (default: 1)
    allowed_domains:          # Domain whitelist (required)
      - string
    concurrency: number       # Concurrent requests (default: 8)
    rate_limit:               # Rate limiting (required)
      requests_per_minute: number
    request_timeout_seconds: number  # Request timeout (default: 15)
    content_selector: string  # CSS selector override (optional)
    user_agent: string       # Custom user agent (optional)
    retry:                    # Retry configuration (optional)
      max_attempts: number   # Total attempts (default: 3)
      backoff_seconds: number # Backoff multiplier (default: 2)
      retry_on_status:        # HTTP codes to retry (default: [429,500,502,503,504])
        - number
```

## 📚 Field Specifications

### Task Configuration

#### `name` (Required)
**Type**: String  
**Description**: Unique identifier for the crawling task  
**Constraints**: 1-100 characters, alphanumeric + hyphens/underscores  
**Default**: Auto-generated if not provided (`task-N`)

**Example**:
```yaml
name: "technical-documentation"
```

#### `seeds` (Required)
**Type**: Array of Strings  
**Description**: Starting URLs for crawling  
**Constraints**: Valid HTTP/HTTPS URLs  
**Validation**: URL format and accessibility checked

**Example**:
```yaml
seeds:
  - "https://docs.docker.com/get-started/"
  - "https://docs.docker.com/engine/"
  - "https://docs.docker.com/compose/"
```

#### `max_depth` (Optional)
**Type**: Integer  
**Description**: Maximum crawling depth relative to seeds  
**Range**: 1-10  
**Default**: 1 (seeds only)  
**Behavior**:
- `1`: Only seed URLs
- `2`: Seeds + links on seed pages
- `3`: Seeds + links + links on those pages

**Example**:
```yaml
max_depth: 2  # Crawl seed pages and their direct links
```

#### `allowed_domains` (Required)
**Type**: Array of Strings  
**Description**: Domain whitelist for crawling  
**Validation**: Matched against URL hostname  
**Behavior**: Only URLs from these domains are processed

**Example**:
```yaml
allowed_domains:
  - "docs.docker.com"
  - "docker.com"
```

#### `concurrency` (Optional)
**Type**: Integer  
**Description**: Maximum concurrent requests for this task  
**Range**: 1-50  
**Default**: 8  
**Impact**: Higher values increase speed but may trigger rate limits

**Example**:
```yaml
concurrency: 16  # High concurrency for fast crawling
```

#### `request_timeout_seconds` (Optional)
**Type**: Integer  
**Description**: Per-request timeout in seconds  
**Range**: 5-300  
**Default**: 15  
**Behavior**: Requests failing to complete within timeout are retried

**Example**:
```yaml
request_timeout_seconds: 30  # Longer timeout for slow sites
```

#### `content_selector` (Optional)
**Type**: String (CSS Selector)  
**Description**: CSS selector to override default content extraction  
**Default**: None (use go-readability algorithm)  
**Usage**: Site-specific content extraction customization

**Example**:
```yaml
content_selector: "article.main-content"  # Custom selector
content_selector: "main.documentation"   # Another example
```

#### `user_agent` (Optional)
**Type**: String  
**Description**: Custom User-Agent header for requests  
**Default**: `Colly/{version}`  
**Recommendation**: Use descriptive user agent for identification

**Example**:
```yaml
user_agent: "LuminaCrawler/0.1 (+https://lumina.example.com/bot-info)"
```

### Rate Limiting Configuration

#### `rate_limit.requests_per_minute` (Required)
**Type**: Integer  
**Description**: Maximum requests per minute  
**Range**: 1-1000  
**Default**: 30 (if not specified)  
**Behavior**: Enforced via delay between requests

**Example**:
```yaml
rate_limit:
  requests_per_minute: 60  # One request per second
```

### Retry Configuration

#### `retry.max_attempts` (Optional)
**Type**: Integer  
**Description**: Total attempts including first request  
**Range**: 1-10  
**Default**: 3  
**Behavior**: `3` means initial attempt + 2 retries

**Example**:
```yaml
retry:
  max_attempts: 5  # More retries for unreliable sites
```

#### `retry.backoff_seconds` (Optional)
**Type**: Integer  
**Description**: Linear backoff multiplier  
**Range**: 0-60  
**Default**: 2  
**Calculation**: `delay = attempt_index * backoff_seconds`

**Example**:
```yaml
retry:
  backoff_seconds: 5  # Longer delays between retries
```

#### `retry.retry_on_status` (Optional)
**Type**: Array of Integers  
**Description**: HTTP status codes that trigger retry  
**Default**: `[429, 500, 502, 503, 504]`  
**Behavior**: Only these HTTP codes will be retried

**Example**:
```yaml
retry:
  retry_on_status: [429, 500, 502, 503, 504, 408]  # Include timeouts
```

## 🌰 Complete Examples

### Example 1: Basic Documentation Crawling

```yaml
tasks:
  - name: "docker-docs"
    seeds:
      - "https://docs.docker.com/get-started/"
      - "https://docs.docker.com/engine/"
    max_depth: 1
    allowed_domains:
      - "docs.docker.com"
    concurrency: 8
    rate_limit:
      requests_per_minute: 60
    request_timeout_seconds: 15
    user_agent: "LuminaCrawler/0.1 (+https://lumina.example.com/bot-info)"
    retry:
      max_attempts: 3
      backoff_seconds: 2
      retry_on_status: [429, 500, 502, 503, 504]
```

### Example 2: High-Performance Crawling

```yaml
tasks:
  - name: "fast-crawl"
    seeds:
      - "https://react.dev/learn"
      - "https://react.dev/reference"
    max_depth: 2
    allowed_domains:
      - "react.dev"
    concurrency: 16
    rate_limit:
      requests_per_minute: 120
    request_timeout_seconds: 10
    content_selector: "main"
    user_agent: "LuminaCrawler/0.1 (High-Performance)"
    retry:
      max_attempts: 2
      backoff_seconds: 1
      retry_on_status: [429, 500]
```

### Example 3: Gentle Crawling with Custom Extraction

```yaml
tasks:
  - name: "gentle-crawl"
    seeds:
      - "https://www.python.org/doc/"
      - "https://docs.python.org/3/"
    max_depth: 2  # Seeds and their direct links
    allowed_domains:
      - "python.org"
      - "docs.python.org"
    concurrency: 4
    rate_limit:
      requests_per_minute: 30
    request_timeout_seconds: 30
    content_selector: "div.document"
    user_agent: "LuminaCrawler/0.1 (Gentle Mode)"
    retry:
      max_attempts: 5
      backoff_seconds: 3
      retry_on_status: [429, 500, 502, 503, 504, 408]
```

### Example 4: Multi-Task Configuration

```yaml
tasks:
  # Task 1: Docker Documentation
  - name: "docker-docs"
    seeds:
      - "https://docs.docker.com/get-started/"
    max_depth: 1
    allowed_domains: ["docs.docker.com"]
    concurrency: 8
    rate_limit: {requests_per_minute: 60}
    user_agent: "LuminaCrawler/0.1"

  # Task 2: React Documentation
  - name: "react-docs"
    seeds:
      - "https://react.dev/learn"
    max_depth: 1
    allowed_domains: ["react.dev"]
    concurrency: 6
    rate_limit: {requests_per_minute: 45}
    content_selector: "main"
    user_agent: "LuminaCrawler/0.1"

  # Task 3: Python Documentation
  - name: "python-docs"
    seeds:
      - "https://docs.python.org/3/tutorial/"
    max_depth: 1
    allowed_domains: ["docs.python.org"]
    concurrency: 4
    rate_limit: {requests_per_minute: 30}
    user_agent: "LuminaCrawler/0.1"
```

## 🔧 Environment Variables

### Service Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CRAWLER_CONFIG` | `crawler-config.yaml` | Path to configuration file |
| `BRAIN_INGEST_URL` | `http://localhost:8000/ingest` | Brain API ingest endpoint |
| `LOG_LEVEL` | `info` | Logging level (debug, info, warn, error) |

### Example Environment Setup

```bash
# Development
export CRAWLER_CONFIG="config-dev.yaml"
export BRAIN_INGEST_URL="http://localhost:8000/ingest"
export LOG_LEVEL="debug"

# Production
export CRAWLER_CONFIG="/etc/lumina/crawler-config.yaml"
export BRAIN_INGEST_URL="http://brain-api:8000/ingest"
export LOG_LEVEL="info"
```

## ✅ Configuration Validation

### Built-in Validation

The crawler performs automatic validation and normalization:

```go
// Validation rules applied automatically
if t.Name == "" {
    t.Name = fmt.Sprintf("task-%d", i+1)
}
if t.MaxDepth < 0 {
    t.MaxDepth = 0
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
```

### Validation Errors

Common validation errors and their meanings:

| Error | Description | Fix |
|-------|-------------|-----|
| `no seeds configured` | Task has no seed URLs | Add at least one seed URL |
| `invalid seed URL` | Seed URL format is invalid | Use valid HTTP/HTTPS URL |
| `no allowed domains` | No domain whitelist specified | Add allowed domains |
| `invalid domain` | Domain format is invalid | Use valid domain names |

## 🚀 Running the Crawler

### Basic Usage

```bash
cd services/crawler-go
go run ./cmd/crawler
```

### With Custom Config

```bash
CRAWLER_CONFIG=config-production.yaml go run ./cmd/crawler
```

### Docker Usage

```bash
docker run --rm \
  -v $(pwd)/crawler-config.yaml:/app/config/crawler-config.yaml \
  -e BRAIN_INGEST_URL=http://brain-api:8000/ingest \
  lumina-crawler:latest
```

## 📊 Performance Tuning

### Concurrency vs Rate Limiting

```yaml
# High-speed crawling (may trigger anti-bot measures)
concurrency: 16
rate_limit:
  requests_per_minute: 120

# Gentle crawling (recommended for production)
concurrency: 4
rate_limit:
  requests_per_minute: 30
```

### Timeout Configuration

```yaml
# Fast sites
request_timeout_seconds: 10

# Slow sites or high-latency networks
request_timeout_seconds: 30
```

### Retry Strategy

```yaml
# Standard retry (most reliable)
retry:
  max_attempts: 3
  backoff_seconds: 2

# Aggressive retry (for unreliable sites)
retry:
  max_attempts: 5
  backoff_seconds: 3

# Minimal retry (for fast, reliable sites)
retry:
  max_attempts: 2
  backoff_seconds: 1
```

## 🛡️ Best Practices

### 1. Respectful Crawling

```yaml
# Recommended for production
concurrency: 4
rate_limit:
  requests_per_minute: 30
user_agent: "LuminaCrawler/0.1 (+https://your-site.com/bot-info)"
```

### 2. Error Handling

```yaml
# Robust retry configuration
retry:
  max_attempts: 5
  backoff_seconds: 3
  retry_on_status: [429, 500, 502, 503, 504, 408, 404]
```

### 3. Content Extraction

```yaml
# Use custom selectors for better content extraction
content_selector: "article.main"  # Common pattern
content_selector: "main.content"  # Alternative pattern
content_selector: ".documentation" # Class-based
```

### 4. Domain Management

```yaml
# Be specific with allowed domains
allowed_domains:
  - "docs.example.com"    # Specific subdomain
  - "api.example.com"     # API documentation
  # Avoid overly broad patterns like "example.com"
```

## 🔍 Troubleshooting

### Common Issues

#### 1. High Error Rates
**Symptoms**: Many 429/500 responses  
**Solution**: Reduce `requests_per_minute` and `concurrency`

```yaml
# Before (causing errors)
concurrency: 16
rate_limit: {requests_per_minute: 120}

# After (fixed)
concurrency: 4
rate_limit: {requests_per_minute: 30}
```

#### 2. Slow Processing
**Symptoms**: Low throughput despite high concurrency  
**Solution**: Increase `request_timeout_seconds` or check network connectivity

#### 3. Poor Content Extraction
**Symptoms**: Empty or irrelevant content  
**Solution**: Add `content_selector` for site-specific extraction

```yaml
content_selector: "article.documentation"
```

#### 4. Memory Issues
**Symptoms**: Out of memory errors  
**Solution**: Reduce `concurrency` and increase `request_timeout_seconds`

### Debug Configuration

```yaml
# Debug mode with verbose logging
tasks:
  - name: "debug-task"
    seeds: ["https://example.com"]
    max_depth: 1
    allowed_domains: ["example.com"]
    concurrency: 1  # Single thread for debugging
    rate_limit: {requests_per_minute: 10}  # Very slow
    request_timeout_seconds: 30
```

---

*For more information about crawler behavior and implementation, see the [Architecture Documentation](../architecture/component-details.md#crawler-service-go).*
