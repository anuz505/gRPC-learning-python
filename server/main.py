"""Auth gRPC Server - Owns all authentication logic."""

from concurrent import futures
import grpc

try:
    # from gen import auth_pb2, auth_pb2_grpc
    import auth_pb2
    import auth_pb2_grpc

    from services.auth_service import AuthService
    from db.db_models import SessionLocal, engine, Base
    from core import LoggerSetup, settings
except ModuleNotFoundError:
    from server.gen import auth_pb2, auth_pb2_grpc
    from server.services.auth_service import AuthService
    from server.db.db_models import SessionLocal, engine, Base
    from server.core import LoggerSetup, settings

logger = LoggerSetup.setup_logger("AuthServiceServer")
GRPC_PORT = 5501


class AuthServiceGrpc(auth_pb2_grpc.AuthServiceServicer):
    """gRPC implementation of Auth service."""

    def Register(self, request: auth_pb2.RegisterRequest, context) -> auth_pb2.RegisterResponse:
        """Register a new user."""
        logger.info(f"Register request: {request.username}")

        db = SessionLocal()
        try:
            auth_service = AuthService(db)
            success, user_id, message = auth_service.register(
                username=request.username,
                email=request.email,
                password=request.password,
            )
            
            if success:
                logger.info(f"Registration successful: {request.email}")
                return auth_pb2.RegisterResponse(
                    success=True,
                    user_id=user_id,
                    message=message,
                    error="",
                )
            else:
                logger.warning(f"Registration failed: {message}")
                return auth_pb2.RegisterResponse(
                    success=False,
                    user_id="",
                    message="",
                    error=message,
                )
        except Exception as e:
            logger.error(f"Register RPC error: {str(e)}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.RegisterResponse(
                success=False,
                user_id="",
                message="",
                error="Internal server error",
            )
        finally:
            db.close()

    def Login(self, request: auth_pb2.LoginRequest, context) -> auth_pb2.LoginResponse:
        """Login user and return tokens."""
        logger.info(f"Login request: {request.email}")
        
        db = SessionLocal()
        try:
            auth_service = AuthService(db)
            success, user_id, access_token, refresh_token, expires_in, message = auth_service.login(
                email=request.email,
                password=request.password,
            )
            
            if success:
                logger.info(f"Login successful: {request.email}")
                return auth_pb2.LoginResponse(
                    success=True,
                    user_id=user_id,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_type="Bearer",
                    expires_in=expires_in,
                    message=message,
                    error="",
                )
            else:
                logger.warning(f"Login failed: {message}")
                return auth_pb2.LoginResponse(
                    success=False,
                    user_id="",
                    access_token="",
                    refresh_token="",
                    token_type="",
                    expires_in=0,
                    message="",
                    error=message,
                )
        except Exception as e:
            logger.error(f"Login RPC error: {str(e)}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.LoginResponse(
                success=False,
                user_id="",
                access_token="",
                refresh_token="",
                token_type="",
                expires_in=0,
                message="",
                error="Internal server error",
            )
        finally:
            db.close()

    def VerifyToken(self, request: auth_pb2.VerifyTokenRequest, context) -> auth_pb2.VerifyTokenResponse:
        """Verify JWT access token."""
        logger.debug("VerifyToken request")
        token = (request.token or "").strip()
        
        if not token:
            logger.warning("VerifyToken: empty token")
            return auth_pb2.VerifyTokenResponse(
                is_valid=False,
                user_id="",
                error_message="Token is required",
            )
        
        db = SessionLocal()
        try:
            auth_service = AuthService(db)
            is_valid, user_id, error_message = auth_service.verify_token(token)
            
            return auth_pb2.VerifyTokenResponse(
                is_valid=is_valid,
                user_id=user_id or "",
                error_message=error_message or "",
            )
        except Exception as e:
            logger.error(f"VerifyToken RPC error: {str(e)}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.VerifyTokenResponse(
                is_valid=False,
                user_id="",
                error_message="Internal server error",
            )
        finally:
            db.close()

    def RefreshToken(self, request: auth_pb2.RefreshTokenRequest, context) -> auth_pb2.RefreshTokenResponse:
        """Refresh access token using refresh token."""
        logger.info("RefreshToken request")
        
        db = SessionLocal()
        try:
            auth_service = AuthService(db)
            success, access_token, user_id, expires_in, error = auth_service.refresh_access_token(
                refresh_token=request.refresh_token,
            )
            
            if success:
                logger.info(f"Token refreshed for user: {user_id}")
                return auth_pb2.RefreshTokenResponse(
                    success=True,
                    access_token=access_token,
                    user_id=user_id,
                    expires_in=expires_in,
                    error="",
                )
            else:
                logger.warning(f"Token refresh failed: {error}")
                return auth_pb2.RefreshTokenResponse(
                    success=False,
                    access_token="",
                    user_id="",
                    expires_in=0,
                    error=error,
                )
        except Exception as e:
            logger.error(f"RefreshToken RPC error: {str(e)}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.RefreshTokenResponse(
                success=False,
                access_token="",
                user_id="",
                expires_in=0,
                error="Internal server error",
            )
        finally:
            db.close()


def serve():
    """Start the gRPC server."""
    # Create database tables
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

    # Create gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(
        AuthServiceGrpc(),
        server,
    )
    
    server.add_insecure_port(f"[::]:{GRPC_PORT}")
    logger.info(f"Auth Service gRPC server listening on port {GRPC_PORT}")
    
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    logger.info("Starting Auth Service")
    serve()
