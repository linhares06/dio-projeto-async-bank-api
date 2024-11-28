import pytest_asyncio
from fastapi import status
from httpx import AsyncClient


@pytest_asyncio.fixture(autouse=True)
async def populate_posts(db):
    from src.schemas.account import AccountIn
    from src.services.account import AccountService
    from src.schemas.user import UserIn
    from src.services.user import UserService
    from src.schemas.transaction import TransactionIn
    from src.services.transaction import TransactionService

    user_service = UserService()
    await user_service.create(UserIn(name="José da Silva", cpf="12345678910", password="test1234"))
    await user_service.create(UserIn(name="Maria dos Santos", cpf="12345678911", password="test1234"))

    acc_service = AccountService()
    await acc_service.create(AccountIn(user_id="1", balance=10))
    await acc_service.create(AccountIn(user_id="2", balance=100))

    transaction_service = TransactionService()
    await transaction_service.create(TransactionIn(account_id=1, type="DEPOSIT", amount=100))


async def test_read_transaction_forbidden(client: AsyncClient, access_token_client: str):
    # Given
    headers = {"Authorization": f"Bearer {access_token_client}"}
    id = 1

    # When
    response = await client.get(f"/transactions/{id}", headers=headers)

    # Then
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_read_transaction_not_authenticated_fail(client: AsyncClient):
    # Given
    id = 1

    # When
    response = await client.get(f"/transactions/{id}", headers={})

    # Then
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_read_transaction_not_found_fail(client: AsyncClient, access_token_manager: str):
    # Given
    headers = {"Authorization": f"Bearer {access_token_manager}"}
    id = 4

    # When
    response = await client.get(f"/transactions/{id}", headers=headers)

    # Then
    assert response.status_code == status.HTTP_404_NOT_FOUND