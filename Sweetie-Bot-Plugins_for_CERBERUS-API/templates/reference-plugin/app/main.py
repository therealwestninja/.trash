from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="Sweetie Reference Plugin", version="1.0.0")
app.include_router(router)
