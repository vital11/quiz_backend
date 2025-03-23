import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class TokenPayload(BaseModel):
    sub: uuid.UUID | EmailStr | str
    email: EmailStr | None = None
    iat: datetime | None = None
    exp: datetime | None = None
