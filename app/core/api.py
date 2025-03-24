from fastapi import APIRouter

from app.users.routes import router as users_router
from app.auth.routes import router as auth_router

api_router = APIRouter()
api_router.include_router(users_router, prefix="/users")
api_router.include_router(auth_router, prefix="/login",)
