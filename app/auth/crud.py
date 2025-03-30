from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import TokenPayload
from app.auth.validation import validate_password
from app.users import crud
from app.users.models import User
from app.users.schemas import UserPublic


async def authenticate(
    session: AsyncSession,
    email: EmailStr | str,
    password: str,
) -> UserPublic | None:
    """Session user getter from Form data"""
    db_user = await crud.get_user_by_email(
        session=session,
        email=email,
        undefer_password=True,
    )
    if not db_user:
        return None
    if not validate_password(password, db_user.hashed_password):
        return None
    return UserPublic(**db_user.__dict__)


async def authenticate_by_token_sub(
    session: AsyncSession,
    payload: TokenPayload,
) -> User:
    """Current user getter from Token 'sub'"""
    user_id = payload.sub
    db_user = await crud.get(session=session, ident=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return db_user
