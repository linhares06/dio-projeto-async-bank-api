from enum import Enum

import sqlalchemy as sa

from src.database import metadata

class Role(str, Enum):
    MANAGER = "MANAGER"
    CLIENT = "CLIENT"
    

users = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.String(255), nullable=False,),
    sa.Column("cpf", sa.String(11), nullable=False, unique=True, index=True),
    sa.Column("password", sa.String(255), nullable=False),
    sa.Column("role_id", sa.Enum(Role, name="role"), nullable=False, default=Role.CLIENT),
    sa.Column("created_at", sa.TIMESTAMP(timezone=True), default=sa.func.now()),
)