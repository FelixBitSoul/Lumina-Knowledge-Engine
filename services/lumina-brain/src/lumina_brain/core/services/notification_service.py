import logging
import json
import asyncio
from typing import Dict, Any, Optional, Callable
import redis
import redis.asyncio as redis_async
from lumina_brain.config.settings import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for handling Redis Pub/Sub notifications"""
    
    def __init__(self):
        # Sync client for Celery tasks
        self.sync_client: Optional[redis.Redis] = None
        # Async client for WebSocket
        self.async_client: Optional[redis_async.Redis] = None
        self.pubsub: Optional[redis_async.client.PubSub] = None
        self.message_handler: Optional[Callable] = None
        logger.info("[NOTIFICATION] Notification service initialized")
    
    def get_sync_client(self) -> redis.Redis:
        """Get synchronous Redis client"""
        if not self.sync_client:
            self.sync_client = redis.Redis(
                host=settings.redis.host,
                port=settings.redis.port,
                db=settings.redis.db
            )
        return self.sync_client
    
    async def get_async_client(self) -> redis_async.Redis:
        """Get asynchronous Redis client"""
        if not self.async_client:
            self.async_client = redis_async.Redis(
                host=settings.redis.host,
                port=settings.redis.port,
                db=settings.redis.db
            )
        return self.async_client
    
    def publish_document_completion(self, file_id: str, metadata: dict = None):
        """Publish document completion notification"""
        message = {
            "file_id": file_id,
            "status": "completed",
            "timestamp": self._get_timestamp(),
            **(metadata or {})
        }
        self._publish_sync("document_updates", message)
    
    def publish_document_failure(self, file_id: str, error: str):
        """Publish document failure notification"""
        message = {
            "file_id": file_id,
            "status": "failed",
            "error": error,
            "timestamp": self._get_timestamp()
        }
        self._publish_sync("document_updates", message)
    
    def publish_document_progress(self, file_id: str, progress_data: dict):
        """Publish document progress notification"""
        message = {
            "file_id": file_id,
            "status": "processing",
            "timestamp": self._get_timestamp(),
            **progress_data
        }
        self._publish_sync("document_updates", message)
    
    async def publish_notification(self, file_id: str, status: str, **kwargs):
        """Publish generic notification"""
        message = {
            "file_id": file_id,
            "status": status,
            "timestamp": self._get_timestamp(),
            **kwargs
        }
        await self._publish_async("document_updates", message)
    
    def _publish_sync(self, channel: str, message: Dict[str, Any]):
        """Publish message synchronously"""
        try:
            client = self.get_sync_client()
            client.publish(channel, json.dumps(message))
            logger.debug(f"[NOTIFICATION] Published message to {channel}: {message}")
        except Exception as e:
            logger.error(f"[NOTIFICATION] Failed to publish message: {str(e)}", exc_info=True)
    
    async def _publish_async(self, channel: str, message: Dict[str, Any]):
        """Publish message asynchronously"""
        try:
            client = await self.get_async_client()
            await client.publish(channel, json.dumps(message))
            logger.debug(f"[NOTIFICATION] Published message to {channel}: {message}")
        except Exception as e:
            logger.error(f"[NOTIFICATION] Failed to publish message: {str(e)}", exc_info=True)
    
    async def start_listener(self, message_handler: Callable):
        """Start Redis Pub/Sub listener"""
        self.message_handler = message_handler
        try:
            client = await self.get_async_client()
            self.pubsub = client.pubsub()
            await self.pubsub.subscribe("document_updates")
            logger.info("[NOTIFICATION] Started Redis Pub/Sub listener")
            asyncio.create_task(self._listen_for_messages())
        except Exception as e:
            logger.error(f"[NOTIFICATION] Failed to start listener: {str(e)}", exc_info=True)
    
    async def _listen_for_messages(self):
        """Listen for Redis messages"""
        if not self.pubsub:
            return
        
        try:
            async for message in self.pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        if self.message_handler:
                            await self.message_handler(data)
                    except Exception as e:
                        logger.error(f"[NOTIFICATION] Error processing message: {str(e)}", exc_info=True)
        except Exception as e:
            logger.error(f"[NOTIFICATION] Error in listener: {str(e)}", exc_info=True)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    async def close(self):
        """Close all connections"""
        if self.sync_client:
            self.sync_client.close()
        if self.async_client:
            await self.async_client.close()
        if self.pubsub:
            await self.pubsub.close()
        logger.info("[NOTIFICATION] Notification service closed")


# Create global instance
notification_service = NotificationService()
