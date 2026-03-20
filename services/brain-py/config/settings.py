from pydantic_settings import BaseSettings
from typing import List
from .loader import load_config


class APISettings(BaseSettings):
    """API configuration settings"""
    host: str = "0.0.0.0"
    port: int = 8000


class CORSSettings(BaseSettings):
    """CORS configuration settings"""
    origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


class ModelSettings(BaseSettings):
    """Model configuration settings"""
    name: str = "all-MiniLM-L6-v2"
    cache_dir: str = "/app/models"


class QdrantSettings(BaseSettings):
    """Qdrant configuration settings"""
    host: str = "localhost"
    port: int = 6333
    collection: str = "knowledge_base"


class LogSettings(BaseSettings):
    """Log configuration settings"""
    level: str = "info"


class Settings(BaseSettings):
    """Application configuration settings"""
    ENVIRONMENT: str = "dev"
    api: APISettings = APISettings()
    cors: CORSSettings = CORSSettings()
    model: ModelSettings = ModelSettings()
    qdrant: QdrantSettings = QdrantSettings()
    log: LogSettings = LogSettings()

    class Config:
        env_file = ".env"
        case_sensitive = True


def get_settings() -> Settings:
    """Get application settings, loaded from files and environment variables."""
    # Load configuration from files and environment variables
    config_dict = load_config()
    
    # Create settings object from the loaded configuration
    return Settings(
        api=APISettings(**config_dict.get("api", {})),
        cors=CORSSettings(**config_dict.get("cors", {})),
        model=ModelSettings(**config_dict.get("model", {})),
        qdrant=QdrantSettings(**config_dict.get("qdrant", {})),
        log=LogSettings(**config_dict.get("log", {})),
    )


# Create global settings instance
settings = get_settings()
