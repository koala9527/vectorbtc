from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.services.scheduler import scheduler_service
from contextlib import asynccontextmanager

from app.api import market, predictions, ai_models, stats, settings, ws

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    scheduler_service.start()
    yield
    # Shutdown
    scheduler_service.stop()

app = FastAPI(title="VectorBTC API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market.router, prefix="/api")
app.include_router(predictions.router, prefix="/api")
app.include_router(ai_models.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(ws.router)

@app.get("/")
def read_root():
    return {"message": "VectorBTC API is running"}
