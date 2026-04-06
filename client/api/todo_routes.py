"""Todo management routes (requires authentication)."""

from typing import List
from fastapi import Depends, status
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from db import get_db
from schema import TodoCreate, TodoResponse, TodoUpdate
from services import TodoService
from dependencies.auth_dependency import get_current_user
from uuid import UUID
from core import LoggerSetup

logger = LoggerSetup.setup_logger("TodoRoutes")
todo_router = APIRouter(prefix="/todo", tags=["todos"])


def get_service(db: Session = Depends(get_db)) -> TodoService:
    logger.info("starting service")
    return TodoService(db)


@todo_router.get(
    "/",
    response_model=List[TodoResponse],
    summary="List user todos",
    description="Get all todo items for the authenticated user"
)
async def get_all_todos(
    service: TodoService = Depends(get_service),
    user_id: str = Depends(get_current_user),
):
    """Get all todos for current user."""
    logger.info(f"getting all todos for user: {user_id}")
    return service.get_all(user_id)


@todo_router.get(
    "/{id}",
    response_model=TodoResponse,
    summary="Get todo detail",
    description="Get a specific todo by ID"
)
async def get_todo_detail(
    id: UUID,
    service: TodoService = Depends(get_service),
    user_id: str = Depends(get_current_user),
):
    """Get a specific todo by ID."""
    logger.info(f"getting todo {id}")
    return service.get_or_404(id, user_id)


@todo_router.post(
    "/",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create todo",
    description="Create a new todo item"
)
async def create_todo(
    data: TodoCreate,
    service: TodoService = Depends(get_service),
    user_id: str = Depends(get_current_user),
):
    """Create a new todo."""
    logger.info(f"creating todo for user: {user_id}")
    return service.create(data, user_id)


@todo_router.put(
    "/{id}",
    response_model=TodoResponse,
    status_code=status.HTTP_200_OK,
    summary="Update todo",
    description="Update a todo item"
)
async def update_todo(
    id: UUID,
    data: TodoUpdate,
    service: TodoService = Depends(get_service),
    user_id: str = Depends(get_current_user),
):
    logger.info("updating todo")
    return service.update(id, data, user_id)


@todo_router.delete("/{id}")
async def delete_todo(
    id: UUID,
    service: TodoService = Depends(get_service),
    user_id: str = Depends(get_current_user),
):
    logger.info("deleting todo")
    return service.delete(id, user_id)
