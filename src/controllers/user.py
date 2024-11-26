from fastapi import APIRouter, Depends, status, HTTPException

from src.schemas.user import UserIn, UserUpdateIn, UserRoleUpdateIn
from src.security.auth import login_required
from src.services.user import UserService
from src.views.user import UserCreatedOut, UserOut
from src.exceptions import UserNotFoundError, ForbiddenAccountAccess

router = APIRouter(prefix="/users")

service = UserService()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserCreatedOut)
async def create_user(user: UserIn):
    return {**user.model_dump(), "id": await service.create(user)}


@router.get("/", response_model=list[UserOut])
async def list_user(limit: int = 10, skip: int = 0, current_user: dict[str, str] = Depends(login_required)):
    try:
        return await service.read_all(limit=limit, skip=skip, current_user=current_user)
    except ForbiddenAccountAccess:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource."
        )


@router.get("/me", response_model=UserOut)
async def read_my_info(current_user: dict[str, str] = Depends(login_required)):
    return await service.read_me(id=int(current_user["user_id"]))


@router.get("/{id}", response_model=UserOut)
async def read_user(id: int, current_user: dict[str, str] = Depends(login_required)):
    try:
        return await service.read(id, current_user)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except ForbiddenAccountAccess:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource."
        )


@router.patch("/{id}", response_model=UserOut)
async def update_user(id: int, user: UserUpdateIn, current_user: dict[str, str] = Depends(login_required)):
    try:
        return await service.update(id=id, user=user, current_user=current_user)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except ForbiddenAccountAccess:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource."
        )


@router.patch("/{id}/role", response_model=UserOut)
async def update_user_role(id: int, user: UserRoleUpdateIn, current_user: dict[str, str] = Depends(login_required)):
    try:
        return await service.update(id=id, user=user, current_user=current_user)
    except ForbiddenAccountAccess:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource."
        )   


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_user(id: int, current_user: dict[str, str] = Depends(login_required)):
    try:
        await service.delete(id=id, current_user=current_user)
    except ForbiddenAccountAccess:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource."
        )