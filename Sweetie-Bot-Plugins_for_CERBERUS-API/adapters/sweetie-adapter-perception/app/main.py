from fastapi import FastAPI
from app.routes import router
app = FastAPI(title="Sweetie Perception Adapter")
app.include_router(router)
