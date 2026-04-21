from fastapi import FastAPI
from app.routes import router
app = FastAPI(title="Sweetie Spatial Memory")
app.include_router(router)
