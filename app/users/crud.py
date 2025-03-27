import uuid

from fastapi import HTTPException, status
from typing import TYPE_CHECKING

from asyncpg.exceptions import UniqueViolationError
from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.database import SessionDep
from app.core.security import hash_password
from app.users.models import User
from app.users.schemas import (
    UserCreate,
    UserPublic,
    UserPrivate,
    UserUpdate,
    UserUpdatePartial,
    UserUpdateMe,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncResult
    from sqlalchemy import ScalarResult
    from sqlalchemy.engine import Result


async def create(session: SessionDep, user_in: UserCreate) -> User:
    user_model = UserPrivate.model_validate(obj=user_in)
    user_model.hashed_password = hash_password(password=user_in.password)
    db_user = User(**user_model.model_dump())
    try:
        session.add(instance=db_user)
        await session.commit()
        await session.refresh(instance=db_user)
    except (UniqueViolationError, IntegrityError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User {db_user.email} already exists in the system",
        )
    logger.info(f"Account {db_user.email} Registration Success")
    return db_user


async def get(session: SessionDep, ident: uuid.UUID) -> User:
    return await session.get(User, ident=ident)


async def find_one_ore_none(session, **filter_by) -> User | None:
    stmt = select(User).filter_by(**filter_by)
    return await session.scalar(statement=stmt)


async def get_all(session: SessionDep, **filter_by) -> list:
    stmt = select(User).filter_by(**filter_by).order_by(User.id)
    return await session.scalars(statement=stmt)


async def update(
    session: SessionDep,
    obj: User,
    obj_update: UserUpdate | UserUpdatePartial | UserUpdateMe,
    partial: bool = False,
) -> User:
    for key, value in obj_update.model_dump(exclude_unset=partial).items():
        setattr(obj, key, value)
    await session.commit()
    await session.refresh(instance=obj)
    return obj


async def delete(session: SessionDep, obj) -> User:
    await session.delete(obj)
    await session.commit()
    session.refresh(obj)
    return obj
