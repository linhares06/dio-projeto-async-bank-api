from fastapi import APIRouter, Depends, status, HTTPException

from src.schemas.account import AccountIn
from src.security.auth import login_required
from src.services.account import AccountService
from src.views.account import AccountOut, AccountCreatedOut
from src.exceptions import UserNotFoundError, AccountNotFoundError

router = APIRouter(prefix="/accounts", dependencies=[Depends(login_required)])

service = AccountService()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AccountCreatedOut)
async def create_account(account: AccountIn):
    try:
        return {**account.model_dump(), "id": await service.create(account)}
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@router.get("/", response_model=list[AccountOut])
async def list_accounts(limit: int, skip: int = 0):
    return await service.read_all(limit=limit, skip=skip)


@router.get("/users/{user_id}", response_model=list[AccountOut])
async def list_accounts_by_user(user_id: int):
    try:
        return await service.read_by_user_id(user_id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

@router.get("/me", response_model=AccountOut)
async def read_my_info(current_user: dict[str, str] = Depends(login_required)):
    return await service.read(int(current_user["user_id"]))


@router.get("/{id}", response_model=AccountOut)
async def read_account(id: int):
    try:
        return await service.read(id)
    except AccountNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_account(id: int):
    await service.delete(id)