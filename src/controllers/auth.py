from fastapi import APIRouter, HTTPException, status

from src.security.auth import sign_jwt
from src.schemas.auth import LoginIn
from src.views.auth import LoginOut
from src.services.auth import AuthService
from src.exceptions import IncorrectUserInformationError


router = APIRouter(prefix="/auth")

service = AuthService()


@router.post("/login", response_model=LoginOut)
async def login(data: LoginIn):
    try:
        user = await service.login(data.cpf, data.password)
        return sign_jwt(user_id=str(user.id), role=user.role_id)
    except IncorrectUserInformationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user information"
        )