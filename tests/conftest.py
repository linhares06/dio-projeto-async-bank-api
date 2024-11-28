import asyncio

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.config import settings
from src.schemas.user import UserRoleIn
from src.services.user import UserService

settings.database_url = "sqlite:///tests.db"


@pytest_asyncio.fixture
async def db(request):
    from src.database import database, engine, metadata
    from src.models.user import users  # noqa
    from src.models.transaction import transactions  # noqa
    from src.models.account import accounts  # noqa

    await database.connect()
    metadata.create_all(engine)

    def teardown():
        async def _teardown():
            await database.disconnect()
            metadata.drop_all(engine)

        asyncio.run(_teardown())

    request.addfinalizer(teardown)


@pytest_asyncio.fixture
async def client(db):
    from src.main import app

    transport = ASGITransport(app=app)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    async with AsyncClient(base_url="http://test", transport=transport, headers=headers) as client:
        yield client


@pytest_asyncio.fixture
async def access_token_client(client: AsyncClient):
    service = UserService()
    await service.create(UserRoleIn(name="Test1", cpf="11111111111", password="12345678", role_id="CLIENT"))

    data: dict = {"cpf": "11111111111",  "password": "12345678"} 
    response = await client.post("/auth/login", json=data)

    return response.json()["access_token"]


@pytest_asyncio.fixture
async def access_token_manager(client: AsyncClient):
    service = UserService()
    await service.create(UserRoleIn(name="Test1", cpf="11111111111", password="12345678", role_id="MANAGER"))

    data: dict = {"cpf": "11111111111",  "password": "12345678"} 
    response = await client.post("/auth/login", json=data)

    return response.json()["access_token"]