import os
import yaml
from dotenv import load_dotenv
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """Load configuration from files and environment variables."""
    # Load environment variables from .env file
    load_dotenv()
    config = {}

    # Load base configuration
    base_config_path = os.path.join(os.path.dirname(__file__), "base.yaml")
    if os.path.exists(base_config_path):
        with open(base_config_path, "r", encoding="utf-8") as f:
            config.update(yaml.safe_load(f))

    # Load environment-specific configuration
    env = os.getenv("ENVIRONMENT", "dev")
    env_config_path = os.path.join(os.path.dirname(__file__), f"{env}.yaml")
    if os.path.exists(env_config_path):
        with open(env_config_path, "r", encoding="utf-8") as f:
            env_config = yaml.safe_load(f)
            # Update config with environment-specific values
            _deep_update(config, env_config)

    # Override with environment variables
    _override_with_env(config)

    return config

def _deep_update(target: Dict[str, Any], source: Dict[str, Any]) -> None:
    """Deep update target dictionary with source dictionary."""
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _deep_update(target[key], value)
        else:
            target[key] = value

def _override_with_env(config: Dict[str, Any]) -> None:
    """Override configuration with environment variables."""
    # Qdrant settings
    if os.getenv("QDRANT_HOST"):
        if "qdrant" not in config:
            config["qdrant"] = {}
        config["qdrant"]["host"] = os.getenv("QDRANT_HOST")

    if os.getenv("QDRANT_PORT"):
        if "qdrant" not in config:
            config["qdrant"] = {}
        config["qdrant"]["port"] = int(os.getenv("QDRANT_PORT"))

    if os.getenv("QDRANT_COLLECTION"):
        if "qdrant" not in config:
            config["qdrant"] = {}
        config["qdrant"]["collection"] = os.getenv("QDRANT_COLLECTION")

    # Model settings
    if os.getenv("MODEL_NAME"):
        if "model" not in config:
            config["model"] = {}
        config["model"]["name"] = os.getenv("MODEL_NAME")

    if os.getenv("MODEL_CACHE_DIR"):
        if "model" not in config:
            config["model"] = {}
        config["model"]["cache_dir"] = os.getenv("MODEL_CACHE_DIR")

    # API settings
    if os.getenv("API_HOST"):
        if "api" not in config:
            config["api"] = {}
        config["api"]["host"] = os.getenv("API_HOST")

    if os.getenv("API_PORT"):
        if "api" not in config:
            config["api"] = {}
        config["api"]["port"] = int(os.getenv("API_PORT"))

    # CORS settings
    if os.getenv("CORS_ORIGINS"):
        if "cors" not in config:
            config["cors"] = {}
        config["cors"]["origins"] = os.getenv("CORS_ORIGINS").split(",")

    # Log settings
    if os.getenv("LOG_LEVEL"):
        if "log" not in config:
            config["log"] = {}
        config["log"]["level"] = os.getenv("LOG_LEVEL")
