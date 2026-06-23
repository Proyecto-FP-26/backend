from datetime import datetime

from pydantic import BaseModel


class UserLogin(BaseModel):
    username: str
    password: str


class UserSessionCreate(BaseModel):
    userId: int
    deviceInfo: str
    ip: str
    rememberMe: bool
    expiresAt: datetime


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
