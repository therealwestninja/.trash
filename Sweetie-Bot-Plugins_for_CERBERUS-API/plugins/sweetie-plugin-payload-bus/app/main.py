from fastapi import FastAPI
from app.routes import router
from app.config import settings

app = FastAPI(
    title="Sweetie Payload Bus Plugin",
    version=settings.plugin_version,
    description="Payload and module registry for CERBERUS-compatible plugins.",
)

app.include_router(router)
