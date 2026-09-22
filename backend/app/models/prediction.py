from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from datetime import datetime

class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ai_model_id: Mapped[int] = mapped_column(ForeignKey("ai_models.id"))
    kline_id: Mapped[int] = mapped_column(ForeignKey("klines.id"))
    
    prediction: Mapped[str] = mapped_column(String) # UP, DOWN, SKIP
    confidence: Mapped[float] = mapped_column(Float)
    reasoning: Mapped[str] = mapped_column(String)
    
    entry_price: Mapped[float] = mapped_column(Float)
    exit_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_direction: Mapped[str | None] = mapped_column(String, nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    settled: Mapped[bool] = mapped_column(Boolean, default=False)
    
    predicted_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    settled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
