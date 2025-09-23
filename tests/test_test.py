import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import User


@pytest.mark.anyio
async def test_read_users(client: AsyncClient):
    response = await client.get("/api/v1/users")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_read_users_not_empty(
    client: AsyncClient, session: AsyncSession, user: User
):
    response = await client.get("/api/v1/users")
    assert response.status_code == status.HTTP_200_OK
    assert any(u["email"] == user.email for u in response.json()) is not None

    await session.delete(user)
    await session.commit()


@pytest.mark.skip
@pytest.mark.anyio
async def test_register_user(client: AsyncClient):
    response = await client.post(
        "/api/v1/users/signup",
        json={
            "email": "user1@example.com",
            "password": "string1",
            "full_name": "string",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()

    assert data["email"] == "user1@example.com"
    assert data["full_name"] == "string"
    assert "id" in data
