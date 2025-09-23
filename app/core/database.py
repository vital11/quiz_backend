from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr

from app.core.config import settings
from app.helpers.case_converter import camel_case_to_snake_case


class Database:
    def __init__(
        self,
        url: str,
        echo: bool = False,
        echo_pool: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ) -> None:
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        await self.engine.dispose()

    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Session getter"""
        async with self.session_factory() as session:
            yield session


db = Database(
    url=str(settings.db.SQLALCHEMY_DATABASE_URI),
    echo=settings.db.ECHO,
    echo_pool=settings.db.ECHO_POOL,
    pool_size=settings.db.POOL_SIZE,
    max_overflow=settings.db.MAX_OVERFLOW,
)


def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Wrapper to simplify overrides so make this more test-friendly"""
    return db.session()


SessionDep = Annotated[AsyncSession, Depends(db_session)]


class Base(DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(naming_convention=settings.db.NAMING_CONVENTION)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{camel_case_to_snake_case(cls.__name__)}s"

    id: Mapped[int] = mapped_column(primary_key=True)
