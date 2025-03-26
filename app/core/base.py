"""Import all the models, so that SQLModel has them before being imported by Alembic"""

from app.core.database import Base
from app.users.models import User
