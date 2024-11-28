import pytest_asyncio
from fastapi import status
from httpx import AsyncClient


@pytest_asyncio.fixture(autouse=True)
async def populate_posts(db):
    from src.schemas.user import UserIn
    from src.services.user import UserService

    user_service = UserService()
    await user_service.create(UserIn(name="José da Silva", cpf="12345678910", password="test1234"))
    await user_service.create(UserIn(name="Maria dos Santos", cpf="12345678911", password="test1234"))


async def test_update_user_not_authenticated_fail(client: AsyncClient):
    # Given
    id = 1

    # When
    response = await client.patch(f"/users/{id}", headers={})

    # Then
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_update_user_not_found_fail(client: AsyncClient, access_token_manager: str):
    # Given
    headers = {"Authorization": f"Bearer {access_token_manager}"}
    data = {"name": "Joaquim"}
    id = 4

    # When
    response = await client.patch(f"/posts/{id}", json=data, headers=headers)

    # Then
    assert response.status_code == status.HTTP_404_NOT_FOUND