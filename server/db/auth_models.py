from datetime import datetime
from uuid import UUID as PythonUUID, uuid4
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from sqlalchemy import DateTime, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum
from .db_models import Base
from sqlalchemy import Enum as SQLAlchemyEnum


class RoleEnum(str, Enum):
    admin = "admin"
    user = "user"


class User(Base):
    """User tablee for auth"""
    __tablename__ = "users"

    id: Mapped[PythonUUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    username: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, onupdate=datetime.now)
    role: Mapped[RoleEnum] = mapped_column(SQLAlchemyEnum(RoleEnum, name="role_enum"), default=RoleEnum.user, nullable=False)

    __table_args__ = (CheckConstraint("length(password) >= 8", name="password_at_least_8_chars"),)
