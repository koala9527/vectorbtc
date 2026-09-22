from pydantic import BaseModel
from typing import List, Dict, Any

class StatsSchema(BaseModel):
    total_predictions: int
    correct_predictions: int
    skip_predictions: int
    accuracy: float
