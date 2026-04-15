from pydantic import BaseModel
from datetime import datetime
from app.models.report import ReportStatus, ReportPriority
from app.schemas.user import UserResponse, UserBasicResponse

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
    category: ReportCategoryResponse
    createdAt: datetime
    updatedAt: datetime
    user: UserBasicResponse | None = None
    resolvedBy: UserBasicResponse | None = None

    model_config = {"from_attributes": True}

class PaginatedReportsResponse(BaseModel):
    page: int
    page_size: int
    reports: list[ReportResponse]

class ReportCategoriesResponse(BaseModel):
    categories: list[ReportCategoryResponse] | None = None

class ReportCategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    icon: str | None = None

    model_config = {"from_attributes": True}

class ReportCategoryCreate(BaseModel):
    name: str
    description: str | None = None
    icon: str | None = None

class ReportCategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    icon: str | None = None

class ReportCategoryCreate(BaseModel):
    name: str
    description: str | None = None
    icon: str | None = None

class ReportStatusResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}