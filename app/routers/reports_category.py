from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.report import ReportCategory
from app.schemas.report_category import (
    ReportCategoriesResponse,
    ReportCategoryCreate,
    ReportCategoryResponse,
)

router = APIRouter(prefix="/reports-categories", tags=["reports-categories"])


@router.get("/", response_model=ReportCategoriesResponse)
async def get_report_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ReportCategory))
    categories = result.scalars().all()

    return ReportCategoriesResponse(categories=categories)


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=ReportCategoryResponse
)
async def create_report_category(
    category_data: ReportCategoryCreate, db: AsyncSession = Depends(get_db)
):
    new_category = ReportCategory(**category_data.model_dump())

    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)

    return new_category


@router.get("/{id}", response_model=ReportCategoryResponse)
async def get_report_category(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ReportCategory).where(ReportCategory.id == id))
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    return category


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report_category(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ReportCategory).where(ReportCategory.id == id))
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    await db.delete(category)
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()  # Volver al estado anterior al commit

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar la categoría porque tiene registros relacionados en la tabla de reportes.",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
