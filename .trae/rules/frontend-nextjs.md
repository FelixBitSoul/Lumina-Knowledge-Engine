# Front-end Next.js & React 19 Rules

## 框架规范 (Next.js 15 App Router)
- **默认服务端渲染**：所有组件默认作为 Server Components 编写。
- **客户端组件边界**：仅当需要使用 `useState`, `useEffect`, `onClick` 等交互或浏览器 API 时，才在文件顶部添加 `"use client"`。
- **数据获取**：优先使用 Server Components 原生 `async/await` 获取数据，不推荐使用 SWR/React Query 除非是纯客户端的高频轮询。

## 样式规范 (Tailwind CSS v4)
- 保持 CSS 类名简洁。不要使用已经废弃的 v3 写法，拥抱 v4 的原生 CSS 变量系统。

## 类型安全 (TypeScript)
- 严禁使用 `any` 和 `@ts-ignore`。所有接口和组件的 Props 必须有明确的类型定义。
