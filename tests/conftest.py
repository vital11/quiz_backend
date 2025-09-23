from typing import AsyncGenerator
import pytest

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import Base
from app.core.config import settings
from app.core.database import Database, db_session
from app.main import app
from app.users.models import User


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """To scope as session the anyio backend"""
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
async def db() -> AsyncGenerator[Database, None]:
    """Session-wide test database."""
    db_name: str = settings.db.POSTGRES_DB
    test_db_url = str(settings.db.SQLALCHEMY_DATABASE_URI).replace(
        db_name, f"test_{db_name}"
    )
    db = Database(
        url=test_db_url,
        echo=settings.db.ECHO,
        echo_pool=settings.db.ECHO_POOL,
        pool_size=settings.db.POOL_SIZE,
        max_overflow=settings.db.MAX_OVERFLOW,
    )

    async with db.engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield db
    # Optionally clean up (not usually necessary for persistent local test db)
    await db.dispose()


@pytest.fixture(scope="session")
async def session(db: Database) -> AsyncGenerator[AsyncSession, None]:
    """New database session for a test."""
    async with db.session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
            await session.rollback()


@pytest.fixture(scope="module")
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Asynchronous test client with override session dependency"""

    async def override_session() -> AsyncGenerator[AsyncSession, None]:
        yield session

    app.dependency_overrides[db_session] = override_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
async def user(session: AsyncSession) -> User:
    """Optionally add a user before testing"""
    user = User(email="test@example.com", hashed_password="fake".encode())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

    # yield user
    # await session.delete(user)
    # await session.commit()
