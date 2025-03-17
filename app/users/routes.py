from fastapi import APIRouter, status

from app.core.database import SessionDep
from app.users.models import UserCreate, UserPublic
from app.users.repository import UserRepository

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_user(session: SessionDep, payload: UserCreate):
    user_repo = UserRepository(session=session)
    return await user_repo.create(payload=payload)


@router.get("/{user_uuid}", status_code=status.HTTP_200_OK)
async def read_user(session: SessionDep, user_uuid: str):
    pass


@router.put("/{user_uuid}", status_code=status.HTTP_200_OK)
async def update_user(session: SessionDep, user_uuid: str):
    pass


@router.delete("/{user_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(session: SessionDep, user_uuid: str):
    pass


@router.get("", status_code=status.HTTP_200_OK)
async def read_users(session: SessionDep):
    pass

