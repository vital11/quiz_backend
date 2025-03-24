import uuid

from fastapi import APIRouter, status, HTTPException
from pydantic import EmailStr

from app.core.database import SessionDep
from app.core.dependencies import CurrentUser
from app.users.models import UserCreate, UserPublic, UserRegister
from app.users.repository import UserRepository

router = APIRouter(tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate) -> UserPublic:
    """Create new user, available for superuser."""
    pass


@router.get("", response_model=list[UserPublic], status_code=status.HTTP_200_OK)
async def read_users() -> list[UserPublic]:
    """Retrieve users."""
    return await UserRepository.get_all()


@router.get("/{user_id}", response_model=UserPublic, status_code=status.HTTP_200_OK)
async def read_user(user_id: uuid.UUID) -> UserPublic:
    """Get a specific user by id."""
    return await UserRepository.find_by_id(obj_id=user_id)


@router.get("/email/{user_email}", response_model=UserPublic, status_code=status.HTTP_200_OK)
async def read_user_by_email(user_email: EmailStr) -> UserPublic:
    """Get a specific user by email."""
    return await UserRepository.find_one_ore_none(email=user_email)


@router.put("/{user_uuid}", status_code=status.HTTP_200_OK)
async def update_user(session: SessionDep, user_uuid: str):
    pass


@router.delete("/{user_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(session: SessionDep, user_uuid: str):
    pass


@router.post("/signup", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserRegister) -> UserPublic:
    """Create new user without the need to be logged in."""
    user = await UserRepository.find_one_ore_none(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The user with this email already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    return await UserRepository.create(user_create=user_create)


@router.get("/me", response_model=UserPublic, status_code=status.HTTP_200_OK)
async def read_me(current_user: CurrentUser) -> UserPublic:
    return current_user
