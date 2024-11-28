import pytest_asyncio
from fastapi import status
from httpx import AsyncClient


@pytest_asyncio.fixture(autouse=True)
async def populate_posts(db):
    from src.schemas.account import AccountIn
    from src.services.account import AccountService
    from src.schemas.user import UserIn
    from src.services.user import UserService

    user_service = UserService()
    await user_service.create(UserIn(name="José da Silva", cpf="12345678910", password="test1234"))
    await user_service.create(UserIn(name="Maria dos Santos", cpf="12345678911", password="test1234"))

    acc_service = AccountService()
    await acc_service.create(AccountIn(user_id="1", balance=10))
    await acc_service.create(AccountIn(user_id="2", balance=100))


async def test_read_account_success(client: AsyncClient, access_token_manager: str):
    # Given
    headers = {"Authorization": f"Bearer {access_token_manager}"}
    acc_id = 1

    # When
    response = await client.get(f"/accounts/{acc_id}", headers=headers)

    # Then
    content = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert content["id"] == acc_id


async def test_read_account_not_authenticated_fail(client: AsyncClient):
    # Given
    acc_id = 1

    # When
    response = await client.get(f"/accounts/{acc_id}", headers={})

    # Then
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_read_account_not_found_fail(client: AsyncClient, access_token_manager: str):
    # Given
    headers = {"Authorization": f"Bearer {access_token_manager}"}
    acc_id = 7

    # When
    response = await client.get(f"/accounts/{acc_id}", headers=headers)

    # Then
    assert response.status_code == status.HTTP_404_NOT_FOUND