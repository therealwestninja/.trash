from fastapi import FastAPI
from app.routes import router
app = FastAPI(title="Sweetie Navigation Core")
app.include_router(router)
