from fastapi import FastAPI
from .routers.catalog import router as catalog_router

app = FastAPI()

app.include_router(catalog_router)
