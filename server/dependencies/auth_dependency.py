from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
try:
    from gen.auth_pb2 import VerifyTokenResponse
except ModuleNotFoundError:
    from server.gen.auth_pb2 import VerifyTokenResponse
from dependencies import AuthClient

auth_client = AuthClient()
bearer_scheme = HTTPBearer()  # reads "Authorization: Bearer <token>"


def get_current_user(credentials=Depends(bearer_scheme)):
    token = credentials.credentials
    resp: VerifyTokenResponse = auth_client.verify_token(token)
    if not resp.is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=resp.error_message or "Invalid authentication token",
        )
    return resp.user_id
