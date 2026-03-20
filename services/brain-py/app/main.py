import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.router import api_router
from config.settings import settings

print(f"CORS Origins: {settings.cors.origins}")

app = FastAPI(title="Lumina Brain - Vector Service")

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.origins,           # Allows specific origins
    allow_credentials=True,                        # Allows cookies to be included in requests
    allow_methods=["*"],                           # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],                           # Allows all headers
)

# Include API router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api.host, port=settings.api.port)
