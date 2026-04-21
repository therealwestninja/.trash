from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="Sweetie Controller", version="0.1.0")
app.include_router(router)
