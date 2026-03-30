from concurrent import futures
from pathlib import Path
import sys

import grpc

# Allow running this file directly with `python app.py` by adding `server/` to import path.
SERVER_ROOT = Path(__file__).resolve().parent.parent
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))
GEN_ROOT = SERVER_ROOT / "gen"
if str(GEN_ROOT) not in sys.path:
    sys.path.insert(0, str(GEN_ROOT))

from gen import users_pb2, users_pb2_grpc
# , auth_pb2_grpc, auth_pb2
# from fastapi import FastAPI, Depends, HTTPException, status
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db import get_repository
from core import LoggerSetup

logger = LoggerSetup.setup_logger("UserService")


class UserService(users_pb2_grpc.UserServiceServicer):
    def SayHelloUser(self, request, context):
        print("Received username:", request.username)
        message = "Hello, %s!" % request.username
        print("Sending message:", message)
        return users_pb2.SayHelloUserResponse(message=message)

    def GetUsers(self, request, context):
        try:
            with get_repository() as repo:
                users = repo.get_all_users()

                users_list = [
                    users_pb2.User(
                        id=str(user.id),
                        username=user.username,
                        email=user.email,
                    ) for user in users
                ]
                return users_pb2.GetUsersResponse(users=users_list)
        except Exception as error:
            context.set_details(str(error))
            logger.error(str(error))
            context.set_code(grpc.StatusCode.INTERNAL)
            # context.abort(grpc.StatusCode.INTERNAL, str(error))

            return users_pb2.GetUsersResponse()


def serve():
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    users_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    logger.info("server started at " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
