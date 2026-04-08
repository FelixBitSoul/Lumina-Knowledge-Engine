# AGENTS.md - Lumina Knowledge Engine 多智能体协作指南

## 1. 项目概览

Lumina Knowledge Engine 是一个现代化的 RAG (Retrieval-Augmented Generation) 系统，用于语义文档搜索和知识管理。项目使用 Go、Python 和 Next.js 构建，具有高性能和可扩展性。

**核心技术栈：**
- **后端**：Go 1.24 (Colly 2.2.0 爬虫)、Python 3.11+ (FastAPI 0.104+)
- **AI/ML**：sentence-transformers 2.2+、Qdrant-Client 1.6+、OpenAI 1.0+
- **前端**：Next.js 15.0.2、React 19.0.0、Tailwind CSS v4
- **数据库**：Qdrant 向量数据库 (384维向量)
- **基础设施**：Docker、Docker Compose、Redis、MinIO、Celery

**主要服务：**
- **Crawler**：Go 语言编写的网络爬虫，用于网页内容抓取和提取
- **Brain API**：Python FastAPI 服务，提供向量嵌入和语义搜索功能
- **Portal**：Next.js 前端，提供用户界面和搜索前端
- **Qdrant**：向量数据库，用于高性能向量存储
- **Redis**：任务队列和 Pub/Sub
- **MinIO**：对象存储，用于文档存储
- **Celery**：后台任务处理

## 2. 多智能体系统概述

### 2.1 智能体架构

Lumina Knowledge Engine 采用多智能体协作架构，由以下核心智能体组成：

| 智能体名称 | 英文标识符 | 角色 | 职责 | 工具访问 |
|-----------|------------|------|------|----------|
| **主智能体 (SOLO Coder)** | - | 协调者 | 任务规划、智能体调度、结果整合 | 所有工具 |
| **Lumina PM** | lumina-pm | 产品负责人 | 需求定义、优先级排序、验收标准定义、冲突协调 | docs/ 目录 |
| **Lumina Architect** | lumina-architect | 项目架构师 | 高层设计、技术选型方案评审、接口契约一致性、架构文档维护 | AGENTS.md、docs/ 目录 |
| **Brain API Specialist** | brain-api-dev | 后端专家 | 优化 Qdrant 向量检索逻辑、编写高性能 Celery 后台任务 | services/lumina-brain 代码库 |
| **Portal Frontend Dev** | portal-frontend-dev | 前端专家 | 界面开发、用户交互、响应式设计、TypeScript 类型安全 | services/portal-next 代码库 |
| **Crawler & Infra Dev** | crawler-infra-dev | 爬虫与运维专家 | 维护爬虫代码、优化爬取效率、管理 Docker 配置、处理基础设施问题 | services/crawler-go 代码库、deployments/ 目录 |
| **Lumina QA Specialist** | qa-test-expert | 测试与质量专家 | 全栈测试、集成测试、边界检查、性能基准 | 所有测试工具 |

### 2.2 智能体协作模式

采用 **协作型** 多智能体模式：
- 多个智能体目标一致，通过资源共享、任务互补完成复杂目标
- 主智能体负责任务分解和调度
- 专业智能体负责各自领域的具体任务
- 结果由主智能体汇总和整合

### 2.3 通信机制

智能体间通过以下方式通信：

1. **共享上下文**：使用 Redis 作为共享上下文存储
2. **消息传递**：基于 MCP (多智能体通信协议) 的消息格式
3. **结果传递**：通过文件系统或 API 传递处理结果

### 2.4 智能体详细配置

#### 2.4.1 Lumina PM (Product Manager)
- **英文标识符**：lumina-pm
- **角色**：产品负责人
- **核心职责**：
  - 需求定义：负责编写和更新 docs/PRD.md，将用户愿景转化为具体的功能规格
  - 优先级排序：在多任务并行时，决定哪些功能（如爬虫优化 vs 搜索界面更新）应优先处理
  - 验收标准（AC）：为每个任务定义清晰的验收标准，供 QA 专家参考
  - 冲突协调：当技术实现与用户体验冲突时，从产品价值角度做出裁决
- **行为准则**：在任何专家开始写代码前，确保需求已在 docs/ 中定义清晰
- **调用时机**：当收到新功能请求、需求不明确、需要更新产品文档或评估功能优先级时

#### 2.4.2 Lumina Architect
- **英文标识符**：lumina-architect
- **角色**：项目架构师
- **核心职责**：
  - 确保 Brain API、Portal 和 Crawler 三者之间的接口契约（Contract）一致性
  - 负责维护 AGENTS.md 和 docs/ 下的系统架构文档
  - 当用户提出新需求时，先输出技术实现方案，而非直接写代码
- **调用时机**：当涉及跨服务更改、新功能规划或需要修改项目核心架构文档时

#### 2.4.3 Brain API Specialist
- **英文标识符**：brain-api-dev
- **角色**：后端专家
- **技术栈限制**：必须使用 uv 管理依赖，遵循 FastAPI 异步最佳实践
- **核心职责**：
  - 优化 Qdrant 向量检索逻辑（384维）
  - 编写高性能的 Celery 后台任务
  - 必须确保通过 Docker Compose 运行 pytest 在修改后通过
- **调用时机**：当需要修改 Python 代码、优化向量数据库逻辑或调整 Brain API 端点时

#### 2.4.4 Portal Frontend Dev
- **英文标识符**：portal-frontend-dev
- **角色**：前端专家
- **技术栈限制**：使用 Next.js 15 (App Router)、React 19 和 Tailwind CSS v4
- **核心职责**：
  - 确保 UI 组件的类型安全（TypeScript 严格模式）
  - 利用 React 19 的新特性（如 Server Actions/Components）优化交互
  - 保持 CSS 类名简洁，遵循 Tailwind v4 规范
- **调用时机**：当涉及页面布局、前端组件、API 集成或样式调整时

#### 2.4.5 Crawler & Infra Dev
- **英文标识符**：crawler-infra-dev
- **角色**：爬虫与运维专家
- **技术栈限制**：Go 1.24 (Colly 框架)、Docker Compose
- **核心职责**：
  - 维护 services/crawler-go，优化爬取效率和反爬策略
  - 编写和优化 deployments/docker-compose.yaml
  - 处理 Redis、MinIO 等基础设施的连接与配置问题
- **调用时机**：当需要修改爬虫代码、优化爬取策略、调整 Docker 配置或处理基础设施问题时

#### 2.4.6 Lumina QA Specialist
- **英文标识符**：qa-test-expert
- **角色**：测试与质量专家
- **核心职责**：
  - 全栈测试：监督并执行 Brain API (pytest)、Portal (Jest) 和 Crawler (go test) 的测试方案，运用 Playwright 编写和执行端到端测试，重点验证 Next.js 15 和 Tailwind v4 的交互稳定性
  - 集成测试：编写跨服务的测试脚本，验证从“爬虫抓取 -> Brain 向量化 -> Portal 搜索”的完整链路
  - 边界检查：严格执行 AGENTS.md 中关于禁止硬编码密钥和数据库模式未经授权更改的规定
  - 性能基准：监控向量检索的响应时间和爬虫的并发效率
- **调用时机**：当需要编写测试用例、执行全链路自动化测试、进行版本发布前的回归测试，或需要评估 RAG 搜索相关性时

### 2.5 最佳实践

- **智能体数量控制**：根据任务复杂度，合理配置智能体数量，避免过多智能体导致的通信开销
- **职责明确**：每个智能体有清晰的职责边界，避免角色重叠
- **工具访问精细化**：只向智能体开放其所需的工具，避免工具滥用
- **内存本地化**：每个智能体只保留与自身任务相关的上下文，避免全局上下文导致的 token 爆炸
- **终止条件设定**：为每个智能体设置明确的任务完成条件，避免无限循环
- **智能体协作流程**：
  1. 需求阶段：Lumina PM 定义需求和验收标准
  2. 设计阶段：Lumina Architect 制定技术方案
  3. 开发阶段：各专业智能体（Brain API、Frontend、Crawler）实现功能
  4. 测试阶段：Lumina QA Specialist 执行测试方案
  5. 部署阶段：Crawler & Infra Dev 处理部署和基础设施配置

## 3. 开发环境设置

### 3.1 前提条件

- Docker 20.10+
- Docker Compose 1.29+

### 3.2 环境配置

**使用 Docker Compose 环境变量：**

1. 在 `deployments` 目录创建 `.env` 文件（基于 `.env.example`）：

```bash
# Qdrant Configuration
QDRANT_VERSION=v1.10.0
HOST_QDRANT_REST_PORT=6333
HOST_QDRANT_GRPC_PORT=6334
QDRANT_COLLECTION=knowledge_base

# Brain API Configuration
HOST_BRAIN_API_PORT=8000
MODEL_NAME=all-MiniLM-L6-v2
MODEL_CACHE_DIR=/app/models

# Portal Configuration
HOST_PORTAL_PORT=3000

# Crawler Configuration
BRAIN_INGEST_URL=http://brain-api:8000/api/ingest

# Logging
LOG_LEVEL=info
```

所有服务的环境变量已在 `docker-compose.yaml` 中配置，无需在本地创建单独的 `.env` 文件。

## 4. 常用命令

### 4.1 启动服务

**使用 Docker Compose：**
```bash
# 启动所有服务
cd deployments
docker-compose up -d

# 启动带爬虫的服务
cd deployments
docker-compose --profile crawler up -d

# 启动特定服务
cd deployments
docker-compose up -d qdrant  # 仅启动 Qdrant
cd deployments
docker-compose up -d brain-api  # 仅启动 Brain API
cd deployments
docker-compose up -d portal  # 仅启动 Portal
```

### 4.2 停止服务

```bash
# 停止所有服务
cd deployments
docker-compose down

# 停止特定服务
cd deployments
docker-compose stop brain-api portal
```

### 4.3 测试命令

**通过 Docker Compose 运行测试：**

```bash
# 运行 Brain API 测试
cd deployments
docker-compose run --rm brain-api pytest

# 运行 Portal 测试
cd deployments
docker-compose run --rm portal npm test

# 运行 Crawler 测试
cd deployments
docker-compose run --rm crawler go test ./...
```

### 4.4 构建命令

**通过 Docker Compose 构建服务：**

```bash
# 构建所有服务
cd deployments
docker-compose build

# 构建特定服务
cd deployments
docker-compose build brain-api  # 仅构建 Brain API
cd deployments
docker-compose build portal  # 仅构建 Portal
cd deployments
docker-compose build crawler  # 仅构建 Crawler
```

## 5. 代码风格指南

### 5.1 Python (Brain API)

- 遵循 PEP 8 编码规范
- 使用 4 个空格进行缩进
- 文件名使用小写蛇形命名法 (`snake_case`)
- 类名使用驼峰命名法 (`CamelCase`)
- 函数和变量名使用小写蛇形命名法 (`snake_case`)
- 导入语句按标准库、第三方库、本地库的顺序排列
- 使用类型注解

### 5.2 Go (Crawler)

- 遵循 Go 官方代码风格
- 使用 `gofmt` 进行代码格式化
- 文件名使用小写蛇形命名法 (`snake_case`)
- 包名使用小写字母
- 函数名使用驼峰命名法 (`CamelCase`)
- 变量名使用驼峰命名法 (`camelCase`)

### 5.3 TypeScript/JavaScript (Portal)

- 使用 TypeScript 严格模式
- 文件名使用 PascalCase 或 camelCase
- 组件名使用 PascalCase
- 函数和变量名使用 camelCase
- 使用 ESLint 进行代码检查
- 使用 Prettier 进行代码格式化

## 6. 测试指南

### 6.1 Brain API 测试

- 测试文件位于 `services/lumina-brain/tests/` 目录
- 使用 pytest 运行测试
- 测试涵盖 API 端点、核心服务和文档处理功能

### 6.2 Portal 测试

- 测试文件位于 `services/portal-next/tests/` 目录
- 使用 Jest 运行测试
- 测试涵盖组件、钩子和 API 集成

### 6.3 测试覆盖要求

- 新功能必须有相应的测试
- 代码修改后必须通过所有测试
- 测试覆盖率应保持在合理水平

## 7. 构建和部署

### 7.1 Docker 部署

**使用 Docker Compose：**
```bash
# 启动所有服务
docker-compose -f deployments/docker-compose.yaml up -d

# 查看日志
docker-compose -f deployments/docker-compose.yaml logs -f [service-name]

# 停止所有服务
docker-compose -f deployments/docker-compose.yaml down
```

### 7.2 环境配置

**开发环境：**
- 使用 `dev.yaml` 配置文件
- 启用热重载
- 详细日志

**生产环境：**
- 使用 `prod.yaml` 配置文件
- 禁用热重载
- 简洁日志
- 启用 HTTPS (如果需要)

## 8. 安全考虑

### 8.1 密钥管理

- 不要在代码中硬编码 API 密钥和其他敏感信息
- 使用环境变量或安全的密钥管理系统
- `.env` 文件应添加到 `.gitignore`

### 8.2 安全测试

- 定期进行安全扫描
- 遵循安全最佳实践
- 及时更新依赖以修复安全漏洞

### 8.3 权限模型

- 实现适当的访问控制
- 限制敏感操作的权限
- 记录关键操作的审计日志

## 9. 行为边界

### 9.1 允许的操作

- 编写和修改 `src/` 目录下的代码
- 添加新功能和修复 bug
- 运行测试和构建命令
- 更新文档

### 9.2 禁止的操作

- 修改 `.github/workflows` 下的 CI/CD 配置
- 提交硬编码的 API 密钥或其他敏感信息
- 修改数据库模式（除非得到明确授权）
- 更改项目的核心架构（除非得到明确授权）

## 10. Git 工作流

### 10.1 分支命名规则

- 特性分支：`feature/feature-name`
- 修复分支：`fix/bug-description`
- 改进分支：`improvement/improvement-description`

### 10.2 提交信息格式

```
[类型]: 简短描述

详细描述（可选）

关联的 issue #（如果有）
```

**类型**：
- `feat`：新功能
- `fix`：bug 修复
- `docs`：文档更新
- `style`：代码风格修改
- `refactor`：代码重构
- `test`：测试更新
- `chore`：构建或依赖更新

### 10.3 Pull Request 指南

- 标题格式：`[组件] 简短描述`
- 提交前必须通过 Docker Compose 运行测试：
  - Brain API: `docker-compose run --rm brain-api pytest`
  - Portal: `docker-compose run --rm portal npm test`
  - Crawler: `docker-compose run --rm crawler go test ./...`
- 提交前必须通过代码风格检查
- 提供清晰的 PR 描述，包括变更内容和理由
- 关联相关的 issue

## 11. 调试和故障排除

### 11.1 常见问题和解决方案

**Qdrant 连接问题：**
- 确保 Qdrant 服务正在运行
- 检查 `QDRANT_HOST` 和 `QDRANT_PORT` 环境变量
- 验证网络连接

**模型加载失败：**
- 确保网络连接正常
- 检查 `MODEL_CACHE_DIR` 权限
- 验证模型名称是否正确

**文档处理失败：**
- 检查文件格式是否支持
- 验证文件大小是否在限制范围内
- 查看 Celery 日志获取详细错误信息

### 11.2 日志模式

**通过 Docker Compose 查看日志：**

```bash
# 查看所有服务日志
cd deployments
docker-compose logs -f

# 查看特定服务日志
cd deployments
docker-compose logs -f brain-api  # 查看 Brain API 日志
cd deployments
docker-compose logs -f portal  # 查看 Portal 日志
cd deployments
docker-compose logs -f crawler  # 查看 Crawler 日志
cd deployments
docker-compose logs -f celery-worker  # 查看 Celery Worker 日志

# 查看最近的日志
cd deployments
docker-compose logs --tail=100 brain-api
```

### 11.3 性能考虑

- 对于大型文档，使用异步处理
- 优化向量搜索参数
- 监控系统资源使用情况

## 12. 附加说明

### 12.1 项目特定上下文

- 本项目使用 `uv` 作为 Python 包管理器，而不是 `pip`
- 前端使用 Next.js 15 App Router
- 爬虫使用 Go 语言的 Colly 框架

### 12.2 常见陷阱

- 确保所有服务都使用正确的端口和主机名
- 注意环境变量的大小写
- 确保 Qdrant 集合已正确创建

### 12.3 性能优化

- 使用批量处理减少 API 调用
- 合理设置向量搜索的 `limit` 和 `offset` 参数
- 对于大型文档，考虑使用分块处理

## 13. 相关文档

- **系统架构**：`docs/architecture/system-overview.md`
- **API 文档**：`docs/api/brain-api.md`
- **爬虫配置**：`docs/api/crawler-config.md`
- **部署指南**：`docs/deployment/`
- **前端集成**：`docs/api/portal-integration.md`
- **技术指南**：`docs/guidelines/`
- **产品需求**：`docs/PRD.md`

## 14. 支持

- **问题**：[GitHub Issues](https://github.com/FelixBitSoul/lumina-knowledge-engine/issues)
- **文档**：[完整文档](docs/)
- **讨论**：[GitHub Discussions](https://github.com/FelixBitSoul/lumina-knowledge-engine/discussions)

---

<p align="center">
  为 Lumina Knowledge Engine 🔍 构建
</p>
