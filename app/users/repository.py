from loguru import logger
from sqlalchemy.exc import IntegrityError

from app.core.database import async_session
from app.core.repository import BaseRepository
from app.users.models import UserCreate, UserPublic, User


class UserRepository(BaseRepository):
    model = User

    @classmethod
    async def create(cls, payload: UserCreate) -> UserPublic | None:
        async with async_session() as session:
            new_user = User(
                email=payload.email,
                full_name=payload.full_name,
                hashed_password="hashed_password",
            )
            try:
                session.add(new_user)
                await session.commit()
                session.refresh(new_user)

                logger.info(f'Account {new_user.email} created successfully')
                return UserPublic(**new_user.model_dump())

            except IntegrityError as e:
                logger.info(f'Account {new_user.email} already exist')

