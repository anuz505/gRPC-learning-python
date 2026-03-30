from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import UUID

from db.auth_models import User
from schema import UserResponse, UserSignUp, UserUpdate
from utils.auth_utils import get_password_hash


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_users(self) -> List[UserResponse]:
        result = self.db.execute(select(User))
        return result.scalars().all()

    def get_by_id(self, id: UUID) -> UserResponse:
        result = self.db.execute(select(User).where(User.id == id))
        return result.scalar_one_or_none()

    def get_user_by_email(self, email: str) -> UserResponse:
        result = self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    def get_user_by_username(self, username: str) -> UserResponse:
        result = self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    def create_user(self, data: UserSignUp) -> UserResponse:
        existing_user = self.get_user_by_email(data.email)
        if existing_user:
            raise ValueError("User with this email already exists")

        payload = data.model_dump()
        payload["password"] = get_password_hash(payload["password"])
        user = User(**payload)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, data: UserUpdate, id: UUID) -> UserResponse:
        user = self.get_by_id(id)
        if not user:
            raise ValueError("The user does not exist")

        update_data = data.model_dump(exclude_unset=True)
        new_email = update_data.get("email")

        if new_email and new_email != user.email:
            existing_user = self.get_user_by_email(new_email)
            if existing_user:
                raise ValueError("User with this email already exists")

        for field, value in update_data.items():
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user
