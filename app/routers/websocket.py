from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

router = APIRouter()
active_connections: List[WebSocket] = []

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()   # Garder la connexion ouverte
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)
