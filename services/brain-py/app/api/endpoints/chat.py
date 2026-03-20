from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
import json
import time
import uuid
import logging

from app.schemas.chat import ChatRequest, ChatResponse
from app.core.llm_service import generate_response, generate_streaming_response
from app.core.vector_service import search_relevant_documents

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 对话存储
conversations = {}

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """处理对话请求"""
    try:
        logger.info(f"Received chat request: {request.message}, collection: {request.collection}")

        # 生成对话ID
        conversation_id = request.conversation_id or str(uuid.uuid4())
        logger.info(f"Generated conversation ID: {conversation_id}")

        # 检索相关文档作为上下文
        logger.info("Searching for relevant documents...")
        context = search_relevant_documents(request.message, request.collection)
        logger.info(f"Found {len(context)} relevant documents")

        # 生成响应
        logger.info("Generating response from LLM...")
        content = generate_response(request.message, context, conversation_id)
        logger.info(f"Received response from LLM: {content[:100]}...")

        # 保存对话历史
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        conversations[conversation_id].append({"role": "user", "content": request.message})
        conversations[conversation_id].append({"role": "assistant", "content": content})
        logger.info(f"Saved conversation history for ID: {conversation_id}")

        # 构建响应
        response = ChatResponse(
            id=str(uuid.uuid4()),
            content=content,
            conversation_id=conversation_id,
            timestamp=int(time.time())
        )

        logger.info(f"Returning chat response: {response.id}")
        return response
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/stream")
async def stream_chat(request: ChatRequest):
    """处理流式对话请求"""
    async def stream():
        try:
            logger.info(f"Received streaming chat request: {request.message}, collection: {request.collection}")

            # 生成对话ID
            conversation_id = request.conversation_id or str(uuid.uuid4())
            logger.info(f"Generated conversation ID: {conversation_id}")

            # 检索相关文档作为上下文
            logger.info("Searching for relevant documents...")
            context = search_relevant_documents(request.message, request.collection)
            logger.info(f"Found {len(context)} relevant documents")

            # 保存用户消息
            if conversation_id not in conversations:
                conversations[conversation_id] = []
            conversations[conversation_id].append({"role": "user", "content": request.message})
            logger.info(f"Saved user message for conversation: {conversation_id}")

            # 生成流式响应
            logger.info("Generating streaming response from LLM...")
            assistant_message = ""
            for chunk in generate_streaming_response(request.message, context, conversation_id):
                assistant_message += chunk
                # 构建SSE格式的响应
                yield f'data: {json.dumps({"id": str(uuid.uuid4()), "content": chunk, "conversation_id": conversation_id, "is_finished": False})}\n\n'

            logger.info(f"Received complete response from LLM: {assistant_message[:100]}...")

            # 保存助手消息
            conversations[conversation_id].append({"role": "assistant", "content": assistant_message})
            logger.info(f"Saved assistant message for conversation: {conversation_id}")

            # 发送结束信号
            yield f'data: {json.dumps({"id": str(uuid.uuid4()), "content": "", "conversation_id": conversation_id, "is_finished": True})}\n\n'
            logger.info(f"Completed streaming response for conversation: {conversation_id}")
        except Exception as e:
            logger.error(f"Error in streaming chat endpoint: {str(e)}")
            # 发送错误信号
            yield f'data: {json.dumps({"id": str(uuid.uuid4()), "content": f"Error: {str(e)}", "conversation_id": str(uuid.uuid4()), "is_finished": True})}\n\n'

    return StreamingResponse(stream(), media_type="text/event-stream")
