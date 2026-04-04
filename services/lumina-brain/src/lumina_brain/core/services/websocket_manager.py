import logging
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio
import redis.asyncio as redis
from lumina_brain.config.settings import settings

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        """Initialize WebSocket connection manager"""
        # room: {file_id} -> set of websocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.redis_client = None
        self.pubsub = None
        logger.info("[WS MANAGER] WebSocket manager initialized")

    async def connect(self, websocket: WebSocket, room: str):
        """Connect to specified room

        Args:
            websocket: WebSocket connection
            room: Room name (file_id)
        """
        logger.info(f"[WS MANAGER] Accepting WebSocket connection for room: {room}")
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = set()
            logger.info(f"[WS MANAGER] Created new room: {room}")
        self.active_connections[room].add(websocket)
        logger.info(f"[WS MANAGER] WebSocket connected to room: {room}, total connections: {len(self.active_connections[room])}")

        # Send connection confirmation
        await self.send_personal_message({
            "file_id": room,
            "status": "connected",
            "message": "WebSocket connected successfully"
        }, websocket)
        logger.info(f"[WS MANAGER] Sent connection confirmation to room: {room}")

    async def disconnect(self, websocket: WebSocket, room: str):
        """Disconnect from room

        Args:
            websocket: WebSocket connection
            room: Room name (file_id)
        """
        logger.info(f"[WS MANAGER] Disconnecting WebSocket from room: {room}")
        if room in self.active_connections:
            self.active_connections[room].discard(websocket)
            logger.info(f"[WS MANAGER] WebSocket removed from room: {room}, remaining connections: {len(self.active_connections[room])}")
            if not self.active_connections[room]:
                del self.active_connections[room]
                logger.info(f"[WS MANAGER] Room {room} is empty, removed")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send personal message to specific connection

        Args:
            message: Message to send
            websocket: WebSocket connection
        """
        try:
            await websocket.send_json(message)
            logger.debug(f"[WS MANAGER] Personal message sent: {message}")
        except Exception as e:
            logger.error(f"[WS MANAGER] Failed to send personal message: {str(e)}")

    async def broadcast(self, message: dict, room: str):
        """Broadcast message to all connections in room

        Args:
            message: Message to broadcast
            room: Room name (file_id)
        """
        logger.info(f"[WS MANAGER] Broadcasting message to room: {room}, message: {message}")
        if room in self.active_connections:
            disconnected = []
            connections = list(self.active_connections[room])
            logger.info(f"[WS MANAGER] Broadcasting to {len(connections)} connections in room: {room}")

            for connection in connections:
                try:
                    await connection.send_json(message)
                    logger.debug(f"[WS MANAGER] Message sent to connection in room: {room}")
                except Exception as e:
                    logger.error(f"[WS MANAGER] Failed to send message to connection: {str(e)}")
                    disconnected.append(connection)

            # Clean up disconnected connections
            if disconnected:
                logger.info(f"[WS MANAGER] Cleaning up {len(disconnected)} disconnected connections from room: {room}")
                for connection in disconnected:
                    await self.disconnect(connection, room)
        else:
            logger.warning(f"[WS MANAGER] Room not found for broadcast: {room}")

    async def init_redis_pubsub(self):
        """Initialize Redis Pub/Sub listener"""
        logger.info(f"[WS MANAGER] Initializing Redis Pub/Sub listener...")
        try:
            self.redis_client = redis.Redis(
                host=settings.redis.host,
                port=settings.redis.port,
                db=settings.redis.db
            )
            self.pubsub = self.redis_client.pubsub()
            await self.pubsub.subscribe("document_updates")
            logger.info(f"[WS MANAGER] Redis Pub/Sub subscribed to channel: document_updates")

            # Start listening task
            asyncio.create_task(self.listen_for_notifications())
            logger.info(f"[WS MANAGER] Redis Pub/Sub listener started")
        except Exception as e:
            logger.error(f"[WS MANAGER] Failed to initialize Redis Pub/Sub: {str(e)}", exc_info=True)

    async def listen_for_notifications(self):
        """Listen for Redis Pub/Sub notifications"""
        logger.info(f"[WS MANAGER] Starting to listen for Redis notifications...")
        try:
            async for message in self.pubsub.listen():
                logger.debug(f"[WS MANAGER] Received Redis message: {message}")
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        file_id = data.get('file_id')
                        logger.info(f"[WS MANAGER] Processing notification for file_id: {file_id}, status: {data.get('status')}")
                        if file_id:
                            await self.broadcast(data, file_id)
                    except Exception as e:
                        logger.error(f"[WS MANAGER] Error processing pubsub message: {str(e)}", exc_info=True)
        except Exception as e:
            logger.error(f"[WS MANAGER] Error in Redis listener: {str(e)}", exc_info=True)

    async def publish_notification(self, file_id: str, status: str, **kwargs):
        """Publish notification to Redis

        Args:
            file_id: Document ID
            status: Notification status
            **kwargs: Additional metadata
        """
        if self.redis_client:
            message = {
                "file_id": file_id,
                "status": status,
                **kwargs
            }
            logger.info(f"[WS MANAGER] Publishing notification to Redis: {message}")
            try:
                await self.redis_client.publish(
                    "document_updates",
                    json.dumps(message)
                )
                logger.info(f"[WS MANAGER] Notification published successfully")
            except Exception as e:
                logger.error(f"[WS MANAGER] Failed to publish notification: {str(e)}", exc_info=True)


# Create global WebSocket manager instance
websocket_manager = ConnectionManager()
logger.info("[WS MANAGER] Global WebSocket manager instance created")
