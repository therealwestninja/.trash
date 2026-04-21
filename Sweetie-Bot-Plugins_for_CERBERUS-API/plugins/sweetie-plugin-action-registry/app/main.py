from fastapi import FastAPI
from app.routes import router
app = FastAPI(title="Sweetie Action Registry")
app.include_router(router)
