from fastapi import FastAPI
from app.routes import router
app = FastAPI(title="Sweetie Peer Transport Adapter")
app.include_router(router)
