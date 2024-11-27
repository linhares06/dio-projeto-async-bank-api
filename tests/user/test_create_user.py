from fastapi import status
from httpx import AsyncClient


async def test_create_user_success(client: AsyncClient):
    # Given
    #headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "name": "José da Silva",
        "cpf": "12345678910",
        "password": "test1234",
    }

    # When
    response = await client.post("/users/", json=data)

    # Then
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["id"] is not None