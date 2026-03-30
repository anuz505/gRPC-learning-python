from typing import List
from fastapi import Depends, status
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from db import get_db
from schema import TodoCreate, TodoResponse, TodoUpdate
from services import TodoService
from uuid import UUID
from core import LoggerSetup

logger = LoggerSetup.setup_logger(__name__)
todo_router = APIRouter(prefix="/todo", tags=["todos"])


def get_service(db: Session = Depends(get_db)) -> TodoService:
    logger.info("starting service")
    return TodoService(db)


@todo_router.get("/", response_model=List[TodoResponse])
async def get_all_todos(service: TodoService = Depends(get_service)):
    logger.info("gettings all todos")
    return service.get_all()


@todo_router.get("/{id}")
async def get_todo_detail(id: UUID, service: TodoService = Depends(get_service)):
    logger.info(f"getting todo {id}")
    return service.get_or_404(id)


@todo_router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(data: TodoCreate, service: TodoService = Depends(get_service)):
    logger.info("creating todo")
    return service.create(data)


@todo_router.put("/{id}", response_model=TodoResponse, status_code=status.HTTP_200_OK)
async def update_todo(id: UUID, data: TodoUpdate, service: TodoService = Depends(get_service)):
    logger.info("updating todo")
    return service.update(id, data)


@todo_router.delete("/{id}")
async def delete_todo(id: UUID, service: TodoService = Depends(get_service)):
    logger.info("deleting todo")
    return service.delete(id)
