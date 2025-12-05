from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.utils import create_tables
from app.routes import user
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)

@app.get("/")
async def root():
    return {"message": "tmdt"}