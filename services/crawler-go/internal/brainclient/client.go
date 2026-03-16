package brainclient

import (
	"bytes"
	"encoding/json"
	"fmt"
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

func (c *Client) Ingest(doc Document) error {
	body, err := json.Marshal(doc)
	if err != nil {
		return fmt.Errorf("marshal ingest payload: %w", err)
	}

	req, err := http.NewRequest(http.MethodPost, c.ingestURL, bytes.NewReader(body))
	if err != nil {
		return fmt.Errorf("build ingest request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	// basic retry for transient errors
	var lastErr error
	for attempt := 0; attempt < 3; attempt++ {
		resp, err := c.http.Do(req)
		if err != nil {
			lastErr = err
			time.Sleep(time.Duration(attempt+1) * time.Second)
			continue
		}
		resp.Body.Close()
		if resp.StatusCode >= 200 && resp.StatusCode < 300 {
			return nil
		}
		lastErr = fmt.Errorf("ingest failed with status %d", resp.StatusCode)
		time.Sleep(time.Duration(attempt+1) * time.Second)
	}

	return lastErr
}

