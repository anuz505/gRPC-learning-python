"""gRPC client for Auth service. FastAPI calls Auth service via gRPC."""

import grpc
from typing import Optional, Tuple
from core import settings, logger
from core.logger import LoggerSetup
import auth_pb2_grpc
import auth_pb2

logger = LoggerSetup.setup_logger("AuthGrpcClient")

# Auth Service gRPC channel configuration
AUTH_SERVICE_HOST = settings.get("auth_service_host", "localhost")
AUTH_SERVICE_PORT = settings.get("auth_service_port", 5501)


class AuthGrpcClient:
    """gRPC client for Auth service."""

    _channel: Optional[grpc.Channel] = None
    _stub: Optional[auth_pb2_grpc.AuthServiceStub] = None

    @classmethod
    def get_channel(cls) -> grpc.Channel:
        """Get or create gRPC channel."""
        if cls._channel is None:
            target = f"{AUTH_SERVICE_HOST}:{AUTH_SERVICE_PORT}"
            logger.info(f"Connecting to Auth Service at {target}")
            cls._channel = grpc.insecure_channel(target)
        return cls._channel

    @classmethod
    def get_stub(cls) -> auth_pb2_grpc.AuthServiceStub:
        """Get or create gRPC stub."""
        if cls._stub is None:
            channel = cls.get_channel()
            cls._stub = auth_pb2_grpc.AuthServiceStub(channel)
        return cls._stub

    @classmethod
    def close(cls):
        """Close gRPC channel."""
        if cls._channel is not None:
            cls._channel.close()
            cls._channel = None
            cls._stub = None

    @staticmethod
    def register(username: str, email: str, password: str) -> Tuple[bool, str, str]:
        """
        Register new user via Auth service.
        
        Returns:
            (success, user_id_or_error, message)
        """
        try:
            stub = AuthGrpcClient.get_stub()
            request = auth_pb2.RegisterRequest(
                username=username,
                email=email,
                password=password,
            )
            response = stub.Register(request, timeout=10)
            
            if response.success:
                logger.info(f"User registered via gRPC: {email}")
                return True, response.user_id, response.message
            else:
                logger.warning(f"Registration failed via gRPC: {response.error}")
                return False, "", response.error
        except grpc.RpcError as e:
            logger.error(f"Auth gRPC error (Register): {e.code()}: {e.details()}")
            return False, "", f"Auth service error: {e.details()}"
        except Exception as e:
            logger.error(f"Register error: {str(e)}")
            return False, "", str(e)

    @staticmethod
    def login(email: str, password: str) -> Tuple[bool, str, str, str, int, str]:
        """
        Login user via Auth service.
        
        Returns:
            (success, user_id, access_token, refresh_token, expires_in, error)
        """
        try:
            stub = AuthGrpcClient.get_stub()
            request = auth_pb2.LoginRequest(
                email=email,
                password=password,
            )
            response = stub.Login(request, timeout=10)
            
            if response.success:
                logger.info(f"User logged in via gRPC: {email}")
                return True, response.user_id, response.access_token, response.refresh_token, response.expires_in, ""
            else:
                logger.warning(f"Login failed via gRPC: {response.error}")
                return False, "", "", "", 0, response.error
        except grpc.RpcError as e:
            logger.error(f"Auth gRPC error (Login): {e.code()}: {e.details()}")
            return False, "", "", "", 0, f"Auth service error: {e.details()}"
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False, "", "", "", 0, str(e)

    @staticmethod
    def verify_token(token: str) -> Tuple[bool, str, str]:
        """
        Verify JWT token via Auth service.
        
        Returns:
            (is_valid, user_id, error_message)
        """
        try:
            stub = AuthGrpcClient.get_stub()
            request = auth_pb2.VerifyTokenRequest(token=token)
            response = stub.VerifyToken(request, timeout=10)
            
            return response.is_valid, response.user_id, response.error_message
        except grpc.RpcError as e:
            logger.error(f"Auth gRPC error (VerifyToken): {e.code()}: {e.details()}")
            return False, "", f"Auth service error: {e.details()}"
        except Exception as e:
            logger.error(f"VerifyToken error: {str(e)}")
            return False, "", str(e)

    @staticmethod
    def refresh_token(refresh_token: str) -> Tuple[bool, str, str, int, str]:
        """
        Refresh access token via Auth service.
        
        Returns:
            (success, access_token, user_id, expires_in, error)
        """
        try:
            stub = AuthGrpcClient.get_stub()
            request = auth_pb2.RefreshTokenRequest(refresh_token=refresh_token)
            response = stub.RefreshToken(request, timeout=10)
            
            if response.success:
                logger.info(f"Token refreshed via gRPC for user: {response.user_id}")
                return True, response.access_token, response.user_id, response.expires_in, ""
            else:
                logger.warning(f"Token refresh failed via gRPC: {response.error}")
                return False, "", "", 0, response.error
        except grpc.RpcError as e:
            logger.error(f"Auth gRPC error (RefreshToken): {e.code()}: {e.details()}")
            return False, "", "", 0, f"Auth service error: {e.details()}"
        except Exception as e:
            logger.error(f"RefreshToken error: {str(e)}")
            return False, "", "", 0, str(e)
