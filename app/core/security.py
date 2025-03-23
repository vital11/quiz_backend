from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from app.auth.models import TokenPayload
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def encode_access_token(
        payload: TokenPayload,
        private_key: str = settings.jwt.PRIVATE_KEY_PATH.read_text(),
        algorithm: str = settings.jwt.ALGORITHM,
        expire_minutes: int = settings.jwt.ACCESS_TOKEN_EXPIRE_MINUTES,
        expire_delta: timedelta | None = None,
) -> str:
    to_encode = payload.model_dump(exclude_unset=True)
    now = datetime.now(tz=timezone.utc)
    if expire_delta:
        expire = now + expire_delta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        sub=str(to_encode.get("sub")),
        iat=now,
        exp=expire,
    )
    return jwt.encode(
        to_encode,
        key=private_key,
        algorithm=algorithm,
    )


def decode_access_token(
        token: str | bytes,
        public_key: str = settings.jwt.PUBLIC_KEY_PATH.read_text(),
        algorithm: str = settings.jwt.ALGORITHM,
) -> Any:
    return jwt.decode(
        token,
        key=public_key,
        algorithms=[algorithm],
    )
