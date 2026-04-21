from fastapi import FastAPI
from app.routes import router
app = FastAPI(title="Sweetie Gait Library")
app.include_router(router)
