from fastapi import FastAPI
from app.routes import router
from app.config import settings
app = FastAPI(title="Sweetie Event Bus", version=settings.plugin_version)
app.include_router(router)
