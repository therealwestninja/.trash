from fastapi import FastAPI

from .state_manager import state_manager

app = FastAPI(title="Sweet Freedom Controller Contract", version="0.2.0")


@app.get("/state")
def get_state():
    return state_manager.get_state()


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/ready")
def ready():
    return {"status": "ready"}
