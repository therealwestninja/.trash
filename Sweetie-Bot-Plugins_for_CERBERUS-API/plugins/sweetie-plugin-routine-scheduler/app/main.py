from fastapi import FastAPI
from app.routes import router
app = FastAPI(title="Sweetie Routine Scheduler")
app.include_router(router)
