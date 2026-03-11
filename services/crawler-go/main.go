package main

import (
	"fmt"
	"net/http"
	"sync"
	"time"

	"github.com/PuerkitoBio/goquery" // 新增依赖
)

type Task struct {
	URL string
}

type Result struct {
	URL     string
	Title   string
	Snippet string // 新增：正文片段
	Error   error
}

func main() {
	urls := []string{
		"https://go.dev/doc/",
		"https://www.python.org/doc/",
		"https://nextjs.org/docs",
	}

	taskChan := make(chan Task, len(urls))
	resChan := make(chan Result, len(urls))
	var wg sync.WaitGroup

	for i := 1; i <= 3; i++ {
		wg.Add(1)
		go worker(i, taskChan, resChan, &wg)
	}

	for _, url := range urls {
		taskChan <- Task{URL: url}
	}
	close(taskChan)

	go func() {
		wg.Wait()
		close(resChan)
	}()

	fmt.Println("--- Lumina Ingestion Started ---")
	for res := range resChan {
		if res.Error != nil {
			fmt.Printf("[Error] %s: %v\n", res.URL, res.Error)
		} else {
			fmt.Printf("[Success]\n  URL: %s\n  Title: %s\n  Snippet: %s...\n\n",
				res.URL, res.Title, res.Snippet)
		}
	}
}

func worker(id int, tasks <-chan Task, results chan<- Result, wg *sync.WaitGroup) {
	defer wg.Done()
	client := http.Client{Timeout: 10 * time.Second}

	for task := range tasks {
		resp, err := client.Get(task.URL)
		if err != nil {
			results <- Result{URL: task.URL, Error: err}
			continue
		}
		defer resp.Body.Close()

		if resp.StatusCode != 200 {
			results <- Result{URL: task.URL, Error: fmt.Errorf("status code %d", resp.StatusCode)}
			continue
		}

		// 使用 goquery 解析 HTML
		doc, err := goquery.NewDocumentFromReader(resp.Body)
		if err != nil {
			results <- Result{URL: task.URL, Error: err}
			continue
		}

		// 提取 Title
		title := doc.Find("title").Text()

		// 提取第一段正文作为摘要 (Snippet)
		snippet := doc.Find("p").First().Text()
		if len(snippet) > 100 {
			snippet = snippet[:100]
		}

		results <- Result{
			URL:     task.URL,
			Title:   title,
			Snippet: snippet,
			Error:   nil,
		}
	}
}
