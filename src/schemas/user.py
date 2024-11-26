from enum import Enum

from pydantic import BaseModel, Field


class Role(str, Enum):
    MANAGER = "MANAGER"
    CLIENT = "CLIENT"


class UserIn(BaseModel):
    name: str
    cpf: str = Field(..., pattern=r'^\d{11}$', description="CPF")
    password: str


class UserUpdateIn(BaseModel):
    name: str 
    password: str


class UserBalanceUpdateIn(BaseModel):
    balance: float


class UserRoleUpdateIn(BaseModel):
    role_id: Role

    class Config:
        use_enum_values = True