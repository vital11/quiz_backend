from typing import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.api import api_router
from app.core.config import settings
from app.core.database import db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    db.dispose()


app = FastAPI(
    lifespan=lifespan,
    title=settings.APP_NAME,
)


if settings.cors.ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


logger.add(
    "./app/core/info.json",
    format="{time} {level} {message}",
    level="INFO",
    rotation="1 MB",
    compression="zip",
    serialize=True,
)


app.include_router(router=api_router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.run.SERVER_HOST,
        port=settings.run.SERVER_PORT,
        reload=True,
    )
