import uuid
from datetime import datetime
import enum
from typing import Annotated

from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, EmailStr


class Message(BaseModel):
    message: str


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class TokenType(enum.Enum):
    ACCESS: str = "access"
    REFRESH: str = "refresh"
    RESET: str = "reset"


class TokenPayload(BaseModel):
    sub: uuid.UUID | str
    jti: uuid.UUID | str | None = None
    email: EmailStr | str | None = None
    iat: datetime | None = None
    exp: datetime | None = None
    type: TokenType | None = None


class NewPassword(BaseModel):
    token: str
    new_password: Annotated[str, MinLen(2), MaxLen(50)]
