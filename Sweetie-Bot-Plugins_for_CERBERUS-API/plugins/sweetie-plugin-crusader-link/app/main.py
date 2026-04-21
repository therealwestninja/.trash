from fastapi import FastAPI
from app.routes import router
app = FastAPI(title="Sweetie Crusader Link")
app.include_router(router)
