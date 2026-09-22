from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.prediction import Prediction
from app.models.ai_model import AIModel
from app.services.binance import binance_service
from app.config import settings
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

async def settle_predictions(
    db_session: AsyncSession,
    exit_price: Optional[float] = None,
    exclude_kline_id: Optional[int] = None
) -> int:
    """Settle all unsettled predictions. Returns count of settled predictions."""
    stmt = select(Prediction).where(Prediction.settled == False)
    if exclude_kline_id:
        stmt = stmt.where(Prediction.kline_id != exclude_kline_id)
        
    result = await db_session.execute(stmt)
    unsettled = result.scalars().all()
    
    if not unsettled:
        return 0
        
    if exit_price is None:
        try:
            exit_price = await binance_service.get_current_price(settings.SYMBOL)
        except Exception as e:
            logger.warning(f"Failed to get current price for settlement: {e}")
            return 0
        
    # Get unique models to update stats
    model_ids = list(set([p.ai_model_id for p in unsettled]))
    models_stmt = select(AIModel).where(AIModel.id.in_(model_ids))
    models_result = await db_session.execute(models_stmt)
    models = {m.id: m for m in models_result.scalars().all()}
    
    settled_count = 0
    for p in unsettled:
        p.exit_price = exit_price
        
        # Determine actual direction
        if exit_price > p.entry_price:
            p.actual_direction = "UP"
        elif exit_price < p.entry_price:
            p.actual_direction = "DOWN"
        else:
            p.actual_direction = "FLAT"
            
        if p.prediction == "SKIP":
            p.is_correct = None
            if p.ai_model_id in models:
                models[p.ai_model_id].skip_predictions += 1
        else:
            if p.actual_direction == "FLAT":
                p.is_correct = False
            else:
                p.is_correct = (p.prediction == p.actual_direction)
            
            if p.ai_model_id in models:
                models[p.ai_model_id].total_predictions += 1
                if p.is_correct:
                    models[p.ai_model_id].correct_predictions += 1
                    
        p.settled = True
        p.settled_at = datetime.utcnow()
        settled_count += 1
        
    await db_session.commit()
    return settled_count
