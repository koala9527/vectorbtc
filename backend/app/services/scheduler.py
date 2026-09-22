from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.config import settings
from app.database import AsyncSessionLocal
from app.services.binance import binance_service
from app.services.indicators import calculate_all
from app.services.ai_predictor import ai_predictor_service
from app.services.settlement import settle_predictions
from app.models.kline import Kline
from app.models.prediction import Prediction
from app.models.ai_model import AIModel
from sqlalchemy import select
from app.utils.ws_manager import manager
import asyncio
import logging

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def start(self):
        # Align to 5-minute candle marks (00, 05, 10, ...) + 3 seconds
        self.scheduler.add_job(
            self.job_func, 
            'cron', 
            minute='*/5',
            second='3',
            id='main_job',
            max_instances=1,
            coalesce=True,
        )
        self.scheduler.start()
        logger.info("Scheduler started — aligned to 5-minute candle close marks (minute='*/5', second='3')")

    def stop(self):
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")

    async def job_func(self):
        logger.info("=== 5-Minute Candle Scheduler Job Started ===")
        try:
            async with AsyncSessionLocal() as session:
                # 1. Fetch klines from Binance first
                klines_data = await binance_service.get_klines(settings.SYMBOL, settings.INTERVAL, 100)
                if not klines_data:
                    logger.warning("No klines data received from Binance")
                    return
                    
                latest_kline_data = klines_data[-1]
                
                # 2. Settle previous predictions using the latest finalized candle close
                settled_count = await settle_predictions(session, exit_price=latest_kline_data["close_price"])
                if settled_count:
                    logger.info(f"Settled {settled_count} predictions at price {latest_kline_data['close_price']}")
                
                # 3. Calculate technical indicators
                indicators = calculate_all(klines_data)
                
                # 4. Save latest kline to DB
                new_kline = Kline(
                    symbol=settings.SYMBOL,
                    interval=settings.INTERVAL,
                    open_time=latest_kline_data["open_time"],
                    close_time=latest_kline_data["close_time"],
                    open_price=latest_kline_data["open_price"],
                    high_price=latest_kline_data["high_price"],
                    low_price=latest_kline_data["low_price"],
                    close_price=latest_kline_data["close_price"],
                    volume=latest_kline_data["volume"],
                    **indicators
                )
                session.add(new_kline)
                await session.commit()
                await session.refresh(new_kline)
                
                # 5. Get 24hr ticker for market context
                try:
                    ticker_24hr = await binance_service.get_ticker_24hr(settings.SYMBOL)
                except Exception as e:
                    logger.warning(f"Failed to get 24hr ticker: {e}")
                    ticker_24hr = {}
                
                # 6. Get active AI models
                stmt = select(AIModel).where(AIModel.is_active == True)
                result = await session.execute(stmt)
                active_models = result.scalars().all()
                
                if not active_models:
                    logger.info("No active AI models, skipping prediction")
                    return
                
                # 7. Build rich market data for AI
                market_data = {
                    "symbol": settings.SYMBOL,
                    "price": latest_kline_data["close_price"],
                    "volume": latest_kline_data["volume"],
                    "price_change_pct": ticker_24hr.get("priceChangePercent", "N/A"),
                    "volume_24h": ticker_24hr.get("quoteVolume", "N/A"),
                    "high_24h": ticker_24hr.get("highPrice", "N/A"),
                    "low_24h": ticker_24hr.get("lowPrice", "N/A"),
                    "recent_klines": klines_data[-10:],
                }
                
                # 8. Run ALL active AI models concurrently
                logger.info(f"Running predictions with {len(active_models)} models")
                tasks = []
                for model in active_models:
                    tasks.append(ai_predictor_service.predict(model, market_data, indicators))
                    
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 9. Save predictions to DB
                saved_preds = []
                for model, res in zip(active_models, results):
                    if isinstance(res, Exception):
                        logger.error(f"Error predicting with model {model.name} (id={model.id}): {res}")
                        res = {"prediction": "SKIP", "confidence": 0.0, "reasoning": f"Exception: {str(res)}"}
                    
                    pred = Prediction(
                        ai_model_id=model.id,
                        kline_id=new_kline.id,
                        prediction=res.get("prediction", "SKIP"),
                        confidence=res.get("confidence", 0.0),
                        reasoning=res.get("reasoning", ""),
                        entry_price=latest_kline_data["close_price"]
                    )
                    session.add(pred)
                    saved_preds.append((model, pred))
                    logger.info(f"  {model.name}: {res.get('prediction')} (confidence: {res.get('confidence', 0):.2f})")
                    
                await session.commit()
                for model, pred in saved_preds:
                    await session.refresh(pred)
                
                broadcast_preds = [
                    {
                        "id": pred.id,
                        "ai_model_id": model.id,
                        "model_name": model.name,
                        "prediction": pred.prediction,
                        "confidence": pred.confidence,
                        "reasoning": pred.reasoning,
                        "entry_price": pred.entry_price,
                        "settled": False,
                    }
                    for model, pred in saved_preds
                ]
                
                # 10. Broadcast updates via WebSocket
                await manager.broadcast({
                    "type": "prediction",
                    "data": {
                        "kline_id": new_kline.id,
                        "price": new_kline.close_price,
                        "predictions": broadcast_preds,
                    }
                })
                
                # Also broadcast ticker update
                await manager.broadcast({
                    "type": "ticker",
                    "data": {
                        "price": new_kline.close_price,
                        "change24h": ticker_24hr.get("priceChangePercent", "0"),
                        "volume24h": ticker_24hr.get("quoteVolume", "0"),
                    }
                })
                
                logger.info(f"=== Scheduler Job Completed. Price: {new_kline.close_price} ===")
                
        except Exception as e:
            logger.error(f"Scheduler job failed: {e}", exc_info=True)

scheduler_service = SchedulerService()
