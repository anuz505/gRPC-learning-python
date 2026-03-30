from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from repositories import AuthRepository
from schema.auth_schema import UserResponse, UserSignUp, UserUpdate
from uuid import UUID


class AuthDbService:
    def __init__(self, db: Session):
        self.repo = AuthRepository(db)

    def get_all_users(self) -> List[UserResponse]:
        return self.repo.get_all_users()

    def create_user(self, data: UserSignUp) -> UserResponse:
        try:
            return self.repo.create_user(data)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

    def update_user(self, data: UserUpdate, id: UUID) -> UserResponse:
        try:
            return self.repo.update_user(data, id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
