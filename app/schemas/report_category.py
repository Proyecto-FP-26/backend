from pydantic import BaseModel

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