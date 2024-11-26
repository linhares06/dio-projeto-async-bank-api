from passlib.context import CryptContext

import time
from typing import Annotated
from uuid import uuid4

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from src.config import settings


class AccessToken(BaseModel):
    iss: str
    sub: str
    rol: str
    aud: str
    exp: float
    iat: float
    nbf: float
    jti: str


class JWTToken(BaseModel):
    access_token: AccessToken


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def sign_jwt(user_id: str, role: str) -> JWTToken:
    """
    Generate a signed JSON Web Token (JWT) for a user.

    Args:
        user_id (int): The unique identifier of the user for whom the token is being generated.
        role (str): The role assigned to the user (e.g., "admin", "user").

    Returns:
        JWTToken: A dictionary containing the generated JWT as an `access_token`.

    The payload of the JWT includes:
        - `iss` (Issuer): The issuing authority of the token, set to "desafio-bank.com.br".
        - `sub` (Subject): The unique identifier of the user (`user_id`).
        - `rol` (Role): The user's role.
        - `aud` (Audience): The intended audience, set to "desafio-bank".
        - `exp` (Expiration): The timestamp when the token expires.
        - `iat` (Issued At): The timestamp when the token was issued.
        - `nbf` (Not Before): The timestamp before which the token is not valid.
        - `jti` (JWT ID): A unique identifier for the token.

    The JWT is signed using the secret and algorithm specified in the `settings`.
    """
    now = time.time()
    payload = {
        "iss": "desafio-bank.com.br",
        "sub": user_id,
        "rol": role,
        "aud": "desafio-bank",
        "exp": now + (60 * 30),  # 30 minutes
        "iat": now,
        "nbf": now,
        "jti": uuid4().hex,
    }
    token = jwt.encode(payload, settings.secret, algorithm=settings.algorithm)
    return {"access_token": token}


async def decode_jwt(token: str) -> JWTToken | None:
    try:
        decoded_token = jwt.decode(token, settings.secret, audience="desafio-bank", algorithms=[settings.algorithm])
        _token = JWTToken.model_validate({"access_token": decoded_token})
        return _token if _token.access_token.exp >= time.time() else None
    except Exception:
        return None
    

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> JWTToken:
        authorization = request.headers.get("Authorization", "")
        scheme, _, credentials = authorization.partition(" ")

        if credentials:
            if not scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme.",
                )
            
            payload = await decode_jwt(credentials)
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token.",
                )
            return payload
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization code.",
            )
        

async def get_current_user(token: Annotated[JWTToken, Depends(JWTBearer())],) -> dict[str, str]:
    return {"user_id": token.access_token.sub, "role": token.access_token.rol}


def login_required(current_user: Annotated[dict[str, str], Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return current_user


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)
