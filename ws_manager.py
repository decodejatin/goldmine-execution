from fastapi import WebSocket
from typing import List
import json
import asyncio

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WS Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"WS Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        if not self.active_connections:
            return
            
        data = json.dumps(message)
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(data)
            except Exception:
                dead_connections.append(connection)
                
        for dc in dead_connections:
            self.disconnect(dc)

# Global manager instance
manager = WebSocketManager()

async def background_tick_broadcaster():
    """
    Simulates polling the database or IPC for new ticks/equity updates
    and broadcasts them to connected WebSocket clients.
    """
    from api.database import execute_query
    last_trade_id = 0
    last_equity_ts = 0
    
    while True:
        try:
            # Check for new trades
            trades = execute_query("SELECT * FROM trades WHERE id > ? ORDER BY id ASC LIMIT 5", (last_trade_id,))
            for t in trades:
                last_trade_id = max(last_trade_id, t['id'])
                await manager.broadcast({"type": "trade", "data": t})
                
            # Check for new equity points
            eq = execute_query("SELECT * FROM equity_curve WHERE timestamp > ? ORDER BY timestamp ASC LIMIT 5", (last_equity_ts,))
            for e in eq:
                last_equity_ts = max(last_equity_ts, e['timestamp'])
                await manager.broadcast({"type": "equity", "data": e})
                
        except Exception as e:
            print(f"Broadcast error: {e}")
            
        await asyncio.sleep(1.0) # Poll every 1 second
