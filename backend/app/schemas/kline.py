from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class KlineSchema(BaseModel):
    id: int
    symbol: str
    interval: str
    open_time: datetime
    close_time: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None
    rsi_14: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    ema_7: Optional[float] = None
    ema_25: Optional[float] = None
    sma_99: Optional[float] = None
    
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
