from pydantic import BaseModel, EmailStr


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class Login(BaseModel):
    email: EmailStr
    password: str
