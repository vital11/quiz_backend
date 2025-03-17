from app.core.database import SessionDep
from app.users.models import UserCreate, UserPublic, User


class UserRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    async def create(self, payload: UserCreate) -> UserPublic:
        new_user = User(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password="hashed_password",
        )
        self.session.add(new_user)
        await self.session.commit()
        self.session.refresh(new_user)
        return UserPublic(**new_user.model_dump())
