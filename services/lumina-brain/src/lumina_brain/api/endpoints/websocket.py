from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from lumina_brain.core.services.websocket_manager import websocket_manager

router = APIRouter()


@router.websocket("/ws/collection/{collection}")
async def websocket_collection_endpoint(websocket: WebSocket, collection: str):
    """
    WebSocket endpoint for real-time document processing notifications by collection
    
    - Frontend should connect to this endpoint to receive updates for all files in a collection
    - Connection will join a room named after the collection
    - When any document in the collection is processed, real-time notifications will be sent
    
    Args:
        websocket: WebSocket connection
        collection: Collection name
    """
    await websocket_manager.connect(websocket, f"collection:{collection}")
    
    # Send connection success message
    await websocket_manager.send_personal_message(
        {
            "status": "connected",
            "message": f"Connected to collection room {collection}",
            "collection": collection
        },
        websocket
    )
    
    try:
        while True:
            # Keep connection alive, receive frontend messages if needed
            data = await websocket.receive_text()
            # Handle frontend messages, such as heartbeats
            await websocket_manager.send_personal_message(
                {
                    "status": "ack",
                    "message": "Message received",
                    "data": data
                },
                websocket
            )
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket, f"collection:{collection}")
