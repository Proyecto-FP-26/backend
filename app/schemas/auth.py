from pydantic import BaseModel
from datetime import datetime
from app.models.user import UserRole

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    isActive: bool
    points: int
    createdAt: datetime

    model_config = {"from_attributes": True}

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
