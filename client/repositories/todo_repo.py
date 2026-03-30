from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from db import Todo
from schema import TodoCreate, TodoResponse, TodoUpdate
from sqlalchemy.dialects.postgresql import UUID


class TodoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, user_id: str) -> List[TodoResponse]:
        result = self.db.execute(select(Todo).where(Todo.user_id == user_id))
        return result.scalars().all()

    def get_by_id(self, id: UUID, user_id: str):
        result = self.db.execute(select(Todo).where(Todo.id == id, Todo.user_id == user_id))
        return result.scalar_one_or_none()

    def create(self, data: TodoCreate, user_id: str) -> TodoResponse:
        payload = data.model_dump()
        payload["user_id"] = user_id
        todo = Todo(**payload)
        self.db.add(todo)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def update(self, todo: Todo, data: TodoUpdate) -> TodoResponse:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(todo, field, value)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def delete(self, todo: Todo):
        self.db.delete(todo)
        self.db.commit()
