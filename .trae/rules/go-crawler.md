# Go & Crawler Rules

## 错误处理
- 必须显式处理所有的 `error`。严禁使用 `_` 忽略可能引发崩溃的错误。
- 错误信息必须包含上下文，优先使用 `fmt.Errorf("failed to process page %s: %w", url, err)`。

## 并发与上下文 (Context)
- 所有的爬虫网络请求和长耗时操作，必须传递并监听 `context.Context`。
- 在启动 Goroutine 时，必须确保有正确的退出机制或使用 `sync.WaitGroup` 防止 Goroutine 泄漏。
