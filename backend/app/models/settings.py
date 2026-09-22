from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from datetime import datetime

class SystemSetting(Base):
    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String, unique=True, index=True)
    value: Mapped[str] = mapped_column(String)
    
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
