from databases.interfaces import Record

from src.exceptions import UserNotFoundError, ForbiddenAccountAccess
from src.database import database
from src.models.user import users
from src.schemas.user import UserIn, UserUpdateIn, Role
from src.security.auth import hash_password


class UserService:
    async def read_all(self, current_user: dict[str, str], limit: int, skip: int = 0) -> list[Record]:
        if current_user.get("role", "") != Role.MANAGER:
            raise ForbiddenAccountAccess
        
        query = users.select().limit(limit).offset(skip)

        return await database.fetch_all(query)

    async def create(self, user: UserIn) -> int:
        command = users.insert().values(
            name = user.name,
            cpf = user.cpf,
            password = hash_password(user.password),
            role_id = Role.CLIENT,
        )
        return await database.execute(command)

    async def read(self, id: int, current_user: dict[str, str]) -> Record:
        if current_user.get("role", "") != Role.MANAGER:
            raise ForbiddenAccountAccess
        
        return await self.__get_by_id(id)
    
    async def read_me(self, id: int) -> Record:
        return await self.__get_by_id(id)

    async def update(self, id: int, user: UserUpdateIn, current_user: dict[str, str]) -> Record:
        if current_user.get("role", "") != Role.MANAGER:
            raise ForbiddenAccountAccess
        
        total = await self.count(id)
        if not total:
            raise UserNotFoundError

        data = user.model_dump(exclude_unset=True)

        if data.get("password"):
            data["password"] = hash_password(data["password"])
            
        command = users.update().where(users.c.id == id).values(**data)
        await database.execute(command)

        return await self.__get_by_id(id)

    async def delete(self, id: int, current_user: dict[str, str]) -> None:
        if current_user.get("role", "") != Role.MANAGER:
            raise ForbiddenAccountAccess
        
        command = users.delete().where(users.c.id == id)
        await database.execute(command)

    @staticmethod
    async def count(id: int) -> int:
        query = "select count(id) as total from users where id = :id"
        result = await database.fetch_one(query, {"id": id})

        return result.total

    async def __get_by_id(self, id: int) -> Record:
        query = users.select().where(users.c.id == id)
        user = await database.fetch_one(query)
        if not user:
            raise UserNotFoundError
        
        return user