from typing import Annotated, List
from datetime import timedelta
from uuid import UUID

from fastapi import Depends, Response, status, Request, HTTPException
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from db import get_db
from schema import TokenResponse, UserResponse, UserSignUp, UserUpdate
from core import LoggerSetup, settings
from repositories import AuthRepository
from services import AuthDbService
from utils.auth_utils import authenticate_user, create_token, decode_token

logger = LoggerSetup.setup_logger(__name__)
auth_router = APIRouter(prefix="/auth", tags=["auth"])


def get_service(db: Session = Depends(get_db)) -> AuthDbService:
    logger.info("starting auth service")
    return AuthDbService(db)


@auth_router.get("/", response_model=List[UserResponse])
async def get_all_users(service: AuthDbService = Depends(get_service)):
    logger.info("getting all users")
    return service.get_all_users()


@auth_router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserSignUp, service: AuthDbService = Depends(get_service)):
    logger.info("creating user")
    return service.create_user(data)


@auth_router.put("/{id}", response_model=UserResponse)
async def update_user(data: UserUpdate, id: UUID, service: AuthDbService = Depends(get_service)):
    logger.info("Update user")
    return service.update_user(data, id)


@auth_router.post("/login", response_model=TokenResponse)
async def login(response: Response, data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    repo = AuthRepository(db)
    user = authenticate_user(data.username, data.password, repo)

    access_ttl = timedelta(minutes=settings.access_token_expires_minutes)
    refresh_ttl = timedelta(days=settings.refresh_token_expires_days)

    access_token = create_token({"sub": user.username}, access_ttl, type="access")
    refresh_token = create_token({"sub": user.username}, refresh_ttl, type="refresh")
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=int(refresh_ttl.total_seconds()),
        path="/"
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=int(access_ttl.total_seconds()),
        path="/"
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@auth_router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh(response: Response, request: Request):

    access_ttl = timedelta(minutes=settings.access_token_expires_minutes)
    refresh_ttl = timedelta(days=settings.refresh_token_expires_days)

    current_refresh_token = request.cookies.get("refresh_token")
    if not current_refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    payload = decode_token(current_refresh_token, expected_type="refresh")
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    new_access_token = create_token({"sub": username}, expires_delta=access_ttl, type="access")
    new_refresh_token = create_token({"sub": username}, expires_delta=refresh_ttl, type="refresh")

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=int(refresh_ttl.total_seconds()),
        path="/"
    )
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=int(access_ttl.total_seconds()),
        path="/"
    )
    return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token)


@auth_router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "logged out"}
