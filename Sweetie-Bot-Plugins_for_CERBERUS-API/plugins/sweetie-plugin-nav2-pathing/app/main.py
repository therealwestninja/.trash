from fastapi import FastAPI
from app.routes import router
from app.config import settings

app = FastAPI(
    title="Sweetie Nav2 Pathing Plugin",
    version=settings.plugin_version,
    description="Controller-friendly pathing contract for CERBERUS with a Nav2-ready upgrade path.",
)

app.include_router(router)
