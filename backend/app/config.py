from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import urllib.request

def detect_system_proxy() -> Optional[str]:
    proxies = urllib.request.getproxies()
    return proxies.get("http") or proxies.get("https")

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./vectorbtc.db"
    BINANCE_BASE_URL: str = "https://api.binance.com"
    SYMBOL: str = "BTCUSDT"
    INTERVAL: str = "5m"
    SCHEDULER_INTERVAL_MINUTES: int = 5
    SECRET_KEY: str = "supersecretkey1234567890123456789012345678"
    HTTP_PROXY: Optional[str] = detect_system_proxy()

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
