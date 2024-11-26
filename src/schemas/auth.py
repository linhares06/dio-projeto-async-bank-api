from pydantic import BaseModel


class LoginIn(BaseModel):
    cpf: str
    password: str