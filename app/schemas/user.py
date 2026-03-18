from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.models.user import UserRole

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.user

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    isActive: bool
    points: int
    createdAt: datetime

    model_config = {"from_attributes": True}  #necesario para leer desde el modelo SQLAlchemy