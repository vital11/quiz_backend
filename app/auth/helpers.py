import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
import bcrypt

from app.auth.schemas import TokenPayload, TokenType
from app.core.config import settings
from app.users.schemas import UserPublic


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(
        password=password.encode(),
        salt=bcrypt.gensalt(),
    )


def _encode_jwt(
    payload: TokenPayload,
    private_key: str = settings.jwt.PRIVATE_KEY_PATH.read_text(),
    algorithm: str = settings.jwt.ALGORITHM,
    expire_minutes: int = settings.jwt.ACCESS_TOKEN_EXPIRE_MINUTES,
    expire_delta: timedelta | None = None,
) -> str:
    now = datetime.now(tz=timezone.utc)
    if expire_delta:
        expire = now + expire_delta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    payload.iat = now
    payload.exp = expire
    payload.sub = str(payload.sub)
    payload.jti = str(uuid.uuid4())
    return jwt.encode(
        payload=payload.model_dump(exclude_unset=True),
        key=private_key,
        algorithm=algorithm,
    )


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.jwt.PUBLIC_KEY_PATH.read_text(),
    algorithm: str = settings.jwt.ALGORITHM,
) -> Any:
    return jwt.decode(
        token,
        key=public_key,
        algorithms=[algorithm],
    )


def _create_token(
    payload: TokenPayload,
    token_type: TokenType,
    expire_minutes: int = settings.jwt.ACCESS_TOKEN_EXPIRE_MINUTES,
    expire_delta: timedelta | None = None,
) -> str:
    payload.type = token_type.value
    return _encode_jwt(
        payload=payload,
        expire_minutes=expire_minutes,
        expire_delta=expire_delta,
    )


def create_access_token(user: UserPublic) -> str:
    payload = TokenPayload(
        sub=user.id,
        email=user.email,
    )
    return _create_token(
        token_type=TokenType.ACCESS,
        payload=payload,
        expire_minutes=settings.jwt.ACCESS_TOKEN_EXPIRE_MINUTES,
    )


def create_refresh_token(user: UserPublic) -> str:
    payload = TokenPayload(
        sub=user.id,
    )
    return _create_token(
        token_type=TokenType.REFRESH,
        payload=payload,
        expire_delta=timedelta(days=settings.jwt.REFRESH_TOKEN_EXPIRE_DAYS),
    )
