from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.db.database import get_db
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportUpdate, ReportResponse

router = APIRouter(prefix="/reports", tags=["reports"])


def report_with_relations():
    #Opciones de carga compartidas entre endpoints de lectura.
    return [
        selectinload(Report.user),
        selectinload(Report.resolvedBy),
    ]


@router.get("/", response_model=list[ReportResponse])
async def get_reports(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Report).options(*report_with_relations())
    )
    return result.scalars().all()


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Report)
        .options(*report_with_relations())
        .where(Report.id == report_id)
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} no encontrado"
        )

    return report


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReportResponse)
async def create_report(report_data: ReportCreate, db: AsyncSession = Depends(get_db)):
    new_report = Report(**report_data.model_dump())

    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)

    #refresh no carga relaciones, hay que recargar con selectinload
    result = await db.execute(
        select(Report)
        .options(*report_with_relations())
        .where(Report.id == new_report.id)
    )
    return result.scalar_one()


@router.patch("/{report_id}", response_model=ReportResponse)
async def update_report(report_id: int, report_data: ReportUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Report)
        .options(*report_with_relations())
        .where(Report.id == report_id)
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} no encontrado"
        )

    #Actualiza solo los campos que vienen en el body, ignora los None
    update_data = report_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(report, field, value)

    await db.commit()
    await db.refresh(report)

    result = await db.execute(
        select(Report)
        .options(*report_with_relations())
        .where(Report.id == report_id)
    )
    return result.scalar_one()