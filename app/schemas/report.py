from pydantic import BaseModel
from datetime import datetime
from app.models.report import ReportStatus, ReportPriority
from app.schemas.user import UserBasicResponse
from app.schemas.report_category import ReportCategoryResponse

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

class ReportStatusResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}

class ReportImagesResponse(BaseModel):
    num_images: int
    images: list[ImageSchema]

class ImageSchema(BaseModel):
    id: int
    url: str

class ReportCommentResponse(BaseModel):
    id: int
    content: str
    createdAt: datetime
    user: UserBasicResponse

    model_config = {"from_attributes": True}

class ReportCommentsResponse(BaseModel):
    num_comments: int
    comments: list[ReportCommentResponse]