from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class PredictionSchema(BaseModel):
    id: int
    ai_model_id: int
    model_name: Optional[str] = None
    kline_id: int
    prediction: str
    confidence: float
    reasoning: str
    entry_price: float
    exit_price: Optional[float] = None
    actual_direction: Optional[str] = None
    is_correct: Optional[bool] = None
    settled: bool
    predicted_at: datetime
    settled_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
