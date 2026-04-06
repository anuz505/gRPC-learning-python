"""FastAPI Auth routes - All auth operations delegated to Auth service via gRPC."""

from fastapi import APIRouter, HTTPException, status, Response, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Annotated
from services.auth_grpc_client import AuthGrpcClient
from core.logger import LoggerSetup

logger = LoggerSetup.setup_logger("AuthRoutes")
auth_router = APIRouter(prefix="/auth", tags=["auth"])


# === Schemas ===
class RegisterRequest(BaseModel):
    """User registration request."""
    username: str
    email: str
    password: str


class RegisterResponse(BaseModel):
    """User registration response."""
    success: bool
    user_id: str = ""
    message: str = ""


class LoginResponse(BaseModel):
    """Login response with tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int  # seconds


class TokenRefreshRequest(BaseModel):
    """Token refresh request."""
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    """Token refresh response."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int  # seconds


# === Routes ===
@auth_router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user account. Password must be at least 8 characters.",
)
async def register(body: RegisterRequest) -> RegisterResponse:
    """
    Register a new user account.
    
    - **username**: Unique username
    - **email**: Unique email address
    - **password**: At least 8 characters
    """
    logger.info(f"Register request: {body.email}")

    success, user_id, message = AuthGrpcClient.register(
        username=body.username,
        email=body.email,
        password=body.password,
    )

    if success:
        logger.info(f"User registered: {body.email}")
        return RegisterResponse(
            success=True,
            user_id=user_id,
            message=message,
        )
    else:
        logger.warning(f"Registration failed: {message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


@auth_router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Login with email and password to get JWT tokens.",
)
async def login(body: Annotated[OAuth2PasswordRequestForm, Depends()]) -> LoginResponse:
    """
    Login user and receive JWT tokens.
    
    - **username** (deprecated): Use email instead
    - **password**: User password
    
    Returns access_token (short-lived) and refresh_token (long-lived).
    """
    # OAuth2PasswordRequestForm uses 'username' field, but we treat it as email
    email = body.username
    password = body.password

    logger.info(f"Login request: {email}")

    success, user_id, access_token, refresh_token, expires_in, error = AuthGrpcClient.login(
        email=email,
        password=password,
    )

    if success:
        logger.info(f"User logged in: {email}")
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=expires_in,
        )
    else:
        logger.warning(f"Login failed: {error}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error or "Invalid credentials",
        )


@auth_router.post(
    "/refresh",
    response_model=TokenRefreshResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Use refresh token to get a new access token.",
)
async def refresh_token(body: TokenRefreshRequest) -> TokenRefreshResponse:
    """
    Refresh the access token using refresh token.
    
    - **refresh_token**: Long-lived refresh token from login
    
    Returns a new access token.
    """
    logger.info("Refresh token request")

    success, access_token, user_id, expires_in, error = AuthGrpcClient.refresh_token(
        refresh_token=body.refresh_token,
    )

    if success:
        logger.info(f"Token refreshed for user: {user_id}")
        return TokenRefreshResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=expires_in,
        )
    else:
        logger.warning(f"Token refresh failed: {error}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error or "Invalid refresh token",
        )


@auth_router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "logged out"}
