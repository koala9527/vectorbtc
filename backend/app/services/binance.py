import httpx
from datetime import datetime
from app.config import settings
import logging

logger = logging.getLogger(__name__)

FALLBACK_URLS = [
    "https://api.binance.com",
    "https://data-api.binance.vision",
    "https://api1.binance.com",
    "https://api2.binance.com",
    "https://api3.binance.com",
]

class BinanceService:
    def __init__(self):
        self.base_url = settings.BINANCE_BASE_URL

    def _get_client(self, timeout: float = 15.0) -> httpx.AsyncClient:
        kwargs = {"timeout": timeout}
        if settings.HTTP_PROXY:
            kwargs["proxy"] = settings.HTTP_PROXY
        return httpx.AsyncClient(**kwargs)

    async def _request(self, path: str, params: dict = None):
        urls = [self.base_url] + [u for u in FALLBACK_URLS if u != self.base_url]
        last_err = None
        for base in urls:
            url = f"{base}{path}"
            try:
                async with self._get_client() as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    return response.json()
            except Exception as e:
                last_err = e
                logger.warning(f"Binance request to {url} failed: {e}. Trying next fallback...")
        raise last_err

    async def get_klines(self, symbol: str, interval: str, limit: int = 100):
        data = await self._request("/api/v3/klines", {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        })
        
        klines = []
        for item in data:
            open_dt = datetime.fromtimestamp(item[0] / 1000)
            close_dt = datetime.fromtimestamp(item[6] / 1000)
            klines.append({
                "timestamp": item[0],
                "open_time": open_dt,
                "close_time": close_dt,
                "open": float(item[1]),
                "open_price": float(item[1]),
                "high": float(item[2]),
                "high_price": float(item[2]),
                "low": float(item[3]),
                "low_price": float(item[3]),
                "close": float(item[4]),
                "close_price": float(item[4]),
                "volume": float(item[5]),
            })
        return klines

    async def get_ticker_24hr(self, symbol: str):
        return await self._request("/api/v3/ticker/24hr", {"symbol": symbol})

    async def get_current_price(self, symbol: str):
        data = await self._request("/api/v3/ticker/price", {"symbol": symbol})
        return float(data["price"])

binance_service = BinanceService()
