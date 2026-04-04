# 文档异步处理系统技术设计方案

## 1. 概述

本文档描述了 Lumina Knowledge Engine 文档上传和处理流程的异步化改造方案。通过引入 Celery + Redis 作为任务队列、MinIO 作为对象存储，结合 Qdrant 向量数据库的优化索引设计，构建一个高性能、可扩展的文档处理架构。同时集成 WebSocket 实现实时通知，提升用户体验。

### 1.1 设计目标

- **异步处理**：上传文件后立即返回响应，后台异步执行 CPU/GPU 密集型的解析和向量化任务
- **用户体验优化**：避免 Web 界面在处理大文档时卡顿，提供实时处理状态反馈
- **高效过滤**：通过 Qdrant Keyword Index 实现基于 file_id 的快速过滤和删除
- **文档预览**：利用 MinIO presigned URL 实现安全、临时的文档预览功能
- **内容一致性**：基于文件内容哈希生成 file_id，确保相同内容的文件得到相同的标识
- **实时通知**：通过 WebSocket 实现任务完成后的实时推送通知
- **解耦架构**：使用 Redis Pub/Sub 实现 Worker 和 API 之间的完全解耦

---

## 2. 系统架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              前端 (Frontend)                                │
│                           http://localhost:3000                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │
│  │  File Upload    │  │  WebSocket      │  │  Task Status    │            │
│  │  /api/upload    │  │  /ws/{file_id}  │  │  Polling (fallback) │        │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘            │
└───────────┼────────────────────┼────────────────────┼───────────────────────┘
            │                    │                    │
            │ 1. Upload File      │ 2. WebSocket       │ 5. Fallback Polling
            ▼                    │  Connection        │
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FastAPI (API Server)                             │
│                         lumina-brain:8000                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │
│  │  Upload API     │  │  WebSocket      │  │  Status API     │            │
│  │  /api/upload    │  │  Manager        │  │  /api/tasks/    │            │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘            │
└───────────┼────────────────────┼────────────────────┼───────────────────────┘
            │                    │                    │
            │ 3. Store in MinIO  │                    │
            ▼                    │                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MinIO (对象存储)                                   │
│                    Bucket: documents / Preview Links                        │
└─────────────────────────────────────────────────────────────────────────────┘
            │
            │ 4. Send Task
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Redis (消息队列/缓存)                              │
│                         localhost:6379                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │
│  │  Celery Queue   │  │  Task Results   │  │  Status Cache   │            │
│  │  celery ->      │  │  celery ->      │  │  task:{id} ->   │            │
│  │  document_queue │  │  status/progress│  │  PENDING/SUCCESS │            │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘            │
└─────────────────────────────────────────────────────────────────────────────┘
            │
            │ 6. Process Task
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Celery Worker (异步任务)                             │
│                   Worker on CPU/GPU Server                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Task: process_document(file_path, file_id, metadata)                 │   │
│  │  ├── 1. Download from MinIO (if needed)                             │   │
│  │  ├── 2. Extract text (PDF/MD/TXT)                                    │   │
│  │  ├── 3. Split into chunks                                           │   │
│  │  ├── 4. Generate embeddings (all-MiniLM-L6-v2)                       │   │
│  │  ├── 5. Store in Qdrant with file_id Keyword Index                   │   │
│  │  ├── 6. Update task status                                          │   │
│  │  └── 7. Send Notification via Redis Pub/Sub                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
            │
            │ 7. Pub/Sub Message
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Redis (Pub/Sub)                                  │
│                         Channel: document_updates                          │
└─────────────────────────────────────────────────────────────────────────────┘
            │
            │ 8. Subscribe to Channel
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FastAPI (WebSocket Manager)                       │
│                         /ws/{file_id}                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  WebSocketManager                                                  │   │
│  │  ├── Connection Management                                         │   │
│  │  ├── Room Management (by file_id)                                 │   │
│  │  └── Redis Pub/Sub Listener                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
            │
            │ 9. Push Notification
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              前端 (Frontend)                                │
│                           http://localhost:3000                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 WebSocket 实时通知流程

```
┌────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌────────┐
│ Client │     │ FastAPI │     │  Redis  │     │ Celery  │     │ Client │
└───┬────┘     └────┬────┘     └────┬────┘     └────┬────┘     └───┬────┘
    │               │               │               │              │
    │ 1. POST /upload│               │               │              │
    │ ─────────────>│               │               │              │
    │               │ 2. Return file_id│               │              │
    │ <───────────── │               │               │              │
    │               │               │               │              │
    │ 3. WebSocket   │               │               │              │
    │ /ws/{file_id}  │               │               │              │
    │ ─────────────>│               │               │              │
    │               │ 4. Join Room  │               │              │
    │               │ (file_id)     │               │              │
    │ <───────────── │  Connection  │               │              │
    │  Established  │               │               │              │
    │               │               │               │              │
    │               │ 5. Send Task  │               │              │
    │               │ ─────────────>│               │              │
    │               │               │ 6. Process    │              │
    │               │               │ ─────────────>│              │
    │               │               │               │ 7. Complete  │
    │               │               │ 8. Pub/Sub    │              │
    │               │               │  Notification │              │
    │               │ 9. Receive    │ <───────────── │              │
    │               │  Notification │               │              │
    │ 10. Push to   │               │               │              │
    │ WebSocket     │               │               │              │
    │ <───────────── │               │               │              │
    │ {"status":    │               │               │              │
    │  "completed"}  │               │               │              │
    │               │               │               │              │
```

### 2.3 解耦架构说明

**核心设计原则**：使用 Redis Pub/Sub 实现 Worker 和 API 之间的完全解耦

| 组件 | 职责 | 依赖 |
|------|------|------|
| **FastAPI API** | 接收上传请求，处理 WebSocket 连接，监听 Redis 通知 | Redis (订阅) |
| **Celery Worker** | 处理文档，发送完成通知 | Redis (发布) |
| **Redis** | 消息队列 + Pub/Sub 消息传递 | - |

**无循环依赖**：
- Worker 只发布消息到 Redis，不依赖 API
- API 只订阅 Redis 消息，不依赖 Worker
- 两者通过 Redis 实现完全解耦

---

## 3. 核心组件详细设计

### 3.1 WebSocket 集成设计

#### 3.1.1 WebSocket 管理器

```python
# lumina_brain/core/services/websocket_manager.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio
import redis.asyncio as redis
from lumina_brain.config.settings import settings


class ConnectionManager:
    def __init__(self):
        # room: {file_id} -> set of websocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.redis_client = None
        self.pubsub = None

    async def connect(self, websocket: WebSocket, room: str):
        """连接到指定房间"""
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = set()
        self.active_connections[room].add(websocket)

    async def disconnect(self, websocket: WebSocket, room: str):
        """断开连接并从房间移除"""
        if room in self.active_connections:
            self.active_connections[room].remove(websocket)
            if not self.active_connections[room]:
                del self.active_connections[room]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """发送个人消息"""
        await websocket.send_json(message)

    async def broadcast(self, message: dict, room: str):
        """向房间广播消息"""
        if room in self.active_connections:
            disconnected = []
            for connection in self.active_connections[room]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)

            # 清理断开的连接
            for connection in disconnected:
                await self.disconnect(connection, room)

    async def init_redis_pubsub(self):
        """初始化 Redis Pub/Sub 监听"""
        self.redis_client = redis.Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            db=settings.redis.db
        )
        self.pubsub = self.redis_client.pubsub()
        await self.pubsub.subscribe("document_updates")

        # 启动监听任务
        asyncio.create_task(self.listen_for_notifications())

    async def listen_for_notifications(self):
        """监听 Redis Pub/Sub 通知"""
        async for message in self.pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    file_id = data.get('file_id')
                    if file_id:
                        await self.broadcast(data, file_id)
                except Exception as e:
                    print(f"Error processing pubsub message: {e}")

    async def publish_notification(self, file_id: str, status: str, **kwargs):
        """发布通知到 Redis"""
        if self.redis_client:
            message = {
                "file_id": file_id,
                "status": status,
                **kwargs
            }
            await self.redis_client.publish(
                "document_updates",
                json.dumps(message)
            )


# 创建全局 WebSocket 管理器实例
websocket_manager = ConnectionManager()
```

#### 3.1.2 WebSocket 路由

```python
# lumina_brain/api/endpoints/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from lumina_brain.core.services.websocket_manager import websocket_manager

router = APIRouter()


@router.websocket("/ws/{file_id}")
async def websocket_endpoint(websocket: WebSocket, file_id: str):
    """
    WebSocket 端点，用于实时通知文档处理状态

    - 前端应在上传文件后连接到此端点
    - 连接后会加入以 file_id 命名的房间
    - 当文档处理完成时，会收到实时通知
    """
    await websocket_manager.connect(websocket, file_id)

    # 发送连接成功消息
    await websocket_manager.send_personal_message(
        {
            "status": "connected",
            "message": f"Connected to room {file_id}",
            "file_id": file_id
        },
        websocket
    )

    try:
        while True:
            # 保持连接，接收前端消息（如果需要）
            data = await websocket.receive_text()
            # 可以处理前端发送的消息，如心跳等
            await websocket_manager.send_personal_message(
                {
                    "status": "ack",
                    "message": "Message received",
                    "data": data
                },
                websocket
            )
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket, file_id)
```

#### 3.1.3 Redis 配置

```python
# settings.py 扩展

class RedisSettings(BaseSettings):
    """Redis configuration settings"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


class Settings(BaseSettings):
    # ... 现有配置 ...
    redis: RedisSettings = RedisSettings()  # ★ 新增
```

---

### 3.2 Celery 任务通知机制

#### 3.2.1 任务完成后发送通知

```python
# lumina_brain/tasks/document_tasks.py 扩展

@celery_app.task(bind=True, name="lumina_brain.tasks.process_document")
def process_document(self, file_id: str, filename: str, category: str, collection: str = "documents"):
    """
    异步文档处理任务

    流程:
    1. 从 MinIO 下载原始文件
    2. 提取文本内容
    3. 文本分块
    4. 生成向量嵌入
    5. 存储到 Qdrant
    6. 更新任务状态
    7. 发送 Redis Pub/Sub 通知
    """
    try:
        # ... 现有处理逻辑 ...

        # 任务完成后发送 Redis Pub/Sub 通知
        send_document_completion_notification(file_id, {
            "filename": filename,
            "chunks_created": len(chunks),
            "collection": collection
        })

        self.update_state(state="SUCCESS", meta={
            "status": "completed",
            "file_id": file_id,
            "chunks_created": len(chunks),
        })

        return {
            "file_id": file_id,
            "filename": filename,
            "chunks_created": len(chunks),
            "status": "success",
        }

    except Exception as e:
        # 发送失败通知
        send_document_failure_notification(file_id, str(e))
        self.update_state(state="FAILURE", meta={
            "status": "failed",
            "file_id": file_id,
            "error": str(e),
        })
        raise


def send_document_completion_notification(file_id: str, metadata: dict = None):
    """发送文档处理完成通知"""
    import redis
    import json

    r = redis.Redis(
        host=settings.redis.host,
        port=settings.redis.port,
        db=settings.redis.db
    )

    message = {
        "file_id": file_id,
        "status": "completed",
        "timestamp": datetime.now().isoformat(),
        **(metadata or {})
    }

    r.publish("document_updates", json.dumps(message))


def send_document_failure_notification(file_id: str, error: str):
    """发送文档处理失败通知"""
    import redis
    import json

    r = redis.Redis(
        host=settings.redis.host,
        port=settings.redis.port,
        db=settings.redis.db
    )

    message = {
        "file_id": file_id,
        "status": "failed",
        "error": error,
        "timestamp": datetime.now().isoformat()
    }

    r.publish("document_updates", json.dumps(message))
```

#### 3.2.2 任务进度通知（可选）

```python
# 任务进度通知
@celery_app.task(bind=True, name="lumina_brain.tasks.process_document")
def process_document(self, file_id: str, filename: str, category: str, collection: str = "documents"):
    try:
        # ... 处理逻辑 ...

        for i, chunk in enumerate(chunks):
            if i % 10 == 0:
                # 发送进度通知
                send_document_progress_notification(file_id, {
                    "progress": i,
                    "total": len(chunks),
                    "step": "embedding"
                })

            # ... 现有处理 ...

        # ... 完成逻辑 ...

    except Exception as e:
        # ... 错误处理 ...


def send_document_progress_notification(file_id: str, progress_data: dict):
    """发送文档处理进度通知"""
    import redis
    import json

    r = redis.Redis(
        host=settings.redis.host,
        port=settings.redis.port,
        db=settings.redis.db
    )

    message = {
        "file_id": file_id,
        "status": "processing",
        "timestamp": datetime.now().isoformat(),
        **progress_data
    }

    r.publish("document_updates", json.dumps(message))
```

---

### 3.3 前端 WebSocket 集成

#### 3.3.1 前端连接逻辑

```javascript
// 前端 WebSocket 连接示例

class DocumentUploader {
  constructor() {
    this.ws = null;
    this.fileId = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 3;
  }

  async uploadFile(file, category) {
    // 1. 上传文件
    const formData = new FormData();
    formData.append("file", file);
    formData.append("category", category);

    const response = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Upload failed");
    }

    const result = await response.json();
    this.fileId = result.file_id;

    // 2. 建立 WebSocket 连接
    this.connectWebSocket();

    return result;
  }

  connectWebSocket() {
    if (!this.fileId) {
      console.error("No file_id to connect WebSocket");
      return;
    }

    const wsUrl = `ws://localhost:8000/ws/${this.fileId}`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log(`WebSocket connected to room ${this.fileId}`);
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleWebSocketMessage(message);
    };

    this.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    this.ws.onclose = () => {
      console.log("WebSocket disconnected");
      this.attemptReconnect();
    };
  }

  handleWebSocketMessage(message) {
    console.log("WebSocket message:", message);

    switch (message.status) {
      case "connected":
        console.log("Connected to WebSocket server");
        break;

      case "processing":
        // 显示处理进度
        const progress = message.progress || 0;
        const total = message.total || 100;
        console.log(`Processing: ${progress}/${total} (${message.step})`);
        // 更新 UI 进度条
        break;

      case "completed":
        console.log("Document processing completed!");
        console.log("Result:", message);
        // 显示完成消息
        // 关闭 WebSocket 连接
        this.ws.close();
        break;

      case "failed":
        console.error("Document processing failed:", message.error);
        // 显示错误消息
        this.ws.close();
        break;

      default:
        console.log("Unknown message:", message);
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      setTimeout(() => {
        this.connectWebSocket();
      }, 1000 * this.reconnectAttempts);
    } else {
      console.error("Max reconnection attempts reached. Falling back to polling.");
      this.startPolling();
    }
  }

  startPolling() {
    if (!this.fileId) return;

    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/upload/tasks/${this.fileId}`);
        const status = await response.json();

        if (status.status === "completed" || status.status === "failed") {
          clearInterval(pollInterval);
          this.handleWebSocketMessage(status);
        } else if (status.status === "processing") {
          this.handleWebSocketMessage(status);
        }
      } catch (error) {
        console.error("Polling error:", error);
      }
    }, 2000);
  }

  closeWebSocket() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// 使用示例
const uploader = new DocumentUploader();

async function handleFileUpload(file) {
  try {
    const result = await uploader.uploadFile(file, "technical");
    console.log("Upload initiated:", result);
  } catch (error) {
    console.error("Upload error:", error);
  }
}
```

#### 3.3.2 错误处理与降级策略

| 场景 | 处理策略 | 备注 |
|------|---------|------|
| WebSocket 连接失败 | 尝试重连 3 次 | 指数退避策略 |
| 重连失败 | 降级到轮询 | 每 2 秒查询一次状态 |
| 网络中断 | 自动重连 | 恢复连接后继续接收通知 |
| 服务器重启 | 重新连接 | 保持文件处理状态 |

---

### 3.4 API 改造设计

#### 3.4.1 上传 API 改造

```python
# lumina_brain/api/endpoints/upload.py 改造

@router.post("", status_code=202)
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload"),
    category: str = Form(..., description="Category for the document"),
    collection: Optional[str] = Form(None, description="Collection name"),
):
    """
    异步上传文档

    返回:
        - task_id: Celery 任务 ID，用于查询处理状态
        - file_id: 文档唯一标识（基于内容哈希）
        - websocket_url: WebSocket 连接 URL，用于实时通知
        - 立即返回，前端可通过 WebSocket 或轮询获取状态
    """
    # ... 现有上传逻辑 ...

    # 启动 Celery 任务
    task = process_document.apply_async(
        args=[file_id, file.filename, category, target_collection],
        task_id=file_id,
    )

    return {
        "task_id": task.id,
        "file_id": file_id,
        "file_name": file.filename,
        "category": category,
        "collection": target_collection,
        "status": "pending",
        "websocket_url": f"ws://{settings.api.host}:{settings.api.port}/ws/{file_id}",
        "message": "Document uploaded successfully. Processing in background.",
    }
```

---

## 4. 系统集成与启动流程

### 4.1 应用启动流程

```python
# lumina_brain/main.py

from fastapi import FastAPI
from lumina_brain.api.endpoints import upload, websocket, documents
from lumina_brain.core.services.websocket_manager import websocket_manager

app = FastAPI()

# 注册路由
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(websocket.router, tags=["websocket"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化 WebSocket 管理器"""
    await websocket_manager.init_redis_pubsub()
    print("WebSocket manager initialized with Redis Pub/Sub")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    if websocket_manager.redis_client:
        await websocket_manager.redis_client.close()
    print("WebSocket manager resources cleaned up")
```

### 4.2 Docker Compose 配置

```yaml
# docker-compose.yml 扩展

services:
  # ... 现有服务 ...

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"  # API
      - "9001:9001"  # Console
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data

  celery_worker:
    build:
      context: ./services/lumina-brain
      dockerfile: Dockerfile
    command: celery -A lumina_brain.celery_app worker --loglevel=info --concurrency=4
    depends_on:
      - redis
      - minio
      - qdrant
    volumes:
      - ./services/lumina-brain:/app
      - model_cache:/root/.cache/huggingface

  fastapi:
    build:
      context: ./services/lumina-brain
      dockerfile: Dockerfile
    command: uvicorn lumina_brain.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    depends_on:
      - redis
      - qdrant
    volumes:
      - ./services/lumina-brain:/app

volumes:
  redis_data:
  minio_data:
  model_cache:
```

---

## 5. 安全性考虑

### 5.1 WebSocket 安全

- **认证机制**：可选添加 JWT 认证，在 WebSocket 连接时验证
- **房间隔离**：确保用户只能连接到自己的 file_id 房间
- **消息验证**：验证消息格式和内容，防止恶意消息
- **连接限制**：限制单个用户的 WebSocket 连接数

### 5.2 Redis 安全

- **访问控制**：设置 Redis 密码认证
- **网络隔离**：在生产环境中限制 Redis 只允许内部网络访问
- **数据加密**：考虑对敏感消息进行加密

### 5.3 前端安全

- **WebSocket URL 验证**：确保连接到正确的 WebSocket 端点
- **消息处理**：验证接收到的消息格式，防止注入攻击
- **错误处理**：优雅处理 WebSocket 错误，避免暴露敏感信息

---

## 6. 性能优化

### 6.1 WebSocket 性能

- **连接池管理**：合理管理 WebSocket 连接，避免资源泄漏
- **消息批处理**：对于频繁的进度更新，考虑批处理消息
- **心跳机制**：定期发送心跳消息，检测连接状态
- **自动重连**：实现智能重连机制，提高可靠性

### 6.2 Redis 性能

- **Pub/Sub 优化**：使用专用的 Redis 实例处理 Pub/Sub
- **消息大小**：保持消息简洁，避免发送过大的消息
- **连接池**：使用 Redis 连接池，提高连接效率

### 6.3 Celery 性能

- **任务优先级**：根据文档大小设置任务优先级
- **Worker 配置**：根据系统资源调整 worker 数量
- **任务超时**：合理设置任务超时时间

---

## 7. 监控与日志

### 7.1 WebSocket 监控

```python
# lumina_brain/monitoring/metrics.py 扩展

from prometheus_client import Counter, Gauge

websocket_connections_total = Gauge(
    "websocket_connections_total",
    "Current number of WebSocket connections",
    ["room"]
)

websocket_messages_total = Counter(
    "websocket_messages_total",
    "Total number of WebSocket messages",
    ["direction", "status"]
)

notification_events_total = Counter(
    "notification_events_total",
    "Total number of notification events",
    ["event_type"]
)
```

### 7.2 日志记录

```python
# lumina_brain/core/services/websocket_manager.py 扩展

import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    # ... 现有代码 ...

    async def connect(self, websocket: WebSocket, room: str):
        """连接到指定房间"""
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = set()
        self.active_connections[room].add(websocket)
        logger.info(f"WebSocket connected: room={room}, connections={len(self.active_connections[room])}")

    async def disconnect(self, websocket: WebSocket, room: str):
        """断开连接并从房间移除"""
        if room in self.active_connections:
            self.active_connections[room].remove(websocket)
            if not self.active_connections[room]:
                del self.active_connections[room]
            logger.info(f"WebSocket disconnected: room={room}, connections={len(self.active_connections.get(room, []))}")

    async def broadcast(self, message: dict, room: str):
        """向房间广播消息"""
        if room in self.active_connections:
            disconnected = []
            for connection in self.active_connections[room]:
                try:
                    await connection.send_json(message)
                    logger.debug(f"Message sent to room {room}: {message}")
                except Exception as e:
                    disconnected.append(connection)
                    logger.error(f"Error sending message: {e}")

            # 清理断开的连接
            for connection in disconnected:
                await self.disconnect(connection, room)
```

---

## 8. 实施计划

### Phase 1: 基础设施搭建 (1-2天)
1. 部署 Redis 和 MinIO
2. 配置 Celery + Redis 连接
3. 创建 MinIO Service 类

### Phase 2: WebSocket 集成 (2天)
1. 实现 WebSocket 管理器
2. 创建 WebSocket 路由
3. 配置 Redis Pub/Sub

### Phase 3: 异步任务改造 (2-3天)
1. 重构 upload API 为异步模式
2. 实现 `process_document` Celery 任务
3. 添加任务完成通知机制
4. 添加任务状态查询 API

### Phase 4: Qdrant 索引优化 (1天)
1. 添加 file_id Keyword Index
2. 实现 `delete_by_file_id` 方法
3. 实现 `search_within_file` 方法

### Phase 5: 前端集成 (1-2天)
1. 实现 WebSocket 连接逻辑
2. 添加错误处理和降级策略
3. 实现实时进度显示

### Phase 6: 测试与优化 (2-3天)
1. 集成测试
2. 性能基准测试
3. 错误处理验证
4. 监控指标集成

---

## 9. 总结

本方案通过引入 **Celery + Redis** 实现文档处理的异步化，**MinIO** 作为对象存储提供原始文件管理和预览功能，**Qdrant** 的 Keyword Index 优化实现高效的基于 file_id 的过滤和删除操作，以及 **WebSocket** 实现实时通知功能。

### 关键收益

| 收益 | 说明 |
|------|------|
| **响应速度** | 上传接口从 ~30s 降到 <1s |
| **用户体验** | 前端不阻塞，可实时查看处理进度 |
| **实时通知** | WebSocket 推送任务完成通知，无需轮询 |
| **解耦架构** | Redis Pub/Sub 实现 Worker 和 API 完全解耦 |
| **资源利用** | 后台任务利用空闲资源处理 |
| **删除效率** | 文档删除从 O(n) 降到 O(1) |
| **预览能力** | 安全、临时的文档预览链接 |
| **内容一致性** | 基于内容哈希生成 file_id，确保相同内容得到相同标识 |

### 技术栈

- **任务队列**: Celery 5.x
- **消息代理**: Redis 7.x (用于 Celery 和 Pub/Sub)
- **对象存储**: MinIO
- **向量数据库**: Qdrant
- **嵌入模型**: all-MiniLM-L6-v2
- **WebSocket**: FastAPI WebSockets

---

*文档版本: 1.3*
*创建日期: 2026-04-04*
*更新: 优化解耦架构，使用 Redis Pub/Sub 实现 Worker 和 API 完全解耦*
