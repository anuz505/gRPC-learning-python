from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from auth_pb2 import VerifyTokenResponse
from services import AuthClient

auth_client = AuthClient()
bearer_scheme = HTTPBearer()


def get_current_user(credentials=Depends(bearer_scheme)):
    token = credentials.credentials
    resp: VerifyTokenResponse = auth_client.verify_token(token)
    if not resp.is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=resp.error_message or "Invalid authentication token",
        )
    return resp.user_id
