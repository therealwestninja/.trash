from fastapi import FastAPI
from app.routes import router
app = FastAPI(title="Sweetie Social Bonding")
app.include_router(router)
