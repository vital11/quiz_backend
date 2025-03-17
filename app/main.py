from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.api import api_router
from app.core.config import settings, SERVER_PORT, SERVER_HOST

app = FastAPI(title=settings.APP_NAME)


if settings.CORS_ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        # CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


logger.add("./app/core/info.json", format="{time} {level} {message}", level="INFO",
           rotation="1 MB", compression="zip", serialize=True)


app.include_router(router=api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=SERVER_HOST, port=SERVER_PORT, reload=True)

