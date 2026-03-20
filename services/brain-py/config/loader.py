import os
import yaml
from typing import Dict, Any
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


def load_config() -> Dict[str, Any]:
    """Load and merge configuration from YAML files and environment variables.
    
    Priority: environment variables > environment-specific YAML > base YAML
    """
    # Determine environment
    env = os.getenv("ENVIRONMENT", "dev")
    
    # Load base configuration
    base_config = _load_yaml("config/base.yaml")
    
    # Load environment-specific configuration
    env_config = _load_yaml(f"config/{env}.yaml")
    
    # Merge configurations
    merged_config = _merge_configs(base_config, env_config)
    
    # Override with environment variables
    merged_config = _override_with_env_vars(merged_config)
    
    return merged_config


def _load_yaml(file_path: str) -> Dict[str, Any]:
    """Load YAML file into a dictionary."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"Warning: {file_path} not found, using empty configuration")
        return {}


def _merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two configuration dictionaries."""
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result


def _override_with_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """Override configuration values with environment variables."""
    # API settings
    if os.getenv("API_HOST"):
        config.setdefault("api", {})["host"] = os.getenv("API_HOST")
    if os.getenv("API_PORT"):
        config.setdefault("api", {})["port"] = int(os.getenv("API_PORT"))
    
    # CORS settings
    if os.getenv("CORS_ORIGINS"):
        config.setdefault("cors", {})["origins"] = os.getenv("CORS_ORIGINS").split(",")
    
    # Model settings
    if os.getenv("MODEL_NAME"):
        config.setdefault("model", {})["name"] = os.getenv("MODEL_NAME")
    if os.getenv("MODEL_CACHE_DIR"):
        config.setdefault("model", {})["cache_dir"] = os.getenv("MODEL_CACHE_DIR")
    
    # Qdrant settings
    if os.getenv("QDRANT_HOST"):
        config.setdefault("qdrant", {})["host"] = os.getenv("QDRANT_HOST")
    if os.getenv("QDRANT_PORT"):
        config.setdefault("qdrant", {})["port"] = int(os.getenv("QDRANT_PORT"))
    if os.getenv("QDRANT_COLLECTION"):
        config.setdefault("qdrant", {})["collection"] = os.getenv("QDRANT_COLLECTION")
    
    # Log settings
    if os.getenv("LOG_LEVEL"):
        config.setdefault("log", {})["level"] = os.getenv("LOG_LEVEL")
    
    return config
