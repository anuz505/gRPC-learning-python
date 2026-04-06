"""Dependency injection for getting current authenticated user via Auth service."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from services.auth_grpc_client import AuthGrpcClient
from core.logger import LoggerSetup

logger = LoggerSetup.setup_logger("AuthDependency")
bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> str:
    """
    Dependency to extract and verify current user from JWT token.
    
    Calls Auth service via gRPC to verify the token.
    
    Returns:
        user_id if token is valid
        
    Raises:
        HTTPException if token is invalid or missing
    """
    if not credentials:
        logger.warning("No authentication credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
        )

    token = credentials.credentials

    # Verify token with Auth service via gRPC
    is_valid, user_id, error_message = AuthGrpcClient.verify_token(token)

    if not is_valid:
        logger.warning(f"Token verification failed: {error_message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message or "Invalid authentication token",
        )

    logger.debug(f"User authenticated: {user_id}")
    return user_id

