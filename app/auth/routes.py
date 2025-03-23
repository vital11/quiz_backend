from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.models import Token, TokenPayload
from app.auth.repository import AuthRepository
from app.core.dependencies import CurrentUser
from app.core.security import encode_access_token
from app.core.security_auth0 import VerifyTokenDep
from app.users.models import UserPublic


router = APIRouter(tags=["Login"])


@router.post("/access-token")
async def login_access_token(
        user_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """OAuth2 compatible token login, get an access token for future requests"""
    user = await AuthRepository.authenticate(email=user_data.username, password=user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return Token(
        access_token=encode_access_token(
            TokenPayload(sub=user.id)
        )
    )


@router.get("/test-token", response_model=UserPublic, status_code=status.HTTP_200_OK)
async def reed_me(current_user: CurrentUser) -> UserPublic:
    """Test access token"""
    return current_user


@router.get("/test-auth0-token", status_code=status.HTTP_200_OK)
async def reed_auth0_token_payload(auth_result: VerifyTokenDep) -> Any:
    """A valid Auth0 access token is required to access this route"""
    return auth_result
