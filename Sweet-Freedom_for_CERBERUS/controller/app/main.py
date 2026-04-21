from fastapi import FastAPI

from .routes import router

app = FastAPI(title="Sweet Freedom Controller", version="0.2.0")
app.include_router(router)
