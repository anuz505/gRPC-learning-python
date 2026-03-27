from concurrent import futures
import logging
import grpc
import users_pb2
import users_pb2_grpc


class UserService(users_pb2_grpc.UserServiceServicer):
    def SayHelloUser(self, request, context):
        print("Received username:", request.username)
        message = "Hello, %s!" % request.username
        print("Sending message:", message)
        return users_pb2.HelloReply(message=message)

    def GetUsers(self, request, context):
        return users_pb2.GetUsersResponse(
            users=[
                users_pb2.User(
                    id="2",
                    name="anuj",
                    username="anuz505",
                    email="anuzb50gmail.com",
                    password="test123"
                ),
                users_pb2.User(
                    id="1",
                    name="anuz",
                    username="anujb364",
                    email="anujb364@gmail.com",
                    password="test123"
                )
            ]
        )


def serve():
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    users_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("server started at " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()
