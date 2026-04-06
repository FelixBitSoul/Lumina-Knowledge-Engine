import redis
import json
import hashlib
from typing import Optional, Any
from lumina_brain.config.settings import settings


class CacheService:
    """Service for handling caching operations"""

    def __init__(self):
        # 检查 RedisSettings 是否有 password 属性
        redis_kwargs = {
            'host': settings.redis.host,
            'port': settings.redis.port,
            'db': settings.redis.db
        }
        # 只有当 RedisSettings 有 password 属性时才添加
        if hasattr(settings.redis, 'password') and settings.redis.password:
            redis_kwargs['password'] = settings.redis.password
        
        self.redis_client = redis.Redis(**redis_kwargs)
        self.default_ttl = 3600  # 1 hour

    def generate_cache_key(self, query: str, collection: str, filters: Optional[dict] = None) -> str:
        """Generate a cache key based on the query, collection, and filters"""
        key_components = [query, collection]
        if filters:
            # Sort filters to ensure consistent key generation
            sorted_filters = sorted(filters.items())
            key_components.extend([f"{k}:{v}" for k, v in sorted_filters])
        key_string = "|".join(key_components)
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Error getting from cache: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in the cache with an optional TTL"""
        try:
            ttl = ttl or self.default_ttl
            self.redis_client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            print(f"Error setting in cache: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete a value from the cache"""
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Error deleting from cache: {e}")
            return False


    def clear_collection_cache(self, collection: str) -> bool:
        """Clear all cache entries for a specific collection"""
        try:
            # This is a simplified approach - in production, you might want to use Redis SCAN
            # or a more sophisticated key naming scheme to efficiently clear collection-specific cache
            keys = self.redis_client.keys(f"*{collection}*")
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            print(f"Error clearing collection cache: {e}")
            return False


# Create global Cache service instance
cache_service = CacheService()
