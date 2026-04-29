from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.db.database import get_db
from app.models.report import Report, ReportCategory, ReportPriority
from app.schemas.report import *
from app.services.reports import create_new_report, get_all_reports, get_report_by_id, delete_report_by_id, update_report_by_id

router = APIRouter(prefix="/reports", tags=["reports"])

def report_with_relations(): #Se cargan las relaciones desde el modelo
    return [
        selectinload(Report.user), #selectinload carga la relación en la misma consulta(Pero ejecuta más de una query) : Select * from report; Select * from user where user.id in (1,2,3)
        selectinload(Report.resolvedBy),
        selectinload(Report.category)
    ]
#joinedload carga la relación con un join (Una sola consulta, pero puede traer datos duplicados) : Select * from report join user on report.userId = user.id 

@router.get("/category-list", response_model=ReportCategoriesResponse)
async def get_report_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ReportCategory))
    categories = result.scalars().all()

    return ReportCategoriesResponse(categories=categories)

@router.get("/priority-list", response_model=list[ReportPriority])
async def get_report_priorities():
    return list(ReportPriority)

@router.get("/", response_model=PaginatedReportsResponse)
async def get_reports(response: Response, page: int = Query(1, ge=1, description="Pagina actual"),
    page_size: int = Query(10, ge=1, description="Cantidad de registros por pagina"),
    db: AsyncSession = Depends(get_db)):

    reports = await get_all_reports(response, page, page_size, db)

    return PaginatedReportsResponse(
        page=page,
        page_size=page_size,
        reports=reports
    )

@router.get("/id/{report_id}", response_model=ReportResponse)
async def get_report(response: Response, report_id: int, db: AsyncSession = Depends(get_db)):
    return await get_report_by_id(response, report_id, db)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReportResponse)
async def create_report(report_data: ReportCreate, db: AsyncSession = Depends(get_db)):
    return await create_new_report(report_data, db)


@router.patch("/id/{report_id}", response_model=ReportResponse)
async def update_report(report_id: int, report_data: ReportUpdate, db: AsyncSession = Depends(get_db)):
    return await update_report_by_id(report_id, report_data, db)

@router.delete("/id/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(report_id: int, db: AsyncSession = Depends(get_db)):
    await delete_report_by_id(report_id, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)