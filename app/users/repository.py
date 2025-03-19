from loguru import logger

from app.core.database import async_session
from app.core.repository import BaseRepository
from app.core.security import get_password_hash
from app.users.models import UserCreate, UserPublic, User


class UserRepository(BaseRepository):
    model = User

    @classmethod
    async def create(cls, *, user_create: UserCreate) -> UserPublic:
        async with async_session() as session:
            db_obj = User.model_validate(
                user_create,
                update={"hashed_password": get_password_hash(user_create.password)}
            )
            session.add(db_obj)
            await session.commit()
            session.refresh(db_obj)

            new_user = UserPublic(**db_obj.model_dump())
            logger.info(f'Account {new_user.email} Registration Success')
            return new_user
