from sqlalchemy import String, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from datetime import datetime

class Kline(Base):
    __tablename__ = "klines"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String, index=True)
    interval: Mapped[str] = mapped_column(String)
    open_time: Mapped[datetime] = mapped_column(DateTime)
    close_time: Mapped[datetime] = mapped_column(DateTime)
    open_price: Mapped[float] = mapped_column(Float)
    high_price: Mapped[float] = mapped_column(Float)
    low_price: Mapped[float] = mapped_column(Float)
    close_price: Mapped[float] = mapped_column(Float)
    volume: Mapped[float] = mapped_column(Float)
    
    macd: Mapped[float | None] = mapped_column(Float, nullable=True)
    macd_signal: Mapped[float | None] = mapped_column(Float, nullable=True)
    macd_hist: Mapped[float | None] = mapped_column(Float, nullable=True)
    rsi_14: Mapped[float | None] = mapped_column(Float, nullable=True)
    bb_upper: Mapped[float | None] = mapped_column(Float, nullable=True)
    bb_middle: Mapped[float | None] = mapped_column(Float, nullable=True)
    bb_lower: Mapped[float | None] = mapped_column(Float, nullable=True)
    ema_7: Mapped[float | None] = mapped_column(Float, nullable=True)
    ema_25: Mapped[float | None] = mapped_column(Float, nullable=True)
    sma_99: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
