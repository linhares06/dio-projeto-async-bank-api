from fastapi import APIRouter, Depends, status, HTTPException

from src.schemas.transaction import TransactionIn
from src.security.auth import login_required
from src.services.transaction import TransactionService
from src.views.transaction import TransactionCreatedOut, TransactionOut
from src.exceptions import AccountNotFoundError, BusinessError, ForbiddenAccountAccess


router = APIRouter(prefix="/transactions", dependencies=[Depends(login_required)])

service = TransactionService()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TransactionCreatedOut)
async def create_transaction(transaction: TransactionIn):
    try:
        return await service.create(transaction)
    except AccountNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Account not found"
        )
    except BusinessError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operation not carried out due to lack of balance"
        )
    

@router.get("/{account_id}", response_model=list[TransactionOut])
async def list_transactions(account_id: int, limit: int = 10, skip: int = 0, current_user = Depends(login_required)):
    try:
        return await service.read_all_by_account_id(account_id=account_id, current_user=current_user, limit=limit, skip=skip)
    except AccountNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    except ForbiddenAccountAccess:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this account."
        )
