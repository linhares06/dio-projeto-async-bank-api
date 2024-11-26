from databases.interfaces import Record

from src.exceptions import AccountNotFoundError, UserNotFoundError
from src.database import database
from src.models.account import accounts
from src.schemas.account import AccountIn
from src.services.user import UserService


class AccountService:
    async def create(self, account: AccountIn) -> int:
        total = await UserService.count(account.user_id)
        if not total:
            raise UserNotFoundError

        command = accounts.insert().values(
            user_id = account.user_id,
            balance = account.balance,
        ) 

        return await database.execute(command)
    
    async def read_all(self, limit: int, skip: int = 0) -> list[Record]:
        query = accounts.select().limit(limit).offset(skip)

        return await database.fetch_all(query)

    async def read(self, id: int) -> Record:
        return await self.__get_by_id(id)
    
    async def read_by_user_id(self, user_id: int) -> list[Record]:
        total = await self.count_user_id(user_id)
        if not total:
            raise UserNotFoundError

        query = accounts.select().where(accounts.c.user_id == user_id)

        return await database.fetch_all(query)
    
    async def update(self, id: int, account: AccountIn) -> Record:
        total = await self.count(id)
        if not total:
            raise AccountNotFoundError

        data = account.model_dump(exclude_unset=True)
        command = accounts.update().where(accounts.c.id == id).values(**data)
        await database.execute(command)

        return await self.__get_by_id(id)

    async def delete(self, id: int) -> None:
        command = accounts.delete().where(accounts.c.id == id)
        await database.execute(command)

    @staticmethod
    async def count(id: int) -> int:
        query = "select count(id) as total from accounts where id = :id"
        result = await database.fetch_one(query, {"id": id})

        return result.total
    
    async def count_user_id(self, user_id: int) -> int:
        query = "select count(user_id) as total from accounts where user_id = :user_id"
        result = await database.fetch_one(query, {"user_id": user_id})

        return result.total
    
    async def __get_by_id(self, id: int) -> Record:
        query = accounts.select().where(accounts.c.id == id)
        account = await database.fetch_one(query)
        if not account:
            raise AccountNotFoundError
        
        return account