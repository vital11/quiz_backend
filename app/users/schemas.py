import uuid
from typing import Annotated

from annotated_types import MaxLen, MinLen
from pydantic import EmailStr, BaseModel, ConfigDict


class UserBase(BaseModel):
    """Shared properties"""

    model_config = ConfigDict(from_attributes=True)

    email: Annotated[EmailStr, MaxLen(50)]
    full_name: Annotated[str | None, MaxLen(50)] = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    """Properties to receive via API on creation"""

    password: Annotated[str, MinLen(2), MaxLen(50)]


class UserRegister(BaseModel):
    email: Annotated[EmailStr, MaxLen(50)]
    password: Annotated[str, MinLen(2), MaxLen(50)]
    full_name: Annotated[str | None, MaxLen(50)] = None


class UserUpdate(UserBase):
    """Properties to receive via API on update, all are mandatory"""

    is_active: bool
    is_superuser: bool


class UserUpdatePartial(UserBase):
    """Properties to receive via API on update, all are optional"""

    email: Annotated[EmailStr | None, MaxLen(50)] = None
    full_name: Annotated[str | None, MaxLen(50)] = None


class UserUpdateMe(BaseModel):
    """Properties to receive via API on update, all are mandatory"""

    email: Annotated[EmailStr, MaxLen(50)]
    full_name: Annotated[str, MaxLen(50)]


class UserUpdateMePartial(BaseModel):
    """Properties to receive via API on update, all are optional"""

    email: Annotated[EmailStr | None, MaxLen(50)] = None
    full_name: Annotated[str | None, MaxLen(50)] = None


class UpdatePassword(BaseModel):
    password: Annotated[str, MinLen(2), MaxLen(50)]
    new_password: Annotated[str, MinLen(2), MaxLen(50)]


class UserPrivate(UserBase):
    """Additional properties stored in DB"""

    id: uuid.UUID | None = None
    hashed_password: bytes | None = None


class UserPublic(UserBase):
    """Properties to return via API, id is always required"""

    id: uuid.UUID | str


class UsersPublic(BaseModel):
    data: list[UserPublic]
    count: int
