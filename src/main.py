from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.controllers import user, account, auth, transaction
from src.database import database


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


tags_metadata = [
    {
        "name": "auth",
        "description": "Operações para autenticação",
    },
    {
        "name": "user",
        "description": "Operações para manter usuários.",
    },
    {
        "name": "account",
        "description": "Operações para manter contas dos usuários.",
    },
    {
        "name": "transaction",
        "description": "Operações para manter transações.",
    },
]

servers = [
    {"url": "http://localhost:8000", "description": "Ambiente de desenvolvimento"},
]


app = FastAPI(
    title="DIO bank API",
    version="1.0.0",
    summary="API para banking.",
    description="""
DIO bank API. 🚀

## Posts

Você será capaz de fazer:

* **Criar usuários**.
* **Recuperar xxxx**.
* **Recuperar xxxx por ID**.
* **Atualizar xxxx**.
* **Excluir xxxx**.
                """,
    openapi_tags=tags_metadata,
    servers=servers,
    redoc_url=None,
    # openapi_url=None, # disable docs
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#app.include_router(auth.router, tags=["auth"])
app.include_router(user.router, tags=["user"])
app.include_router(account.router, tags=["account"])
app.include_router(auth.router, tags=["auth"])
app.include_router(transaction.router, tags=["transaction"])