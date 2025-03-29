from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.users import crud
from app.users.schemas import UserPublic


async def authenticate(
    session: AsyncSession,
    email: EmailStr | str,
    password: str,
) -> UserPublic | None:
    db_user = await crud.get_user_by_email(
        session=session,
        email=email,
        undefer_password=True,
    )
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return UserPublic(**db_user.__dict__)
