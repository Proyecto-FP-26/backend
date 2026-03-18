from pydantic import BaseModel
from datetime import datetime
from app.models.report import ReportStatus, ReportPriority
from app.schemas.user import UserResponse

class ReportCreate(BaseModel):
    title: str
    description: str
    latitude: float
    longitude: float
    priority: ReportPriority = ReportPriority.mid
    categoryId: int
    userId: int

class ReportUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    status: ReportStatus | None = None
    priority: ReportPriority | None = None
    categoryId: int | None = None
    resolvedById: int | None = None

class ReportResponse(BaseModel):
    id: int
    title: str
    description: str
    latitude: float
    longitude: float
    status: ReportStatus
    priority: ReportPriority
    userId: int
    resolvedById: int | None
    categoryId: int
    createdAt: datetime
    updatedAt: datetime
    user: UserResponse | None = None
    resolvedBy: UserResponse | None = None

    model_config = {"from_attributes": True}