package brainclient

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"
)

type Document struct {
	URL     string `json:"url"`
	Title   string `json:"title"`
	Content string `json:"content"`
}

type Client struct {
	ingestURL string
	http      *http.Client
}

func New() *Client {
	ingestURL := os.Getenv("BRAIN_INGEST_URL")
	if ingestURL == "" {
		ingestURL = "http://localhost:8000/ingest"
	}
	return &Client{
		ingestURL: ingestURL,
		http: &http.Client{
			Timeout: 20 * time.Second,
		},
	}
}

func (c *Client) Ingest(doc Document, collection string) error {
	body, err := json.Marshal(doc)
	if err != nil {
		return fmt.Errorf("marshal ingest payload: %w", err)
	}

	// basic retry for transient errors
	var lastErr error
	for attempt := 0; attempt < 3; attempt++ {
		// Build a fresh request each attempt (do not reuse bodies/readers).
		requestURL := c.ingestURL
		if collection != "" {
			requestURL += "?collection=" + collection
		}
		req, err := http.NewRequest(http.MethodPost, requestURL, bytes.NewReader(body))
		if err != nil {
			return fmt.Errorf("build ingest request: %w", err)
		}
		req.Header.Set("Content-Type", "application/json")

		resp, err := c.http.Do(req)
		if err != nil {
			lastErr = err
			time.Sleep(time.Duration(attempt+1) * time.Second)
			continue
		}

		// Use an anonymous function to ensure cleanup happens immediately
		// after processing, rather than waiting for the entire Ingest function to return.
		func() {
			// defer ensures the body is closed even if a panic or early return occurs
			defer resp.Body.Close()

			// Drain the response body to allow the default HTTP Transport to reuse
			// the underlying TCP connection (Keep-Alive).
			// Failing to drain prevents connection pooling and leads to resource exhaustion.
			_, _ = io.Copy(io.Discard, resp.Body)
		}()

		if resp.StatusCode >= 200 && resp.StatusCode < 300 {
			return nil
		}
		lastErr = fmt.Errorf("ingest failed with status %d", resp.StatusCode)
		time.Sleep(time.Duration(attempt+1) * time.Second)
	}

	return lastErr
}
