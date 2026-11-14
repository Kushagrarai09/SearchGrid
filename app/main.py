from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text
from app.core.config import settings
from app.db.session import engine, Base
from app.api.routes import router
from app.services.search import ensure_index
from app.services.cache import redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensure_index()
    yield

app = FastAPI(title=settings.app_name, version="1.0.0",
              description="Distributed search and indexing platform", lifespan=lifespan)
app.include_router(router, prefix=settings.api_prefix, tags=["SearchGrid"])

@app.get("/health")
def health():
    checks = {}
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["postgres"] = "ok"
    except Exception as exc:
        checks["postgres"] = f"error: {exc.__class__.__name__}"
    try:
        redis_client.ping()
        checks["redis"] = "ok"
    except Exception as exc:
        checks["redis"] = f"error: {exc.__class__.__name__}"
    try:
        from app.services.search import es
        es.ping()
        checks["elasticsearch"] = "ok"
    except Exception as exc:
        checks["elasticsearch"] = f"error: {exc.__class__.__name__}"
    return {"status": "ok" if all(v == "ok" for v in checks.values()) else "degraded", "services": checks}
