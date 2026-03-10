package main

import (
	"fmt"
	"net/http"
	"sync"
	"time"
)

// Task 代表一个采集任务
type Task struct {
	URL string
}

// Result 代表采集结果
type Result struct {
	URL   string
	Title string
	Error error
}

func main() {
	urls := []string{
		"https://go.dev",
		"https://python.org",
		"https://nextjs.org",
	}

	taskChan := make(chan Task, len(urls))
	resChan := make(chan Result, len(urls))
	var wg sync.WaitGroup

	// 1. 启动 Worker 线程池 (限制并发数为 3)
	for i := 1; i <= 3; i++ {
		wg.Add(1)
		go worker(i, taskChan, resChan, &wg)
	}

	// 2. 分发任务
	for _, url := range urls {
		taskChan <- Task{URL: url}
	}
	close(taskChan) // 关闭通道，通知 worker 任务分发完毕

	// 3. 等待所有 worker 完成并关闭结果通道
	go func() {
		wg.Wait()
		close(resChan)
	}()

	// 4. 打印结果
	fmt.Println("--- 采集任务开始 ---")
	for res := range resChan {
		if res.Error != nil {
			fmt.Printf("[失败] %s: %v\n", res.URL, res.Error)
		} else {
			fmt.Printf("[成功] %s | 结果: %s\n", res.URL, res.Title)
		}
	}
}

// worker 模拟爬虫抓取过程
func worker(id int, tasks <-chan Task, results chan<- Result, wg *sync.WaitGroup) {
	defer wg.Done()
	for task := range tasks {
		fmt.Printf("Worker [%d] 正在抓取: %s\n", id, task.URL)

		// 模拟网络请求
		client := http.Client{Timeout: 5 * time.Second}
		resp, err := client.Get(task.URL)

		title := "Unknown"
		if err == nil {
			title = resp.Status // 这里暂时拿状态码演示，后续会引入 HTML 解析
			resp.Body.Close()
		}

		results <- Result{
			URL:   task.URL,
			Title: title,
			Error: err,
		}
	}
}
