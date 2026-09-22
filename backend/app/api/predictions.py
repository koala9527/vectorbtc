from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.models.prediction import Prediction
from app.models.ai_model import AIModel
from app.schemas.prediction import PredictionSchema
from app.services.scheduler import scheduler_service
from typing import List, Optional

router = APIRouter(prefix="/predictions", tags=["Predictions"])

async def _attach_model_names(predictions: List[Prediction], db: AsyncSession) -> List[dict]:
    if not predictions:
        return []
    model_ids = list(set([p.ai_model_id for p in predictions]))
    res = await db.execute(select(AIModel).where(AIModel.id.in_(model_ids)))
    name_map = {m.id: m.name for m in res.scalars().all()}
    
    out = []
    for p in predictions:
        d = {c.name: getattr(p, c.name) for c in p.__table__.columns}
        d["model_name"] = name_map.get(p.ai_model_id, f"Model #{p.ai_model_id}")
        out.append(PredictionSchema(**d))
    return out

@router.get("", response_model=List[PredictionSchema])
@router.get("/", response_model=List[PredictionSchema], include_in_schema=False)
async def get_predictions(
    ai_model_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Prediction)
        .join(AIModel, Prediction.ai_model_id == AIModel.id)
        .where(AIModel.is_deleted == False)
        .order_by(desc(Prediction.predicted_at))
        .limit(limit)
        .offset(offset)
    )
    if ai_model_id:
        stmt = stmt.where(Prediction.ai_model_id == ai_model_id)
    
    result = await db.execute(stmt)
    preds = result.scalars().all()
    return await _attach_model_names(preds, db)

@router.get("/latest", response_model=List[PredictionSchema])
async def get_latest(limit: int = 10, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Prediction)
        .join(AIModel, Prediction.ai_model_id == AIModel.id)
        .where(AIModel.is_deleted == False)
        .order_by(desc(Prediction.predicted_at))
        .limit(limit)
    )
    result = await db.execute(stmt)
    preds = result.scalars().all()
    return await _attach_model_names(preds, db)

@router.post("/trigger")
async def trigger_cycle(background_tasks: BackgroundTasks):
    """Manually triggers a 5-minute prediction and settlement cycle immediately."""
    background_tasks.add_task(scheduler_service.job_func)
    return {"status": "success", "message": "5-Minute prediction & settlement cycle triggered"}
