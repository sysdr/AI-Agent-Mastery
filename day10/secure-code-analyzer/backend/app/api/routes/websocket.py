"""
WebSocket routes for real-time updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

@router.websocket("/analysis-updates")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and send periodic updates
            await asyncio.sleep(30)
            await manager.send_message(
                json.dumps({
                    "type": "heartbeat",
                    "timestamp": "2024-11-20T12:00:00Z"
                }),
                websocket
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def broadcast_scan_update(scan_data: dict):
    """Broadcast scan update to all connected clients"""
    message = json.dumps({
        "type": "scan_update",
        "data": scan_data
    })
    await manager.broadcast(message)
