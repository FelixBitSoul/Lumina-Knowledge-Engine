# Git Commit & Branch Rules

## 提交信息规范 (Conventional Commits)
每次提交必须严格遵循以下格式：`<type>([scope]): <description>`
- `type` 只能是：`feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- `scope` 是可选的，如 `(portal)`, `(brain-api)`, `(crawler)`
- `description` 必须简洁明了。

示例：`feat(portal): add PDF upload button in search bar`

## 分支命名
- 新功能：`feature/xxx`
- 修复：`bugfix/xxx`
