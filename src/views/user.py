from pydantic import BaseModel


class UserCreatedOut(BaseModel):
    id: int
    name: str
    cpf: str

    class Config:
        use_enum_values = True


class UserOut(UserCreatedOut):
    role_id: str