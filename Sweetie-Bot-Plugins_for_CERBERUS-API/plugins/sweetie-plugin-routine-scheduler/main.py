from fastapi import FastAPI
from routes import router

app = FastAPI(title="Sweetie Routine Scheduler")
app.include_router(router)
