from pydantic import BaseModel

class StatsSchema(BaseModel):
    total_predictions: int
    correct_predictions: int
    skip_predictions: int
    accuracy: float
