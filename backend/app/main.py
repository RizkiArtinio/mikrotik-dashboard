import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings
from app.core.logging_conf import configure_logging
from app.db.init_db import run_startup_seed
from app.db.session import AsyncSessionLocal
from app.scheduler.scheduler import shutdown_scheduler, start_scheduler
from app.services.router_connection_pool import connection_pool
from app.services.telegram_bot import telegram_bot
from app.websocket.ws_routes import router as ws_router

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionLocal() as db:
        await run_startup_seed(db)

    start_scheduler()
    telegram_bot.start()
    logger.info("MikroTik dashboard backend started")
    try:
        yield
    finally:
        await telegram_bot.stop()
        shutdown_scheduler()
        connection_pool.disconnect_all()
        logger.info("MikroTik dashboard backend stopped")


app = FastAPI(
    title="MikroTik RouterOS Monitoring & Management Dashboard",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(ws_router)


@app.get("/api/healthz", tags=["health"])
async def healthz() -> dict:
    return {"status": "ok"}
