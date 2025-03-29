from fastapi import APIRouter, HTTPException, status

from app.core.database import SessionDep
from app.core.dependencies import CurrentUser, UserByIdDep
from app.users import crud
from app.users.schemas import (
    UserCreate,
    UserPublic,
    UserRegister,
    UserUpdate,
    UserUpdatePartial,
)

router = APIRouter(tags=["Users"])


@router.get("", response_model=list[UserPublic], status_code=status.HTTP_200_OK)
async def read_users(
    session: SessionDep,
) -> list[UserPublic]:
    """Retrieve users"""
    return await crud.get_all(session=session)


@router.post("/signup", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserRegister,
    session: SessionDep,
) -> UserPublic:
    """Create new user without the need to be logged in"""
    user = await crud.find_one_ore_none(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The user {user.email} already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    return await crud.create(session=session, user_in=user_create)


@router.get("/{user_id}", response_model=UserPublic, status_code=status.HTTP_200_OK)
async def read_user(
    user: UserByIdDep,
) -> UserPublic:
    """Get a specific user by id"""
    return user


@router.put("/{user_id}", response_model=UserPublic, status_code=status.HTTP_200_OK)
async def update_user(
    user_update: UserUpdate,
    session: SessionDep,
    user: UserByIdDep,
) -> UserPublic:
    """Update a specific user by id"""
    return await crud.update(session=session, user=user, user_update=user_update)


@router.patch("/{user_id}", response_model=UserPublic, status_code=status.HTTP_200_OK)
async def update_user_partial(
    user_update: UserUpdatePartial,
    session: SessionDep,
    user: UserByIdDep,
) -> UserPublic:
    """Update a specific user by id"""
    return await crud.update(
        session=session, user=user, user_update=user_update, partial=True
    )


@router.delete("/{user_id}", response_model=UserPublic, status_code=status.HTTP_200_OK)
async def delete_user(
    session: SessionDep,
    user: UserByIdDep,
) -> UserPublic:
    """Delete a specific user by id and return deleted"""
    return await crud.delete(session=session, user=user)


@router.get("/me", response_model=UserPublic, status_code=status.HTTP_200_OK)
async def read_me(
    current_user: CurrentUser,
) -> UserPublic:
    """Get current user"""
    return current_user
