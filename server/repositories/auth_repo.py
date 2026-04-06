"""Repository layer for User database access. Auth service owns user table."""

from typing import Optional
from uuid import UUID as PythonUUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from db.auth_models import User


class AuthRepository:
    """Data access layer for User table."""

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        result = self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    def get_user_by_id(self, user_id: PythonUUID) -> Optional[User]:
        """Get user by ID."""
        result = self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
    ) -> User:
        """
        Create a new user.
        
        Args:
            username: Username
            email: Email address
            password_hash: Hashed password
            
        Returns:
            Created User object
        """
        user = User(
            username=username,
            email=email,
            password=password_hash,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def user_exists(self, email: str = None, username: str = None) -> bool:
        """Check if user exists by email or username."""
        if email:
            return self.get_user_by_email(email) is not None
        if username:
            return self.get_user_by_username(username) is not None
        return False
