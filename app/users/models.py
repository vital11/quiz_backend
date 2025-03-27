import uuid

from sqlalchemy import func, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    email: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
    )
    full_name: Mapped[str | None] = mapped_column(
        String(50),
        default=None,
        server_default=None,
    )
    hashed_password: Mapped[bytes]
    is_active: Mapped[bool] = True
    is_superuser: Mapped[bool] = False
