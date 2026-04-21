from fastapi import FastAPI
from app.routes import router
from app.config import settings

app = FastAPI(
    title="Sweetie World Model Plugin",
    version=settings.plugin_version,
    description="Shared object memory for CERBERUS-compatible plugins and controller features.",
)

app.include_router(router)
