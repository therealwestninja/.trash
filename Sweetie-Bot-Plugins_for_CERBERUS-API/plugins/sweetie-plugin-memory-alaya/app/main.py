from fastapi import FastAPI
from app.routes import router
from app.config import settings
app = FastAPI(title="Sweetie Memory Alaya", version=settings.plugin_version)
app.include_router(router)
