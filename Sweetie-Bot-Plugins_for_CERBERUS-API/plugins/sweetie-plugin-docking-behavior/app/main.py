from fastapi import FastAPI
from app.routes import router
app = FastAPI(title="Sweetie Docking Behavior")
app.include_router(router)
