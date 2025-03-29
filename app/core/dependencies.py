import uuid
from datetime import datetime, timezone
from typing import Annotated, TYPE_CHECKING

from fastapi import Depends, Path, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from app.auth.schemas import TokenPayload, TokenType
from app.core.config import settings
from app.core.security import decode_jwt
from app.core.database import SessionDep
from app.users.models import User
from app.users import crud


reusable_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/login/access-token"
)


def verify_token(
    token: Annotated[str, Depends(reusable_oauth2_scheme)],
) -> TokenPayload:
    try:
        token_data = decode_jwt(token=token)
        payload = TokenPayload(**token_data)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    if payload.exp < datetime.now(tz=timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access token expired",
        )
    return payload


async def get_current_user(
    session: SessionDep,
    payload: Annotated[TokenPayload, Depends(verify_token)],
) -> User:
    token_type = payload.type
    if token_type != TokenType.ACCESS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type {token_type.value!r}, {TokenType.ACCESS.value!r} expected",
        )
    user = await crud.get(session=session, ident=payload.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_superuser(
    current_user: CurrentUser,
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


CurrentSuperUser = Annotated[User, Depends(get_current_superuser)]


async def get_user_by_id(
    user_id: Annotated[uuid.UUID, Path],
    session: SessionDep,
) -> User:
    user = await crud.get(session=session, ident=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    return user


UserByIdDep = Annotated[User, Depends(get_user_by_id)]
