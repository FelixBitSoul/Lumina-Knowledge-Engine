import openai
import os
from typing import List, Optional

# 配置API
api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE", "")

# 配置OpenAI客户端
client = openai.OpenAI(
    api_key=api_key,
    base_url=api_base if api_base else None
)

def generate_response(message: str, context: List[str] = None, conversation_id: str = None) -> str:
    """生成大模型响应"""
    # 构建提示词
    prompt = build_prompt(message, context)

    # 调用API
    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo"),
        messages=[
            {"role": "system", "content": "You are a helpful assistant for the Lumina Knowledge Engine."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )

    return response.choices[0].message.content

def build_prompt(message: str, context: List[str] = None) -> str:
    """构建提示词"""
    prompt = f"User query: {message}\n"

    if context:
        prompt += "\nRelevant context:\n"
        for item in context:
            prompt += f"- {item}\n"

    prompt += "\nPlease provide a helpful response based on the context above."

    return prompt

def generate_streaming_response(message: str, context: List[str] = None, conversation_id: str = None):
    """生成流式响应"""
    # 构建提示词
    prompt = build_prompt(message, context)

    # 调用API的流式接口
    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo"),
        messages=[
            {"role": "system", "content": "You are a helpful assistant for the Lumina Knowledge Engine."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000,
        stream=True
    )

    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
