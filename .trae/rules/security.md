# Strict Security Rules

## 凭证管理 (Zero Tolerance)
- 绝对禁止在代码中硬编码任何 API Keys (如 OpenAI 密钥)、数据库密码或访问令牌。
- 所有机密配置必须通过环境变量注入（例如使用 `os.getenv()` 或 `process.env`）。

## SQL/NoSQL 注入防御
- 禁止拼接查询字符串。与 Qdrant 或其他数据库交互时，必须使用官方 SDK 提供的参数化查询或数据模型。
