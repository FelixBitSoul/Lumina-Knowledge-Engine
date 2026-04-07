# Python & FastAPI Rules

## 类型提示 (Type Hinting)
- 强制要求：所有函数参数和返回值必须包含严格的类型注解（Type Hints）。
- 优先使用 Python 3.11+ 的原生类型（如 `list[str]`, `str | None`），不再使用 `typing.List` 或 `typing.Optional`。

## FastAPI 异步规范
- 所有的 API 路由函数（路由处理程序）如果涉及 I/O 操作（如查询 Qdrant、请求 OpenAI），必须定义为 `async def`。
- 如果必须调用同步的阻塞库，请使用 `run_in_threadpool` 包装。

## 依赖管理限制
- 只能使用 `uv add` 或 `uv remove` 管理依赖，绝对禁止使用 `pip install`。
