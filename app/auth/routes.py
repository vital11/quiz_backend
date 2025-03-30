from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer

from app.auth import crud
from app.auth.helpers import create_access_token, create_refresh_token
from app.auth.schemas import Token

from app.core.database import SessionDep
from app.auth.dependencies import CurrentUser, CurrentUserForRefresh
from app.core.security_auth0 import VerifyTokenDep
from app.users.schemas import UserPublic


http_bearer = HTTPBearer(auto_error=False)


router = APIRouter(
    tags=["Login"],
    dependencies=[Depends(http_bearer)],
)


@router.post("/access-token", response_model=Token, status_code=status.HTTP_201_CREATED)
async def login_access_token(
    session: SessionDep,
    user_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """OAuth2 compatible token login by form data, get an access token for future requests"""
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


@router.post(
    "/refresh-token",
    response_model=Token,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def refresh_token(
    current_user_for_refresh: CurrentUserForRefresh,
) -> Token:
    """OAuth2 compatible token login by refresh token, get an access token for future requests"""
    return Token(
        access_token=create_access_token(user=current_user_for_refresh),
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
