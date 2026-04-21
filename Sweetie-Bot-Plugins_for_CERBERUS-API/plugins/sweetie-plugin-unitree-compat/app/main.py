from __future__ import annotations
from fastapi import FastAPI
from .routes import router

app = FastAPI(title="Sweetie Plugin - Unitree Compat", version="0.1.0")
app.include_router(router)
