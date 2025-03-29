from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer

from app.auth import crud
from app.core.security import create_access_token, create_refresh_token
from app.auth.schemas import Token

from app.core.database import SessionDep
from app.core.dependencies import CurrentUser
from app.core.security_auth0 import VerifyTokenDep
from app.users.schemas import UserPublic


http_bearer = HTTPBearer(auto_error=False)


router = APIRouter(
    tags=["Login"],
    dependencies=[Depends(http_bearer)],
)


@router.post("/access-token")
async def login_access_token(
    session: SessionDep,
    user_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """OAuth2 compatible token login, get an access token for future requests"""
    user = await crud.authenticate(
        session=session,
        email=user_data.username,
        password=user_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )
    return Token(
        access_token=create_access_token(user=user),
        refresh_token=create_refresh_token(user=user),
    )


@router.get("/test-token", response_model=UserPublic, status_code=status.HTTP_200_OK)
async def reed_me(
    current_user: CurrentUser,
) -> UserPublic:
    """Test access token"""
    return current_user


@router.get("/test-auth0-token", status_code=status.HTTP_200_OK)
async def reed_auth0_token_payload(
    auth_result: VerifyTokenDep,
) -> Any:
    """A valid Auth0 access token is required to access this route"""
    return auth_result
