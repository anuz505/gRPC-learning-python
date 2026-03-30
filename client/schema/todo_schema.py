from pydantic import BaseModel, Field
from datetime import datetime
from typing import Annotated
import uuid


class TodoCreate(BaseModel):
    title: Annotated[str, Field(max_length=255)] = "placeholder title"
    description: Annotated[str, Field(max_length=255, examples=["placeholder description"])] = "placeholder description"


class TodoResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TodoUpdate(BaseModel):
    title: Annotated[str | None, Field(max_length=255)] = None
    description: Annotated[str | None, Field(default=None, max_length=255)] = None