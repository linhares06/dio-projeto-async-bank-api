from datetime import datetime
from pydantic import BaseModel, PositiveFloat


class AccountCreatedOut(BaseModel):
    id: int
    user_id: int
    balance: PositiveFloat


class AccountOut(AccountCreatedOut):
    created_at: datetime
