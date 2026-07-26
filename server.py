import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List

from api.database import execute_query
from api.models.schemas import TradeResponse, EquityResponse
from api.ws_manager import manager, background_tick_broadcaster
import toml

app = FastAPI(title="Goldmine Production Engine API", version="1.0.0")

# Allow CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static dashboard files
app.mount("/static", StaticFiles(directory="api/dashboard"), name="static")

@app.on_event("startup")
async def startup_event():
    # Start the background task to poll the DB and stream via WS
    asyncio.create_task(background_tick_broadcaster())

@app.get("/")
def serve_dashboard():
    return FileResponse("api/dashboard/index.html")

@app.get("/api/trades", response_model=List[TradeResponse])
def get_recent_trades(limit: int = 50):
    trades = execute_query("SELECT * FROM trades ORDER BY close_time DESC LIMIT ?", (limit,))
    return trades

@app.get("/api/equity", response_model=List[EquityResponse])
def get_equity_curve(limit: int = 1000):
    equity = execute_query("SELECT * FROM equity_curve ORDER BY timestamp DESC LIMIT ?", (limit,))
    # Reverse so it's chronological for graphing
    return list(reversed(equity))

@app.get("/api/config")
def get_config():
    try:
        with open("../config/goldmine.toml", "r") as f:
            return toml.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
