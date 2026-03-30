import grpc
import auth_pb2
import auth_pb2_grpc

AUTH_SERVER = "localhost:5501"


class AuthClient:
    def __init__(self):
        self.channel = grpc.insecure_channel(AUTH_SERVER)
        self.stub = auth_pb2_grpc.AuthServiceStub(self.channel)

    def verify_token(self, token):
        request = auth_pb2.VerifyTokenRequest(token=token)
        try:
            response = self.stub.VerifyToken(request)
            return response
        except grpc.RpcError as e:
            return auth_pb2.VerifyTokenResponse(
                is_valid=False, user_id="", error_message=(str(e))
            )
