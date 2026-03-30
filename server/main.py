from concurrent import futures
import grpc
from jose import jwt, JWTError, ExpiredSignatureError

try:
    from gen import auth_pb2, auth_pb2_grpc
    from core import LoggerSetup, settings
except ModuleNotFoundError:
    from server.gen import auth_pb2, auth_pb2_grpc
    from server.core import LoggerSetup, settings

logger = LoggerSetup.setup_logger("AuthService")

JWT_SECRET: str = settings.jwt_secret
JWT_ALGORITHM: str = settings.jwt_algorithm


class AuthService(auth_pb2_grpc.AuthServiceServicer):
    def VerifyToken(self, request, context):
        token = (request.token or "").strip()

        if not token:
            return auth_pb2.VerifyTokenResponse(
                is_valid=False,
                user_id="",
                error_message="Token is required",
            )

        try:
            payload: dict = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=[JWT_ALGORITHM],
            )
        except ExpiredSignatureError:
            logger.warning("Rejected expired JWT")
            return auth_pb2.VerifyTokenResponse(
                is_valid=False,
                user_id="",
                error_message="Token has expired",
            )
        except JWTError as exc:
            logger.warning("JWT validation failed: %s", exc)
            return auth_pb2.VerifyTokenResponse(
                is_valid=False,
                user_id="",
                error_message="Invalid authentication token",
            )

        # `sub` is the standard JWT claim for the subject / user identifier.
        user_id: str = payload.get("sub", "")
        if not user_id:
            return auth_pb2.VerifyTokenResponse(
                is_valid=False,
                user_id="",
                error_message="Token missing required 'sub' claim",
            )

        logger.info("Token verified for user: %s", user_id)
        return auth_pb2.VerifyTokenResponse(
            is_valid=True,
            user_id=user_id,
            error_message="",
        )


def serve():
    port = "5501"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(), server)
    server.add_insecure_port("127.0.0.1:" + port)
    server.start()
    logger.info("Auth gRPC server started at " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
