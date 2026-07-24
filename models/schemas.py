from pydantic import BaseModel, Field
from typing import Optional, List

class TradeResponse(BaseModel):
    id: int
    open_time: int
    close_time: int
    direction: str
    entry_price: float
    exit_price: float
    qty: float
    pnl_usd: float
    fees: float
    sl: float
    tp: float
    conviction: float
    rules_mask: int
    duration_ticks: int

class EquityResponse(BaseModel):
    timestamp: int
    equity: float
    drawdown_pct: float
    trade_count: int

class ControlAction(BaseModel):
    action: str = Field(..., description="Action to perform: 'close_all', 'halt_engine', 'resume_engine'")
    
class ConfigUpdate(BaseModel):
    section: str
    key: str
    value: float
