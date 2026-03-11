package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"sync"
	"time"

	"github.com/PuerkitoBio/goquery"
)

// Task represents a scraping target
type Task struct {
	URL string
}

// Result carries the scraped data or an error
type Result struct {
	URL     string
	Title   string
	Snippet string
	Error   error
}

func main() {
	// List of technical documentations to scrape
	urls := []string{
		"https://go.dev/doc/",
		"https://www.python.org/doc/",
		"https://nextjs.org/docs",
	}

	taskChan := make(chan Task, len(urls))
	resChan := make(chan Result, len(urls))
	var wg sync.WaitGroup

	// Initialize worker pool (concurrency control)
	const workerCount = 3
	for i := 1; i <= workerCount; i++ {
		wg.Add(1)
		go worker(i, taskChan, resChan, &wg)
	}

	// Dispatch tasks to workers
	for _, url := range urls {
		taskChan <- Task{URL: url}
	}
	close(taskChan)

	// Orchestrate shutdown: close resChan when all workers are done
	go func() {
		wg.Wait()
		close(resChan)
	}()

	fmt.Println(">>> Lumina Ingestion Engine Started")
	for res := range resChan {
		if res.Error != nil {
			fmt.Printf("[Error] %s: %v\n", res.URL, res.Error)
		} else {
			fmt.Printf("[Success]\n  URL: %s\n  Title: %s\n  Snippet: %s...\n\n",
				res.URL, res.Title, res.Snippet)
		}
	}
}

// worker processes tasks and sends data to the Python AI service
func worker(id int, tasks <-chan Task, results chan<- Result, wg *sync.WaitGroup) {
	defer wg.Done()
	client := http.Client{Timeout: 10 * time.Second}

	for task := range tasks {
		// 1. Fetch the webpage
		resp, err := client.Get(task.URL)
		if err != nil {
			results <- Result{URL: task.URL, Error: err}
			continue
		}

		doc, err := goquery.NewDocumentFromReader(resp.Body)
		resp.Body.Close() // Close early to free resources
		if err != nil {
			results <- Result{URL: task.URL, Error: err}
			continue
		}

		title := doc.Find("title").Text()
		content := doc.Find("p").First().Text() // Simplification for test

		// 2. Prepare JSON payload for Python service
		// In a real RAG, you'd send more content
		payload := map[string]string{
			"url":     task.URL,
			"title":   title,
			"content": content,
		}
		jsonData, _ := json.Marshal(payload)

		// 3. Send POST request to Python AI Service
		// Ensure Python is running on localhost:8000
		apiURL := "http://localhost:8000/ingest"
		apiResp, err := http.Post(apiURL, "application/json", bytes.NewBuffer(jsonData))

		if err != nil {
			fmt.Printf("Worker [%d] failed to connect to AI Service: %v\n", id, err)
		} else {
			apiResp.Body.Close()
		}

		results <- Result{URL: task.URL, Title: title, Error: nil}
	}
}
