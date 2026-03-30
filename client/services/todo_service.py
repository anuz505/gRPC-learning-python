from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from repositories import TodoRepository
from schema import TodoCreate, TodoResponse, TodoUpdate
from uuid import UUID


class TodoService:
    def __init__(self, db: Session):
        self.repo = TodoRepository(db)

    def get_all(self) -> List[TodoResponse]:
        return self.repo.get_all()

    def get_or_404(self, id: UUID) -> TodoResponse:
        todo = self.repo.get_by_id(id)
        if not todo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo not found {id}")
        return todo

    def create(self, todo: TodoCreate):
        return self.repo.create(todo)

    def update(self, id: UUID, updated_todo: TodoUpdate):
        todo = self.get_or_404(id)
        return self.repo.update(todo, updated_todo)

    def delete(self, id: UUID):
        todo = self.get_or_404(id)
        return self.repo.delete(todo)
