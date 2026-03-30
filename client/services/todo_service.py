from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from repositories import TodoRepository
from schema import TodoCreate, TodoResponse, TodoUpdate
from uuid import UUID


class TodoService:
    def __init__(self, db: Session):
        self.repo = TodoRepository(db)

    def get_all(self, user_id: str) -> List[TodoResponse]:
        return self.repo.get_all(user_id)

    def get_or_404(self, id: UUID, user_id: str) -> TodoResponse:
        todo = self.repo.get_by_id(id, user_id)
        if not todo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo not found {id}")
        return todo

    def create(self, todo: TodoCreate, user_id: str):
        return self.repo.create(todo, user_id)

    def update(self, id: UUID, updated_todo: TodoUpdate, user_id: str):
        todo = self.get_or_404(id, user_id)
        return self.repo.update(todo, updated_todo)

    def delete(self, id: UUID, user_id: str):
        todo = self.get_or_404(id, user_id)
        return self.repo.delete(todo)
