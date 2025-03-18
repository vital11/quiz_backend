import uuid

from fastapi import APIRouter, status
from pydantic import EmailStr

from app.core.database import SessionDep
from app.users.models import UserCreate, UserPublic
from app.users.repository import UserRepository

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate) -> UserPublic | None:
    return await UserRepository.create(payload=payload)


@router.get("", response_model=list[UserPublic], status_code=status.HTTP_200_OK)
async def read_users() -> list[UserPublic]:
    return await UserRepository.get_all()


@router.get("/{user_id}", response_model=UserPublic, status_code=status.HTTP_200_OK)
async def read_user(user_id: uuid.UUID) -> UserPublic:
    return await UserRepository.find_by_id(model_id=user_id)


@router.get("/email/{user_email}", response_model=UserPublic, status_code=status.HTTP_200_OK)
async def read_user_by_email(user_email: EmailStr) -> UserPublic:
    return await UserRepository.find_one_ore_none(email=user_email)


@router.put("/{user_uuid}", status_code=status.HTTP_200_OK)
async def update_user(session: SessionDep, user_uuid: str):
    pass


@router.delete("/{user_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(session: SessionDep, user_uuid: str):
    pass

