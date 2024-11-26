from src.exceptions import IncorrectUserInformationError
from src.database import database
from src.models.user import users
from src.security.auth import verify_password


class AuthService:
    async def login(self, cpf, password):
        query = users.select().where(users.c.cpf == cpf)
        user = await database.fetch_one(query)

        if not user or not verify_password(password, user.password):
            raise IncorrectUserInformationError
        
        return user