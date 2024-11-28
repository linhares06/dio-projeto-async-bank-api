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


async def test_create_transaction_deposit_success(client: AsyncClient, access_token_manager: str):
    # Given
    headers = {"Authorization": f"Bearer {access_token_manager}"}
    data = {"account_id": 1, "type": "DEPOSIT", "amount": 100}

    # When
    response = await client.post("/transactions/", json=data, headers=headers)

    # Then
    content = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert content["id"] is not None


async def test_create_transaction_withdrawal_success(client: AsyncClient, access_token_manager: str):
    # Given
    headers = {"Authorization": f"Bearer {access_token_manager}"}
    data = {"account_id": 1, "type": "WITHDRAWAL", "amount": 1000}

    # When
    response = await client.post("/transactions/", json=data, headers=headers)

    # Then
    content = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert content["detail"] == "Operation not carried out due to lack of balance"


async def test_create_transaction_not_authenticated_fail(client: AsyncClient):
    # Given
    data = {"account_id": 1, "type": "WITHDRAWAL", "amount": 1000}

    # When
    response = await client.post("/transactions/", json=data, headers={})

    # Then
    assert response.status_code == status.HTTP_401_UNAUTHORIZED