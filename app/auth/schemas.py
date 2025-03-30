import uuid
from datetime import datetime
import enum

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class TokenType(enum.Enum):
    ACCESS: str = "access"
    REFRESH: str = "refresh"


class TokenPayload(BaseModel):
    sub: uuid.UUID | str
    email: EmailStr | str | None = None
    iat: datetime | None = None
    exp: datetime | None = None
    type: TokenType | None = None
