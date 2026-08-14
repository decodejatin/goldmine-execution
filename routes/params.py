import struct
import mmap
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

class RLParams(BaseModel):
    version_id: int
    risk_pct: float
    tp_multiplier: float = Field(..., gt=0.0)
    sl_multiplier: float = Field(..., gt=0.0)
    conv_threshold: float
    p_profitable_gate_bps: int
    regime_id: int

@router.post("/api/v1/update_parameters")
def update_parameters(params: RLParams):
    shm_path = "/dev/shm/goldmine_param_shm"
    if not os.path.exists(shm_path):
        raise HTTPException(status_code=500, detail="SHM file not found")
        
    try:
        with open(shm_path, "r+b") as f:
            mm = mmap.mmap(f.fileno(), 0)
            
            # DynamicParams uses alignas(64) for each field
            mm.seek(0)
            mm.write(struct.pack("Q", params.version_id))
            
            mm.seek(64)
            mm.write(struct.pack("d", params.risk_pct))
            
            mm.seek(128)
            mm.write(struct.pack("d", params.tp_multiplier))
            
            mm.seek(192)
            mm.write(struct.pack("d", params.sl_multiplier))
            
            mm.seek(256)
            mm.write(struct.pack("d", params.conv_threshold))
            
            mm.seek(320)
            mm.write(struct.pack("I", params.p_profitable_gate_bps))
            
            mm.seek(384)
            mm.write(struct.pack("B", params.regime_id))
            
            mm.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return {"status": "success", "version_id": params.version_id}
