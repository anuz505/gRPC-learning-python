"""Auth service business logic. Auth service owns all authentication operations."""

from typing import Optional, Tuple
from uuid import UUID as PythonUUID
from sqlalchemy.orm import Session
from repositories.auth_repo import AuthRepository
from utils.password_utils import PasswordManager
from utils.jwt_utils import JWTHandler
from db.auth_models import User
from core.logger import LoggerSetup

logger = LoggerSetup.setup_logger("AuthService")
password_manager = PasswordManager()
jwt_handler = JWTHandler()


class AuthService:
    """Business logic for authentication."""

    def __init__(self, db: Session):
        self.repo = AuthRepository(db)
        self.password_manager = password_manager
        self.jwt_handler = jwt_handler

    def register(
        self,
        username: str,
        email: str,
        password: str,
    ) -> Tuple[bool, Optional[str], str]:
        """
        Register new user.
        
        Returns:
            (success, user_id, message/error)
        """
        # Validate inputs
        if not username or not email or not password:
            logger.warning("Registration: missing required fields")
            return False, None, "Username, email, and password are required"

        if len(password) < 8:
            logger.warning("Registration: password too short")
            return False, None, "Password must be at least 8 characters"

        # Check if user already exists
        if self.repo.user_exists(email=email):
            logger.warning(f"Registration: email already exists: {email}")
            return False, None, "Email already registered"

        if self.repo.user_exists(username=username):
            logger.warning(f"Registration: username already exists: {username}")
            return False, None, "Username already taken"

        # Create user
        try:
            password_hash = self.password_manager.hash_password(password)
            user = self.repo.create_user(
                username=username,
                email=email,
                password_hash=password_hash,
            )
            logger.info(f"User registered successfully: {user.email}")
            return True, str(user.id), "User registered successfully"
        except Exception as e:
            logger.error(f"Registration failed: {str(e)}")
            return False, None, "Registration failed"

    def login(
        self,
        email: str,
        password: str,
    ) -> Tuple[bool, Optional[str], Optional[str], Optional[str], int, str]:
        """
        Login user and return tokens.
        
        Returns:
            (success, user_id, access_token, refresh_token, expires_in, message/error)
        """
        if not email or not password:
            logger.warning("Login: missing email or password")
            return False, None, None, None, 0, "Email and password are required"

        # Get user
        user = self.repo.get_user_by_email(email)
        if not user:
            logger.warning(f"Login: user not found: {email}")
            return False, None, None, None, 0, "Invalid credentials"

        # Verify password
        if not self.password_manager.verify_password(password, user.password):
            logger.warning(f"Login: invalid password for user: {email}")
            return False, None, None, None, 0, "Invalid credentials"

        # Generate tokens
        try:
            access_token, expires_in = self.jwt_handler.create_access_token(str(user.id))
            refresh_token = self.jwt_handler.create_refresh_token(str(user.id))
            logger.info(f"User logged in: {email}")
            return True, str(user.id), access_token, refresh_token, expires_in, "Login successful"
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False, None, None, None, 0, "Login failed"

    def verify_token(self, token: str) -> Tuple[bool, Optional[str], str]:
        """
        Verify access token.
        
        Returns:
            (is_valid, user_id, error_message)
        """
        if not token:
            logger.warning("Token verification: token is empty")
            return False, None, "Token is required"

        user_id = self.jwt_handler.verify_access_token(token)
        if not user_id:
            logger.warning("Token verification: token invalid or expired")
            return False, None, "Token is invalid or expired"

        # Enforce: verify user still exists
        try:
            user_uuid = PythonUUID(user_id)
            user = self.repo.get_user_by_id(user_uuid)
            if not user:
                logger.warning(f"Token verification: user not found: {user_id}")
                return False, None, "User not found"

            logger.debug(f"Token verified for user: {user_id}")
            return True, user_id, ""
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            return False, None, "Token verification failed"

    def refresh_access_token(self, refresh_token: str) -> Tuple[bool, Optional[str], Optional[str], int, str]:
        """
        Refresh access token using refresh token.
        
        Returns:
            (success, access_token, user_id, expires_in, error_message)
        """
        if not refresh_token:
            logger.warning("Refresh token: token is empty")
            return False, None, None, 0, "Refresh token is required"

        user_id = self.jwt_handler.verify_refresh_token(refresh_token)
        if not user_id:
            logger.warning("Refresh token: token invalid or expired")
            return False, None, None, 0, "Refresh token is invalid or expired"

        try:
            # Verify user still exists
            user_uuid = PythonUUID(user_id)
            user = self.repo.get_user_by_id(user_uuid)
            if not user:
                logger.warning(f"Refresh token: user not found: {user_id}")
                return False, None, None, 0, "User not found"

            # Generate new access token
            access_token, expires_in = self.jwt_handler.create_access_token(user_id)
            logger.info(f"Access token refreshed for user: {user_id}")
            return True, access_token, user_id, expires_in, ""
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            return False, None, None, 0, "Token refresh failed"

