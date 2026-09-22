from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.settings import SystemSetting
from pydantic import BaseModel

router = APIRouter(prefix="/settings", tags=["Settings"])

class SettingItem(BaseModel):
    key: str
    value: str

@router.get("/")
async def get_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SystemSetting))
    return result.scalars().all()

@router.put("/")
async def update_setting(item: SettingItem, db: AsyncSession = Depends(get_db)):
    stmt = select(SystemSetting).where(SystemSetting.key == item.key)
    result = await db.execute(stmt)
    setting = result.scalars().first()
    
    if setting:
        setting.value = item.value
    else:
        setting = SystemSetting(key=item.key, value=item.value)
        db.add(setting)
        
    await db.commit()
    await db.refresh(setting)
    return setting
