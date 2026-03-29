import os
from openai import OpenAI

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

def build_prompt(message: str, context: list = None) -> str:
    """构建提示词"""
    prompt = "You are a helpful assistant for the Lumina Knowledge Engine. "
    prompt += "Based on the following context, answer the user's question. "
    prompt += "If you don't know the answer, say you don't know. "
    prompt += "Keep your answer concise and relevant.\n\n"
    
    if context:
        prompt += "Context:\n"
        for i, doc in enumerate(context, 1):
            prompt += f"{i}. {doc[:500]}...\n"
        prompt += "\n"
    
    prompt += f"Question: {message}\n"
    prompt += "Answer:"
    return prompt

def generate_response(message: str, context: list = None, conversation_id: str = None) -> str:
    """生成响应"""
    prompt = build_prompt(message, context)
    
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

def generate_streaming_response(message: str, context: list = None, conversation_id: str = None):
    """生成流式响应"""
    prompt = build_prompt(message, context)
    
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