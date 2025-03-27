import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, Path, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from app.auth.models import TokenPayload
from app.core.config import settings
from app.core.security import decode_access_token
from app.core.database import SessionDep
from app.users import crud
from app.users.schemas import UserPublic
from app.users.models import User


reusable_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/login/access-token"
)

TokenDep = Annotated[str, Depends(reusable_oauth2_scheme)]


def verify_token(token: TokenDep) -> TokenPayload:
    try:
        token_data = decode_access_token(token=token)
        payload = TokenPayload(**token_data)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    if payload.exp < datetime.now(tz=timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access token expired"
        )
    return payload


async def get_current_user(
    session: SessionDep, payload: Annotated[TokenPayload, Depends(verify_token)]
) -> UserPublic:
    user = await session.get(User, ident=payload.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )
    return UserPublic(**user.model_dump())


CurrentUser = Annotated[UserPublic, Depends(get_current_user)]


def get_current_superuser(current_user: CurrentUser) -> UserPublic:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


CurrentSuperUser = Annotated[UserPublic, Depends(get_current_superuser)]


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


UserDep = Annotated[UserPublic, Depends(get_user_by_id)]
