import uuid

from sqlalchemy import func, String, Boolean, text
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
    hashed_password: Mapped[bytes] = mapped_column(
        deferred=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("true"),
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
    )

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, email={self.email!r})"

    def __repr__(self):
        return str(self)
