from fastapi import status
from httpx import AsyncClient


async def test_create_account_success(client: AsyncClient, access_token_manager: str):
    # Given
    headers = {"Authorization": f"Bearer {access_token_manager}"}
    data = { "user_id": 1, "balance": 1000.0 }

    # When
    response = await client.post("/accounts/", json=data, headers=headers)

    # Then
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["id"] is not None


async def test_create_account_invalid_user(client: AsyncClient, access_token_manager: str):
    # Given
    headers = {"Authorization": f"Bearer {access_token_manager}"}
    data = { "user_id": 2, "balance": 1000.0 }

    # When
    response = await client.post("/accounts/", json=data, headers=headers)

    # Then
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User not found"


async def test_create_account_invalid_balance(client: AsyncClient, access_token_manager: str):
    # Given
    headers = {"Authorization": f"Bearer {access_token_manager}"}
    data = { "user_id": 1, "balance": -1000.0 }

    # When
    response = await client.post("/accounts/", json=data, headers=headers)

    # Then
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()['detail'][0]["msg"] == "Input should be greater than 0"


async def test_create_account_not_authenticated_fail(client: AsyncClient):
    # Given
    data = { "user_id": 2, "balance": 1000.0 }

    # When
    response = await client.post("/accounts/", json=data, headers={})

    # Then
    assert response.status_code == status.HTTP_401_UNAUTHORIZED