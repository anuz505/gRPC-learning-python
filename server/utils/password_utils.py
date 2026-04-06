"""Password hashing utilities using argon2."""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash


class PasswordManager:
    """Handles password hashing and verification."""

    def __init__(self):
        self.hasher = PasswordHasher()

    def hash_password(self, password: str) -> str:
        """
        Hash password using argon2.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return self.hasher.hash(password)

    def verify_password(self, password: str, hash_: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            password: Plain text password
            hash_: Password hash to verify against
            
        Returns:
            True if password matches hash, False otherwise
        """
        try:
            self.hasher.verify(hash_, password)
            return True
        except (VerifyMismatchError, InvalidHash):
            return False
