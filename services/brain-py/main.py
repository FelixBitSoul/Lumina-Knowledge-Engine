import os
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import uvicorn

app = FastAPI(title="Lumina Brain API")

# Schema for incoming document ingestion requests
class Document(BaseModel):
    url: str
    title: str
    content: str

# Initialize LLM with OpenAI-compatible API (e.g., DeepSeek)
# Using environment variables for sensitive credentials
llm = ChatOpenAI(
    model='deepseek-chat', 
    openai_api_key=os.getenv("DEEPSEEK_API_KEY", "your_placeholder_key"), 
    openai_api_base='https://api.deepseek.com'
)

@app.post("/ingest")
async def ingest_document(doc: Document):
    """
    Receives raw text, generates a summary using LLM, 
    and prepares data for vector storage.
    """
    prompt_template = ChatPromptTemplate.from_template(
        "You are a professional knowledge assistant. "
        "Summarize the following content in less than 50 words:\n"
        "Title: {title}\nContent: {content}"
    )
    
    # Modern LangChain Expression Language (LCEL) chain
    chain = prompt_template | llm
    
    try:
        response = chain.invoke({"title": doc.title, "content": doc.content})
        print(f"Successfully processed document from: {doc.url}")
        return {
            "status": "success", 
            "summary": response.content,
            "metadata": {"url": doc.url, "title": doc.title}
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Run the server with Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)