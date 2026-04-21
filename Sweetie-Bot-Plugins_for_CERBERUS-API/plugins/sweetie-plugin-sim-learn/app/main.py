from fastapi import FastAPI
from app.routes import router
from app.config import settings

app = FastAPI(
    title="Sweetie Simulation and Learning Plugin",
    version=settings.plugin_version,
    description="Simulation logging, replay, and dataset-capture contract for CERBERUS-compatible plugins.",
)

app.include_router(router)
