from fastapi import APIRouter
from app.services.binance import binance_service
from app.config import settings

router = APIRouter(prefix="/market", tags=["Market"])

@router.get("/ticker")
async def get_ticker():
    return await binance_service.get_ticker_24hr(settings.SYMBOL)

@router.get("/klines")
async def get_klines(limit: int = 100):
    return await binance_service.get_klines(settings.SYMBOL, settings.INTERVAL, limit)

@router.get("/indicators")
async def get_indicators():
    from app.services.indicators import calculate_all
    klines = await binance_service.get_klines(settings.SYMBOL, settings.INTERVAL, 100)
    return calculate_all(klines)
