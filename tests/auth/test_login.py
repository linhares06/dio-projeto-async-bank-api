from fastapi import status
from httpx import AsyncClient

import pytest_asyncio


@pytest_asyncio.fixture(autouse=True)
async def populate_users(db):
    from src.schemas.user import UserIn
    from src.services.user import UserService

    service = UserService()
    await service.create(UserIn(
        name="Test1",
        cpf="11111111111",
        password="12345678",
    ))


async def test_login_success(client: AsyncClient) -> None:
    # Given
    data = {
        "cpf": "11111111111",
        "password": "12345678"
    }

    # When
    response = await client.post("/auth/login", json=data)

    # Then
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["access_token"] is not None