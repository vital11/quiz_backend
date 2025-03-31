from fastapi import APIRouter

from app.core.config import settings
from app.users.routes import router as users_router
from app.auth.routes import router as auth_router

api_router = APIRouter(
    prefix=settings.api.v1.PREFIX,
)

api_router.include_router(
    router=users_router,
    prefix=settings.api.v1.USERS,
)
api_router.include_router(
    router=auth_router,
    prefix=settings.api.v1.LOGIN,
)
