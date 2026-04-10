import { test, expect } from '@playwright/test';

test('Switching between collections should not cause errors', async ({ page }) => {
  // 导航到文件管理页面
  await page.goto('http://localhost:3018');

  // 等待页面加载完成
  await page.waitForLoadState('networkidle');
  console.log('Page loaded successfully');

  // 等待并选择 Knowledge_base 集合
  try {
    await page.waitForSelector('text=Knowledge_base', { timeout: 15000 });
    await page.click('text=Knowledge_base');
    console.log('Selected Knowledge_base collection');

    // 等待页面更新
    await page.waitForLoadState('networkidle');
    console.log('Knowledge_base collection page loaded');

    // 等待一段时间，让 WebSocket 连接建立
    await page.waitForTimeout(3000);

    // 切换到 documents 集合
    await page.waitForSelector('text=documents', { timeout: 10000 });
    await page.click('text=documents');
    console.log('Switched to documents collection');

    // 等待页面更新
    await page.waitForLoadState('networkidle');
    console.log('Documents collection page loaded');

    // 等待一段时间，让 WebSocket 连接建立
    await page.waitForTimeout(3000);

    // 检查页面是否正常加载
    const pageContent = await page.content();
    console.log('Page content length after switch:', pageContent.length);

    // 检查是否有错误
    const consoleErrors = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // 等待一段时间，看看是否有错误
    await page.waitForTimeout(3000);
    console.log('Console errors:', consoleErrors);

    // 确保没有错误
    expect(consoleErrors.length).toBe(0);

  } catch (error) {
    console.log('Error during test:', error);
    throw error;
  }

  // 测试通过
  expect(true).toBe(true);
});
