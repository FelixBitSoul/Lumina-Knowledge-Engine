from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from lumina_brain.core.services.websocket_manager import websocket_manager

router = APIRouter()


@router.websocket("/ws/{file_id}")
async def websocket_endpoint(websocket: WebSocket, file_id: str):
    """
    WebSocket endpoint for real-time document processing notifications
    
    - Frontend should connect to this endpoint after uploading a file
    - Connection will join a room named after the file_id
    - When document processing is complete, real-time notifications will be sent
    
    Args:
        websocket: WebSocket connection
        file_id: Document ID (based on content hash)
    """
    await websocket_manager.connect(websocket, file_id)
    
    # Send connection success message
    await websocket_manager.send_personal_message(
        {
            "status": "connected",
            "message": f"Connected to room {file_id}",
            "file_id": file_id
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
        await websocket_manager.disconnect(websocket, file_id)
