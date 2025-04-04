import uuid
from typing import Annotated

from fastapi import Depends, Path, HTTPException, status

from app.auth.crud import authenticate_by_token_sub
from app.auth.schemas import TokenType
from app.auth.validation import (
    validate_token,
    validate_token_type,
    reusable_oauth2_scheme,
)
from app.core.database import SessionDep
from app.users.models import User
from app.users import crud


class AuthenticateByTokenOfType:
    """Current user getter by token type: 'access', 'refresh' etc."""

    def __init__(self, token_type: TokenType):
        self.token_type = token_type

    async def __call__(
        self,
        session: SessionDep,
        token: Annotated[str, Depends(reusable_oauth2_scheme)],
    ):
        payload = validate_token(token=token)
        validate_token_type(
            payload=payload,
            token_type=self.token_type,
        )
        return await authenticate_by_token_sub(
            session=session,
            payload=payload,
        )


CurrentUser = Annotated[
    User, Depends(AuthenticateByTokenOfType(token_type=TokenType.ACCESS))
]

CurrentUserForRefresh = Annotated[
    User, Depends(AuthenticateByTokenOfType(token_type=TokenType.REFRESH))
]


def get_current_superuser(
    current_user: CurrentUser,
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


CurrentSuperUser = Annotated[User, Depends(get_current_superuser)]


async def get_user_by_id(
    user_id: Annotated[uuid.UUID, Path],
    session: SessionDep,
) -> User:
    user = await crud.get(session=session, ident=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    return user


UserByIdDep = Annotated[User, Depends(get_user_by_id)]
