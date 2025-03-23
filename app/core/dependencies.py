from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from app.auth.models import TokenPayload
from app.core.security import decode_access_token
from app.core.database import SessionDep
from app.users.models import UserPublic, User


reusable_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login/access-token"
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
    return payload


async def get_current_user(
        session: SessionDep,
        payload: Annotated[TokenPayload, Depends(verify_token)]
) -> UserPublic:
    user = await session.get(User, ident=payload.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
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
