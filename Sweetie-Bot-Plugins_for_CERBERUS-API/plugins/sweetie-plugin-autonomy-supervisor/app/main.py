from fastapi import FastAPI
from app.routes import router
app = FastAPI(title="Sweetie Autonomy Supervisor")
app.include_router(router)
