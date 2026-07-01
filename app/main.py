import aio_pika
from fastapi import FastAPI
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import engine

app = FastAPI(title=settings.app_name)
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/live", tags=["health"])
async def liveness_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready", tags=["health"])
async def readiness_check() -> dict[str, str | dict[str, str]]:
    checks: dict[str, str] = {}

    try:
        async with engine.connect() as connection:
            await connection.execute(text("select 1"))
        checks["postgres"] = "ok"
    except Exception:
        checks["postgres"] = "unavailable"

    try:
        connection = await aio_pika.connect_robust(
            settings.rabbitmq_url,
            timeout=settings.healthcheck_timeout_seconds,
        )
        await connection.close()
        checks["rabbitmq"] = "ok"
    except Exception:
        checks["rabbitmq"] = "unavailable"

    status = "ok" if all(value == "ok" for value in checks.values()) else "degraded"
    return {"status": status, "checks": checks}
