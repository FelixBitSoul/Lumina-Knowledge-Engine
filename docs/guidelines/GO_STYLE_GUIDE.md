# Go Style Guide

This style guide defines coding standards and best practices for Go code in the Lumina Knowledge Engine project, specifically for the Crawler service (`services/crawler-go`).

---

## 📋 Table of Contents

- [Code Formatting](#code-formatting)
- [Naming Conventions](#naming-conventions)
- [Project Structure](#project-structure)
- [Error Handling](#error-handling)
- [Concurrency](#concurrency)
- [Testing](#testing)
- [Documentation](#documentation)
- [Common Patterns](#common-patterns)
- [Anti-patterns to Avoid](#anti-patterns-to-avoid)

---

## 🎨 Code Formatting

### Mandatory Formatting

All Go code **must** be formatted with `gofmt`:

```bash
# Format single file
gofmt -w filename.go

# Format all files in directory
gofmt -w .

# Check formatting without writing
gofmt -l .
```

### Import Organization

Use `goimports` for import management:

```bash
# Install goimports
go install golang.org/x/tools/cmd/goimports@latest

# Format with imports
goimports -w .
```

Imports should be grouped and ordered:

```go
// Standard library imports
import (
    "encoding/json"
    "fmt"
    "net/http"
    "time"
)

// Third-party imports
import (
    "github.com/gocolly/colly/v2"
    "github.com/PuerkitoBio/goquery"
    "gopkg.in/yaml.v3"
)

// Internal/project imports
import (
    "lumina/internal/config"
    "lumina/internal/extract"
)
```

### Line Length

- Soft limit: 100 characters
- Hard limit: 120 characters
- Break long lines at logical points

### Code Organization

```go
// Package comment (always first)
// Package crawler provides web crawling functionality...
package crawler

// Imports
import (
    // ...
)

// Constants
const (
    defaultTimeout = 30 * time.Second
    maxRetries     = 3
)

// Variables (avoid globals when possible)
var (
    defaultUserAgent = "LuminaCrawler/1.0"
)

// Types (interfaces first, then structs)
// Crawler defines the interface for web crawlers.
type Crawler interface {
    Crawl(url string) (*Result, error)
    Stop() error
}

// Config holds crawler configuration.
type Config struct {
    Timeout time.Duration
    MaxDepth int
}

// Constructor functions
// NewCrawler creates a new crawler instance.
func NewCrawler(cfg *Config) (*DefaultCrawler, error) {
    // ...
}

// Methods (group by receiver type)
func (c *DefaultCrawler) Crawl(url string) (*Result, error) {
    // ...
}

// Private helper functions
func normalizeURL(rawURL string) (string, error) {
    // ...
}
```

---

## 🏷 Naming Conventions

### General Rules

- Use **camelCase** for unexported identifiers
- Use **CamelCase** for exported identifiers
- Use **ALL_CAPS** for acronyms (HTTP, URL, ID, API)
- Be descriptive but concise
- Avoid abbreviations unless universally understood

### Package Names

- Short, lowercase, single words
- No underscores, no mixed caps
- Should not be plural (except for standard library patterns)

```go
// Good
package crawler
package config
package brainclient

// Bad
package crawler_go
package Crawler
package crawlers
```

### Variable Names

```go
// Good - descriptive
baseURL := "https://example.com"
requestTimeout := 30 * time.Second
crawlerConfig := &Config{}

// Acceptable - short scope
for i, url := range urls {
    // i and url are clear in this small scope
}

// Bad - unclear
u := "https://example.com"  // What's 'u'?
rt := 30                   // What's 'rt'?
data := getData()          // What kind of data?
```

### Function Names

```go
// Exported functions - describe what they do
func FetchDocument(url string) (*Document, error)
func NormalizeURL(rawURL string) (string, error)
func NewCrawler(config *Config) (*Crawler, error)

// Unexported functions - implementation details
func parseHTML(html []byte) (*Document, error)
func shouldRetry(err error) bool
func logDebug(format string, args ...any)
```

### Interface Names

- Single method interfaces: method name + "er"
- Multi-method interfaces: descriptive noun

```go
// Single method - method name + "er"
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Crawler interface {
    Crawl(url string) (*Result, error)
}

// Multi-method - descriptive noun
type DocumentProcessor interface {
    Process(doc *Document) error
    Validate(doc *Document) error
    Transform(doc *Document) (*Document, error)
}
```

### Struct Names

```go
// Exported structs
type Crawler struct {
    config *Config
    client *http.Client
}

type Document struct {
    URL     string
    Title   string
    Content string
}

// Unexported structs for internal use
type crawlState struct {
    visited map[string]bool
    depth   int
}
```

### Constant Names

```go
// Exported constants
const DefaultTimeout = 30 * time.Second
const MaxRetries = 3

// Unexported constants
const defaultUserAgent = "LuminaCrawler/1.0"
const maxRedirects = 10
```

### Error Variables

```go
// Prefixed with Err
var ErrNotFound = errors.New("resource not found")
var ErrTimeout = errors.New("request timeout")
var ErrInvalidURL = errors.New("invalid URL format")
```

---

## 📁 Project Structure

### Standard Layout

```
services/crawler-go/
├── cmd/
│   └── crawler/
│       └── main.go          # Application entry point
├── internal/
│   ├── crawler/
│   │   └── crawler.go        # Core crawling logic
│   ├── config/
│   │   └── config.go         # Configuration loading
│   ├── brainclient/
│   │   └── client.go         # Brain API client
│   └── extract/
│       └── readability.go    # Content extraction
├── go.mod                    # Module definition
├── go.sum                    # Dependency checksums
├── crawler-config.yaml      # Configuration file
└── README.md                 # Service documentation
```

### Package Guidelines

- **`cmd/`**: Main applications - one subdirectory per application
- **`internal/`**: Private application code - cannot be imported by other projects
- **No `pkg/`**: We don't expose public libraries (use `internal/`)

### File Organization

- One main type or concept per file
- File name should match the primary type (e.g., `crawler.go` for `Crawler` struct)
- `_test.go` suffix for test files
- Keep files under 500 lines when possible

---

## ⚠️ Error Handling

### Error Handling Principles

1. **Explicit error checking**: Always check errors immediately
2. **Early returns**: Handle errors at the top, success at the bottom
3. **Error wrapping**: Add context using `fmt.Errorf` with `%w`
4. **Sentinel errors**: Define package-level error variables

### Error Handling Pattern

```go
// Good - early return, clear flow
func (c *Crawler) Fetch(url string) (*Document, error) {
    resp, err := c.client.Get(url)
    if err != nil {
        return nil, fmt.Errorf("fetching %s: %w", url, err)
    }
    defer resp.Body.Close()
    
    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("unexpected status: %d", resp.StatusCode)
    }
    
    doc, err := parseResponse(resp)
    if err != nil {
        return nil, fmt.Errorf("parsing response from %s: %w", url, err)
    }
    
    return doc, nil
}

// Bad - nested, hard to follow
func (c *Crawler) FetchBad(url string) (*Document, error) {
    resp, err := c.client.Get(url)
    if err == nil {
        defer resp.Body.Close()
        if resp.StatusCode == http.StatusOK {
            doc, err := parseResponse(resp)
            if err == nil {
                return doc, nil
            } else {
                return nil, err
            }
        } else {
            return nil, fmt.Errorf("bad status")
        }
    } else {
        return nil, err
    }
}
```

### Error Wrapping

```go
// Add context when errors cross API boundaries
func LoadConfig(path string) (*Config, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("read config %q: %w", path, err)
    }
    
    var cfg Config
    if err := yaml.Unmarshal(data, &cfg); err != nil {
        return nil, fmt.Errorf("parse config %q: %w", path, err)
    }
    
    return &cfg, nil
}

// Check specific error types
if errors.Is(err, ErrNotFound) {
    // Handle not found
}

// Check error types (Go 1.13+)
var netErr net.Error
if errors.As(err, &netErr) && netErr.Timeout() {
    // Handle timeout
}
```

### Panic Guidelines

- **Avoid panic in production code**
- Only panic for unrecoverable programmer errors
- Use `log.Fatal` for initialization errors

```go
// Acceptable - programmer error
if len(slice) == 0 {
    panic("unreachable: slice must not be empty")
}

// Never do this - recoverable error
if err != nil {
    panic(err)
}
```

---

## 🔄 Concurrency

### Goroutines

- Keep goroutine lifecycles clear and bounded
- Always handle goroutine errors
- Use `sync.WaitGroup` for coordination

```go
// Good - clear lifecycle, error handling
func (c *Crawler) CrawlMultiple(urls []string) ([]*Document, error) {
    var wg sync.WaitGroup
    results := make(chan *Document, len(urls))
    errors := make(chan error, len(urls))
    
    for _, url := range urls {
        wg.Add(1)
        go func(u string) {
            defer wg.Done()
            
            doc, err := c.Crawl(u)
            if err != nil {
                errors <- err
                return
            }
            results <- doc
        }(url)
    }
    
    // Close channels when done
    go func() {
        wg.Wait()
        close(results)
        close(errors)
    }()
    
    // Collect results
    // ...
}
```

### Channels

- Close channels from the sender side
- Use buffered channels to prevent blocking
- Document channel ownership

```go
// Producer owns the channel, closes it when done
func produce() <-chan int {
    ch := make(chan int, 10) // Buffered
    go func() {
        defer close(ch)
        for i := 0; i < 100; i++ {
            ch <- i
        }
    }()
    return ch
}

// Consumer reads until channel closed
func consume(ch <-chan int) {
    for v := range ch {
        // Process v
    }
}
```

### Context Usage

- Pass `context.Context` as first parameter
- Use context for cancellation and timeouts
- Don't store context in structs

```go
// Good
func FetchWithContext(ctx context.Context, url string) (*Response, error) {
    req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
    if err != nil {
        return nil, err
    }
    return http.DefaultClient.Do(req)
}

// Bad - storing context in struct
type BadClient struct {
    ctx context.Context  // Don't do this
}
```

---

## 🧪 Testing

### Test Organization

```go
// crawler_test.go
package crawler

import (
    "testing"
)

func TestCrawler_Crawl(t *testing.T) {
    // Test cases
}

func TestCrawler_Crawl_Error(t *testing.T) {
    // Error case tests
}

// Table-driven tests
func TestNormalizeURL(t *testing.T) {
    tests := []struct {
        name     string
        input    string
        expected string
        wantErr  bool
    }{
        {
            name:     "simple URL",
            input:    "https://example.com",
            expected: "https://example.com",
            wantErr:  false,
        },
        {
            name:     "URL with fragment",
            input:    "https://example.com/page#section",
            expected: "https://example.com/page",
            wantErr:  false,
        },
        {
            name:     "invalid URL",
            input:    "://invalid",
            expected: "",
            wantErr:  true,
        },
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := NormalizeURL(tt.input)
            if (err != nil) != tt.wantErr {
                t.Errorf("NormalizeURL() error = %v, wantErr %v", err, tt.wantErr)
                return
            }
            if got != tt.expected {
                t.Errorf("NormalizeURL() = %v, want %v", got, tt.expected)
            }
        })
    }
}
```

### Test Naming

```go
// Test functions: Test + Type + Method
func TestCrawler_Crawl(t *testing.T)
func TestConfig_Load(t *testing.T)
func TestDocument_Extract(t *testing.T)

// Subtests: descriptive names
func TestCrawler_Crawl(t *testing.T) {
    t.Run("success", func(t *testing.T) { })
    t.Run("invalid_url", func(t *testing.T) { })
    t.Run("timeout", func(t *testing.T) { })
}
```

### Mocking and Interfaces

```go
// Define interfaces for dependencies
type HTTPClient interface {
    Do(req *http.Request) (*http.Response, error)
}

// Production implementation
type RealHTTPClient struct {
    client *http.Client
}

// Mock for testing
type MockHTTPClient struct {
    responses map[string]*http.Response
    errors    map[string]error
}

func (m *MockHTTPClient) Do(req *http.Request) (*http.Response, error) {
    if err, ok := m.errors[req.URL.String()]; ok {
        return nil, err
    }
    return m.responses[req.URL.String()], nil
}
```

---

## 📝 Documentation

### Package Documentation

```go
// Package crawler provides web crawling functionality for the Lumina
// Knowledge Engine. It supports concurrent crawling, rate limiting,
// and content extraction.
//
// Basic usage:
//
//	cfg := &crawler.Config{
//	    Seeds: []string{"https://example.com"},
//	    MaxDepth: 2,
//	}
//	c, err := crawler.New(cfg)
//	if err != nil {
//	    log.Fatal(err)
//	}
//	results, err := c.Run()
package crawler
```

### Function Documentation

```go
// FetchDocument retrieves a document from the given URL and parses
// its content. It respects the crawler's rate limiting and timeout
// settings.
//
// If the URL is invalid or the request fails, an error is returned.
// HTTP 4xx and 5xx status codes result in an error.
//
// The returned Document must not be modified after being passed to
// downstream processors.
func (c *Crawler) FetchDocument(url string) (*Document, error) {
    // ...
}
```

### Type Documentation

```go
// Config holds configuration parameters for the Crawler.
// All fields have sensible defaults if left zero-valued.
type Config struct {
    // Seeds are the initial URLs to start crawling from.
    // At least one seed is required.
    Seeds []string
    
    // MaxDepth limits how many links deep to crawl from seeds.
    // 1 means only seeds, 2 means seeds + their links, etc.
    // Default is 1.
    MaxDepth int
    
    // Concurrency limits the number of simultaneous requests.
    // Default is 8.
    Concurrency int
}
```

---

## 🎯 Common Patterns

### Configuration Pattern

```go
type Config struct {
    Timeout    time.Duration
    MaxRetries int
}

func DefaultConfig() *Config {
    return &Config{
        Timeout:    30 * time.Second,
        MaxRetries: 3,
    }
}

func New(cfg *Config) (*Service, error) {
    if cfg == nil {
        cfg = DefaultConfig()
    }
    
    // Validation
    if cfg.Timeout <= 0 {
        return nil, errors.New("timeout must be positive")
    }
    
    return &Service{config: cfg}, nil
}
```

### Functional Options Pattern

```go
type Crawler struct {
    timeout time.Duration
    logger  *log.Logger
}

type Option func(*Crawler)

func WithTimeout(d time.Duration) Option {
    return func(c *Crawler) {
        c.timeout = d
    }
}

func WithLogger(l *log.Logger) Option {
    return func(c *Crawler) {
        c.logger = l
    }
}

func NewCrawler(opts ...Option) *Crawler {
    c := &Crawler{
        timeout: 30 * time.Second,
        logger:  log.Default(),
    }
    for _, opt := range opts {
        opt(c)
    }
    return c
}

// Usage
crawler := NewCrawler(
    WithTimeout(60 * time.Second),
    WithLogger(customLogger),
)
```

### HTTP Client Resource Management

Ensure HTTP response bodies are **fully consumed** to enable TCP connection reuse (Keep-Alive):

```go
// Pattern 1: Read body content (automatically consumed)
func (c *Client) Request(url string) ([]byte, error) {
    resp, err := c.http.Get(url)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    
    // io.ReadAll consumes entire body, enabling connection reuse
    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return nil, err
    }
    return body, nil
}

// Pattern 2: Discard unread body (when you don't need content)
func (c *Client) Ingest(doc Document) error {
    resp, err := c.http.Post(c.ingestURL, "application/json", body)
    if err != nil {
        return err
    }
    defer func() {
        // Explicitly drain unread body before close to enable connection reuse
        io.Copy(io.Discard, resp.Body)
        resp.Body.Close()
    }()
    
    if resp.StatusCode != http.StatusOK {
        return fmt.Errorf("unexpected status: %d", resp.StatusCode)
    }
    return nil
}

// Pattern 3: Immediate cleanup in retry loops
func (c *Client) IngestWithRetry(doc Document) error {
    for attempt := 0; attempt < 3; attempt++ {
        resp, err := c.http.Do(req)
        if err != nil {
            continue
        }
        
        // Consume and close immediately before next iteration
        func() {
            defer resp.Body.Close()
            io.Copy(io.Discard, resp.Body)  // Drain if not reading
        }()
        
        if resp.StatusCode == http.StatusOK {
            return nil
        }
    }
    return errors.New("failed after retries")
}
```

**Key Points:**
1. **Body must be fully consumed**: The HTTP Transport can only reuse a connection if the entire response body has been read. Whether you read it for processing or discard it, full consumption is required.
2. **Close after consumption**: Always call `resp.Body.Close()` to release resources, but do so after the body is fully consumed.
3. **Use `io.Copy(io.Discard, resp.Body)` only when needed**: If you've already read the body with `io.ReadAll`, `json.Decoder`, etc., the body is already consumed—no need to drain again. Use discard only when you won't read the body content.
4. **Retry loop handling**: In loops, use anonymous functions with `defer` for immediate cleanup rather than deferring to function exit.

**Why this matters:**
- TCP connection reuse significantly reduces latency and overhead in high-concurrency scenarios (no repeated handshakes)
- Proper consumption prevents connection pool exhaustion in sustained high-throughput workloads
- In long-running crawlers, this optimization maintains steady performance without resource degradation

**Note**: While `defer resp.Body.Close()` alone prevents goroutine leaks, **full body consumption** is what enables TCP connection pooling. Both are needed for production-grade HTTP client code.

---

### Builder Pattern

```go
type RequestBuilder struct {
    url     string
    headers map[string]string
    timeout time.Duration
}

func NewRequest(url string) *RequestBuilder {
    return &RequestBuilder{
        url:     url,
        headers: make(map[string]string),
        timeout: 30 * time.Second,
    }
}

func (b *RequestBuilder) WithHeader(key, value string) *RequestBuilder {
    b.headers[key] = value
    return b
}

func (b *RequestBuilder) WithTimeout(d time.Duration) *RequestBuilder {
    b.timeout = d
    return b
}

func (b *RequestBuilder) Build() (*http.Request, error) {
    req, err := http.NewRequest("GET", b.url, nil)
    if err != nil {
        return nil, err
    }
    for k, v := range b.headers {
        req.Header.Set(k, v)
    }
    return req, nil
}
```

---

## 🚫 Anti-patterns to Avoid

### 1. Ignoring Errors

```go
// Bad
file, _ := os.Open("crawler-config.yaml")  // Ignoring error!

// Good
file, err := os.Open("crawler-config.yaml")
if err != nil {
    return fmt.Errorf("open config: %w", err)
}
defer file.Close()
```

### 2. Unnecessary Interface

```go
// Bad - single implementation interface
type DocumentProcessor interface {
    Process(doc *Document) error
}

type DefaultDocumentProcessor struct{}

// Good - concrete type until needed
 type DocumentProcessor struct{}

// Extract interface when you have multiple implementations
```

### 3. Package Name Stuttering

```go
// Bad
package crawler
type CrawlerConfig struct{}  // Stutters: crawler.CrawlerConfig

// Good
package crawler
type Config struct{}  // Clear: crawler.Config
```

### 4. Goroutine Leaks

```go
// Bad - leaked goroutine
func bad() {
    ch := make(chan int)
    go func() {
        ch <- 42  // May block forever
    }()
    // If we return early, goroutine leaks
}

// Good - bounded lifecycle
func good() {
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()
    
    ch := make(chan int, 1)  // Buffered to prevent blocking
    go func() {
        select {
        case ch <- 42:
        case <-ctx.Done():
        }
    }()
    
    select {
    case v := <-ch:
        _ = v
    case <-ctx.Done():
    }
}
```

### 5. Nil Pointer Dereferences

```go
// Bad
func (c *Crawler) Crawl(url string) error {
    return c.client.Get(url)  // c may be nil!
}

// Good - check or ensure initialization
func (c *Crawler) Crawl(url string) error {
    if c == nil {
        return errors.New("crawler not initialized")
    }
    if c.client == nil {
        return errors.New("HTTP client not initialized")
    }
    return c.client.Get(url)
}
```

---

## 📚 Additional Resources

- [Effective Go](https://golang.org/doc/effective_go.html) - Official best practices
- [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments) - Common review feedback
- [Uber Go Style Guide](https://github.com/uber-go/guide/blob/master/style.md) - Extended conventions
- [Standard Go Project Layout](https://github.com/golang-standards/project-layout) - Project structure

---

## 🛠 Tools Configuration

### golangci-lint Config (`.golangci.yml`)

```yaml
run:
  timeout: 5m
  issues-exit-code: 1
  tests: true

linters:
  enable:
    - gofmt
    - goimports
    - golint
    - govet
    - errcheck
    - staticcheck
    - unused
    - gosimple
    - structcheck
    - varcheck
    - ineffassign
    - deadcode
    - typecheck
    - misspell
    - gocyclo
    - gocognit
    - dupl

linters-settings:
  gocyclo:
    min-complexity: 15
  dupl:
    threshold: 100

issues:
  exclude-use-default: false
```

---

<p align="center">
  Write idiomatic Go. Be concise, be clear. 🐹
</p>
