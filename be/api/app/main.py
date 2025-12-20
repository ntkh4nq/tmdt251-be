from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.services.utils import create_tables
from app.routes import user, order, catalog, engagement, cart, address, discount
from contextlib import asynccontextmanager
import traceback


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
app.include_router(order.router)
app.include_router(catalog.router)
app.include_router(engagement.router)
app.include_router(cart.router)
app.include_router(address.router)
app.include_router(discount.router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = f"Global Exception: {str(exc)}\n{traceback.format_exc()}"
    print(error_msg)  # Show in terminal
    with open("error.log", "a") as f:
        f.write(error_msg + "\n" + "-" * 20 + "\n")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "debug": str(exc)},
    )


@app.get("/")
async def root():
    return {"message": "tmdt"}
