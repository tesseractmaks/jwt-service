from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from starlette.middleware.cors import CORSMiddleware

from api import router as router_v1
from api import router_token
from core import settings
from core.config import logger
from db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)


@logger.catch
@app.exception_handler(ResponseValidationError)
async def validation_exception_handler(request, exc):
    logger.error(exc)
    return await request_validation_exception_handler(request, exc)


@logger.catch
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return await request_validation_exception_handler(request, exc)


app.include_router(router=router_v1, prefix=settings.api_v1_prefix)
app.include_router(router=router_token)

origins = [
    "portfolio.tesseractmaks.tech",
    "portfolio.tesseractmaks.tech/",
    "https://portfolio.tesseractmaks.tech",
    "/",
    "http://portfolio.tesseractmaks.tech/",
    "http://portfolio.tesseractmaks.tech",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "PUT", "OPTIONS", "HEAD", "PATCH", "POST", "DELETE"],
    allow_headers=["*"],
)
