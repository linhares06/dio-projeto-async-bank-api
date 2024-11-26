from datetime import datetime
from pydantic import BaseModel, PositiveFloat


class TransactionCreatedOut(BaseModel):
    id: int
    account_id: int
    type: str
    amount: PositiveFloat


class TransactionOut(TransactionCreatedOut):
    timestamp: datetime