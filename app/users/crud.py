import uuid

from fastapi import HTTPException, status
from typing import Union

from asyncpg.exceptions import UniqueViolationError
from loguru import logger
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import undefer

from app.core.security import hash_password
from app.users.models import User
from app.users.schemas import (
    UserCreate,
    UserPublic,
    UserPrivate,
    UserUpdate,
    UserUpdatePartial,
    UserUpdateMe,
    UserUpdateMePartial,
)


async def create(
    session: AsyncSession,
    user_in: UserCreate,
) -> UserPublic:
    user_model = UserPrivate.model_validate(obj=user_in)
    user_model.hashed_password = hash_password(password=user_in.password)
    user = User(**user_model.model_dump())
    try:
        session.add(instance=user)
        await session.commit()
        await session.refresh(instance=user)
    except (UniqueViolationError, IntegrityError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User {user.email} already exists in the system",
        )
    logger.info(f"Account {user.email} Registration Success")
    return UserPublic(**user.__dict__)


async def get(
    session: AsyncSession,
    ident: uuid.UUID,
) -> User | None:
    return await session.get(User, ident=ident)


async def find_one_ore_none(
    session: AsyncSession,
    **filter_by,
) -> User | None:
    stmt = select(User).filter_by(**filter_by)
    return await session.scalar(statement=stmt)


async def get_all(
    session: AsyncSession,
    **filter_by,
) -> list[UserPublic]:
    stmt = select(User).filter_by(**filter_by).order_by(User.id)
    users = await session.scalars(statement=stmt)
    return [UserPublic(**user.__dict__) for user in users]


async def update(
    session: AsyncSession,
    user: User,
    user_update: Union[
        UserUpdate, UserUpdatePartial, UserUpdateMe, UserUpdateMePartial
    ],
    partial: bool = False,
) -> UserPublic:
    for key, value in user_update.model_dump(exclude_unset=partial).items():
        setattr(user, key, value)
    await session.commit()
    await session.refresh(instance=user)
    return UserPublic(**user.__dict__)


async def delete(
    session: AsyncSession,
    user: User,
) -> UserPublic:
    await session.delete(user)
    await session.commit()
    await session.refresh(user)
    return UserPublic(**user.__dict__)


async def get_user_by_email(
    session: AsyncSession,
    email: EmailStr | str,
    undefer_password: bool = False,
) -> User | None:
    stmt = (
        select(User).where(User.email == email).options(undefer(User.hashed_password))
        if undefer_password
        else select(User).where(User.email == email)
    )
    session_user = await session.scalar(statement=stmt)
    return session_user
