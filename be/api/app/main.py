from fastapi import FastAPI
from app.services.utils import create_tables
from app.routes import user
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(user.router)

@app.get("/")
async def root():
    return {"message": "tmdt"}