# Import all the models, so that SQLModel has them before being imported by Alembic

from sqlmodel import SQLModel
from app.users.models import User
