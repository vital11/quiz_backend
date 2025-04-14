from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from fastapi.responses import HTMLResponse

from app.auth import crud
from app.auth.crud import authenticate_by_token_sub
from app.auth.helpers import (
    create_access_token,
    create_refresh_token,
    create_password_reset_token,
    hash_password,
)
from app.auth.schemas import Token, Message, TokenPayload, NewPassword
from app.auth.validation import validate_token

from app.core.database import SessionDep
from app.auth.dependencies import (
    CurrentUser,
    CurrentUserForRefresh,
)
from app.core.security_auth0 import VerifyTokenDep
from app.helpers.emails import generate_reset_password_email, send_email
from app.users.crud import get_user_by_email
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


@router.post("/recover-password/{email}")
async def recover_password(email: str, session: SessionDep) -> Message:
    """Password Recovery"""
    user = await get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this email does not exist in the system.",
        )
    password_reset_token = create_password_reset_token(user=user)

    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Password recovery email sent")


@router.post("/reset-password/")
async def reset_password(
    session: SessionDep,
    body: NewPassword,
) -> Message:
    """Reset password"""
    payload = validate_token(token=body.token)
    user = await authenticate_by_token_sub(
        session=session,
        payload=TokenPayload.model_validate(payload),
    )
    user.hashed_password = hash_password(password=body.new_password)
    session.add(user)
    await session.commit()
    return Message(message="Password updated successfully")


@router.post(
    "/password-recovery-html-content/{email}",
    response_class=HTMLResponse,
)
async def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """HTML Content for Password Recovery"""
    user = await get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = create_password_reset_token(user=user)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    return HTMLResponse(
        content=email_data.html_content, headers={"subject:": email_data.subject}
    )
