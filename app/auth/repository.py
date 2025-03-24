from pydantic import EmailStr

from app.core.repository import BaseRepository
from app.core.security import verify_password
from app.users.models import UserPublic, User


class AuthRepository(BaseRepository):
    model = User

    @classmethod
    async def authenticate(cls, email: EmailStr | str, password: str) -> UserPublic | None:
        db_user = await cls.find_one_ore_none(email=email)
        if not db_user and not verify_password(password, db_user.hashed_password):
            return None
        return UserPublic(**db_user.model_dump())