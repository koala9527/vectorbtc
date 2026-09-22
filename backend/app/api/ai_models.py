from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.ai_model import AIModel
from app.schemas.ai_model import AIModelSchema, AIModelCreate, AIModelUpdate
from app.services.ai_predictor import get_cipher, decrypt_api_key, ai_predictor_service
from typing import List

router = APIRouter(prefix="/ai-models", tags=["AI Models"])

def mask_api_key(key: str) -> str:
    if len(key) <= 4:
        return "****"
    return "*" * (len(key) - 4) + key[-4:]

@router.get("/", response_model=List[AIModelSchema])
async def get_models(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AIModel))
    models = result.scalars().all()
    
    # We map ORM to schema manually to mask the api key
    out = []
    for m in models:
        raw_key = decrypt_api_key(m.api_key_encrypted)
        d = {c.name: getattr(m, c.name) for c in m.__table__.columns}
        d["api_key_masked"] = mask_api_key(raw_key)
        out.append(AIModelSchema(**d))
    return out

@router.post("/", response_model=AIModelSchema)
async def create_model(item: AIModelCreate, db: AsyncSession = Depends(get_db)):
    cipher = get_cipher()
    enc_key = cipher.encrypt(item.api_key.encode()).decode()
    
    model = AIModel(
        name=item.name,
        provider=item.provider,
        base_url=item.base_url,
        api_key_encrypted=enc_key,
        model_name=item.model_name,
        temperature=item.temperature,
        is_active=item.is_active,
        system_prompt=item.system_prompt
    )
    db.add(model)
    await db.commit()
    await db.refresh(model)
    
    d = {c.name: getattr(model, c.name) for c in model.__table__.columns}
    d["api_key_masked"] = mask_api_key(item.api_key)
    return AIModelSchema(**d)

@router.put("/{model_id}", response_model=AIModelSchema)
async def update_model(model_id: int, item: AIModelUpdate, db: AsyncSession = Depends(get_db)):
    model = await db.get(AIModel, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
        
    update_data = item.model_dump(exclude_unset=True)
    new_key = update_data.pop("api_key", None)
    if new_key and new_key.strip():
        cipher = get_cipher()
        model.api_key_encrypted = cipher.encrypt(new_key.strip().encode()).decode()
        
    for k, v in update_data.items():
        setattr(model, k, v)
        
    await db.commit()
    await db.refresh(model)
    
    d = {c.name: getattr(model, c.name) for c in model.__table__.columns}
    d["api_key_masked"] = mask_api_key(decrypt_api_key(model.api_key_encrypted))
    return AIModelSchema(**d)

@router.delete("/{model_id}")
async def delete_model(model_id: int, db: AsyncSession = Depends(get_db)):
    model = await db.get(AIModel, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    await db.delete(model)
    await db.commit()
    return {"status": "deleted"}

@router.post("/{model_id}/test")
async def test_model(model_id: int, db: AsyncSession = Depends(get_db)):
    model = await db.get(AIModel, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
        
    market_data = {"symbol": "BTCUSDT", "price": 85000.0, "volume": 100.0}
    indicators = {"rsi_14": 52.0, "macd": 15.0, "macd_signal": 10.0, "macd_hist": 5.0}
    
    res = await ai_predictor_service.predict(model, market_data, indicators)
    reasoning = res.get("reasoning", "")
    if res.get("prediction") == "SKIP" and any(err in reasoning.lower() for err in ["error", "timed out", "failed", "exception"]):
        raise HTTPException(status_code=400, detail=reasoning)
    return res
