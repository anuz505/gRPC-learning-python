"""JWT token generation and validation utilities for Auth service."""

from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError
from typing import Optional, Dict, Any
from core import settings


class JWTHandler:
    """Handles JWT token creation and validation."""

    def __init__(self):
        self.secret = settings.jwt_secret
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.access_token_expires_minutes
        self.refresh_token_expire_days = settings.refresh_token_expires_days

    def create_access_token(self, user_id: str) -> tuple[str, int]:
        """
        Create access token.
        
        Returns:
            tuple: (token, expires_in_seconds)
        """
        expires_in_seconds = self.access_token_expire_minutes * 60
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "sub": user_id,
            "type": "access",
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }
        token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
        return token, expires_in_seconds

    def create_refresh_token(self, user_id: str) -> str:
        """Create refresh token."""
        expire = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }
        token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
        return token

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode token.
        
        Returns:
            dict with token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
            )
            return payload
        except ExpiredSignatureError:
            return None
        except JWTError:
            return None

    def verify_access_token(self, token: str) -> Optional[str]:
        """
        Verify access token and return user_id.
        
        Returns:
            user_id if valid, None otherwise
        """
        payload = self.verify_token(token)
        if not payload or payload.get("type") != "access":
            return None
        return payload.get("sub")

    def verify_refresh_token(self, token: str) -> Optional[str]:
        """
        Verify refresh token and return user_id.
        
        Returns:
            user_id if valid, None otherwise
        """
        payload = self.verify_token(token)
        if not payload or payload.get("type") != "refresh":
            return None
        return payload.get("sub")
