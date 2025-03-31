import uuid
from datetime import datetime, timezone
from typing import Annotated

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from app.auth.schemas import TokenPayload, TokenType
from app.core.config import settings
from app.auth.helpers import decode_jwt


reusable_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api.PREFIX}{settings.api.v1.PREFIX}{settings.api.v1.LOGIN}/access-token"
)


def validate_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )


def validate_token(
    token: Annotated[str, Depends(reusable_oauth2_scheme)],
) -> TokenPayload:
    try:
        token_data = decode_jwt(token=token)
        payload = TokenPayload(**token_data)
        payload.sub = uuid.UUID(payload.sub)
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


def validate_token_type(
    payload: TokenPayload,
    token_type: TokenType,
) -> bool:
    current_token_type = payload.type
    if current_token_type != token_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type {current_token_type.value!r}, {token_type.value!r} expected",
        )
    return True
