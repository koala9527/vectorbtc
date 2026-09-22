from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.utils.ws_manager import manager

router = APIRouter(tags=["WebSocket"])

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # keep alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)
