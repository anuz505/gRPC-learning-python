from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Annotated
from db.auth_models import RoleEnum
import uuid


class UserSignUp(BaseModel):
    username: Annotated[str, Field(max_length=255)]
    email: Annotated[EmailStr, Field(max_length=255)]
    password: Annotated[str, Field(max_length=50, min_length=8)]
    role: Annotated[RoleEnum, Field(default=RoleEnum.user)]


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    role: RoleEnum
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    username: Annotated[str | None, Field(max_length=255)] = None
    email: Annotated[EmailStr | None, Field(max_length=255)] = None
    role: Annotated[RoleEnum | None, Field(default=None)] = None
