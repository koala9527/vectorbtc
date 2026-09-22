from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.ai_model import AIModel
from app.models.prediction import Prediction
from datetime import datetime, timedelta

router = APIRouter(prefix="/stats", tags=["Statistics"])

@router.get("/overview")
async def get_overview(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AIModel).where(AIModel.is_deleted == False))
    models = result.scalars().all()
    
    total = sum(m.total_predictions for m in models)
    correct = sum(m.correct_predictions for m in models)
    skips = sum(m.skip_predictions for m in models)
    wrong = total - correct
    effective = total
    
    win_rate = (correct / effective * 100) if effective > 0 else 0.0
    
    return {
        "total_predictions": total,
        "correct_predictions": correct,
        "wrong_predictions": wrong,
        "skip_predictions": skips,
        "win_rate": round(win_rate, 2),
    }

@router.get("/by-model")
async def get_by_model(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AIModel).where(AIModel.is_deleted == False))
    models = result.scalars().all()
    stats = []
    for m in models:
        effective = m.total_predictions
        win_rate = (m.correct_predictions / effective * 100) if effective > 0 else 0.0
        stats.append({
            "model_id": m.id,
            "name": m.name,
            "is_active": m.is_active,
            "total_predictions": m.total_predictions,
            "correct_predictions": m.correct_predictions,
            "wrong_predictions": m.total_predictions - m.correct_predictions,
            "skip_predictions": m.skip_predictions,
            "win_rate": round(win_rate, 2),
        })
    stats.sort(key=lambda x: x["win_rate"], reverse=True)
    return stats

@router.get("/history")
async def get_history(days: int = Query(default=7, ge=1, le=90), db: AsyncSession = Depends(get_db)):
    """Get daily win rate trend for the last N days for non-deleted models."""
    since = datetime.utcnow() - timedelta(days=days)
    
    stmt = (
        select(Prediction)
        .join(AIModel, Prediction.ai_model_id == AIModel.id)
        .where(AIModel.is_deleted == False)
        .where(Prediction.settled == True)
        .where(Prediction.prediction != "SKIP")
        .where(Prediction.settled_at >= since)
        .order_by(Prediction.settled_at)
    )
    result = await db.execute(stmt)
    predictions = result.scalars().all()
    
    daily_stats = {}
    for p in predictions:
        if p.settled_at is None:
            continue
        date_key = p.settled_at.strftime("%Y-%m-%d")
        if date_key not in daily_stats:
            daily_stats[date_key] = {"total": 0, "correct": 0}
        daily_stats[date_key]["total"] += 1
        if p.is_correct:
            daily_stats[date_key]["correct"] += 1
    
    history = []
    for date_key in sorted(daily_stats.keys()):
        s = daily_stats[date_key]
        win_rate = (s["correct"] / s["total"] * 100) if s["total"] > 0 else 0.0
        history.append({
            "date": date_key,
            "total": s["total"],
            "correct": s["correct"],
            "win_rate": round(win_rate, 2),
        })
    
    return history
