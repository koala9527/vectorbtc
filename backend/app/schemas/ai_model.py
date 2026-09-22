from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class AIModelBase(BaseModel):
    name: str
    provider: Optional[str] = "Custom"
    base_url: str
    model_name: str
    temperature: float = 0.3
    is_active: bool = True
    system_prompt: Optional[str] = None

class AIModelCreate(AIModelBase):
    api_key: str

class AIModelUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    base_url: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    is_active: Optional[bool] = None
    system_prompt: Optional[str] = None
    api_key: Optional[str] = None

class AIModelSchema(AIModelBase):
    id: int
    api_key_masked: str
    total_predictions: int
    correct_predictions: int
    skip_predictions: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
