from __future__ import print_function
import logging
import os
import grpc
import users_pb2
import users_pb2_grpc


def run():
    target = os.getenv("GRPC_TARGET", "localhost:50051")
    with grpc.insecure_channel(target) as channel:
        grpc.channel_ready_future(channel).result(timeout=10)
        stub = users_pb2_grpc.UserServiceStub(channel)
        response = stub.SayHelloUser(
            users_pb2.SayHelloUserRequest(
                username="anuz505",
                email="anuz505@gmail.com"
            )
        )
        print("Client received: " + response.message)

        all_users_response = stub.GetUsers(users_pb2.GetUsersRequest())
        for user in all_users_response.users:
            print(user.id, user.username, user.email)


if __name__ == "__main__":
    logging.basicConfig()
    run()
