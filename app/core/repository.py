from sqlalchemy.ext.asyncio import AsyncResult
from sqlmodel import select

from app.core.database import async_session


class BaseRepository:
    model = None

    @classmethod
    async def find_by_id(cls, model_id):
        async with async_session() as session:
            statement = select(cls.model).filter_by(id=model_id)
            result: AsyncResult = await session.execute(statement=statement)
            return result.scalar_one_or_none()


    @classmethod
    async def find_one_ore_none(cls, **filter_by):
        async with async_session() as session:
            statement = select(cls.model).filter_by(**filter_by)
            result: AsyncResult = await session.execute(statement=statement)
            return result.scalar_one_or_none()


    @classmethod
    async def get_all(cls, **filter_by):
        async with async_session() as session:
            statement = select(cls.model).filter_by(**filter_by)
            result: AsyncResult = await session.execute(statement=statement)
            return result.scalars().all()

