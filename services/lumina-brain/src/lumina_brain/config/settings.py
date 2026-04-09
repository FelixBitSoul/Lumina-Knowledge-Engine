from pydantic_settings import BaseSettings
from typing import List
from .loader import load_config


class APISettings(BaseSettings):
    """API configuration settings"""
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


class CORSSettings(BaseSettings):
    """CORS configuration settings"""
    origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

        @classmethod
        def parse_env_var(cls, field_name, raw_val):
            if field_name == "origins" and isinstance(raw_val, str):
                # Split comma-separated string into list
                return [origin.strip() for origin in raw_val.split(",")]
            return raw_val


class ModelSettings(BaseSettings):
    """Model configuration settings"""
    name: str = "all-MiniLM-L6-v2"
    cache_dir: str = "./models"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


class QdrantSettings(BaseSettings):
    """Qdrant configuration settings"""
    host: str = "qdrant"
    port: int = 6333
    collection: str = "knowledge_base"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


class LogSettings(BaseSettings):
    """Log configuration settings"""
    level: str = "info"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


class RedisSettings(BaseSettings):
    """Redis configuration settings"""
    host: str = "redis"
    port: int = 6379
    db: int = 0

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


class MinIOSettings(BaseSettings):
    """MinIO configuration settings"""
    endpoint: str = "minio:9000"
    access_key: str = "minioadmin"
    secret_key: str = "minioadmin"
    bucket: str = "lumina-documents"
    secure: bool = False
    presigned_expiry: int = 600

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


class CelerySettings(BaseSettings):
    """Celery configuration settings"""
    broker_url: str = "redis://redis:6379/0"
    result_backend: str = "redis://redis:6379/1"
    worker_concurrency: int = 4

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


class PostgresSettings(BaseSettings):
    """PostgreSQL configuration settings"""
    host: str = "postgres"
    port: int = 5432
    db: str = "lumina"
    user: str = "lumina"
    password: str = "lumina123"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


class UploadSettings(BaseSettings):
    """Upload configuration settings"""
    allowed_extensions: List[str] = ["pdf", "md", "markdown", "txt", "text"]
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    default_collection: str = "knowledge_base"
    chunk_size: int = 600
    chunk_overlap: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

        @classmethod
        def parse_env_var(cls, field_name, raw_val):
            if field_name == "allowed_extensions" and isinstance(raw_val, str):
                # Split comma-separated string into list
                return [ext.strip() for ext in raw_val.split(",")]
            elif field_name == "max_file_size" and isinstance(raw_val, str):
                # Parse string to int
                return int(raw_val)
            return raw_val


class Settings(BaseSettings):
    """Application configuration settings"""
    ENVIRONMENT: str = "dev"
    api: APISettings = APISettings()
    cors: CORSSettings = CORSSettings()
    model: ModelSettings = ModelSettings()
    qdrant: QdrantSettings = QdrantSettings()
    log: LogSettings = LogSettings()
    redis: RedisSettings = RedisSettings()
    minio: MinIOSettings = MinIOSettings()
    celery: CelerySettings = CelerySettings()
    postgres: PostgresSettings = PostgresSettings()
    upload: UploadSettings = UploadSettings()

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


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
        redis=RedisSettings(**config_dict.get("redis", {})),
        minio=MinIOSettings(**config_dict.get("minio", {})),
        celery=CelerySettings(**config_dict.get("celery", {})),
        postgres=PostgresSettings(**config_dict.get("postgres", {})),
        upload=UploadSettings(**config_dict.get("upload", {})),
    )


# Create global settings instance
settings = get_settings()
