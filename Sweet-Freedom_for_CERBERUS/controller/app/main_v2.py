from fastapi import FastAPI

from .routes_api_v1 import router_v1
from .routes_v2 import router

app = FastAPI(title="Sweet Freedom Controller", version="0.2.0")

app.include_router(router)
app.include_router(router_v1)
