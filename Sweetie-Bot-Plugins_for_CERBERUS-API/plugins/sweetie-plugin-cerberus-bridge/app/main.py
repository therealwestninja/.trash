
from fastapi import FastAPI
app = FastAPI()

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/execute")
def execute(data: dict):
    return {"plugin":"ok","data":data}
