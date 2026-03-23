from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.db.database import get_db
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportUpdate, ReportResponse

router = APIRouter(prefix="/reports", tags=["reports"])

def report_with_relations(): #Se cargan las relaciones desde el modelo
    return [
        selectinload(Report.user), #selectinload carga la relación en la misma consulta(Pero ejecuta más de una query) : Select * from report; Select * from user where user.id in (1,2,3)
        selectinload(Report.resolvedBy),
    ]
#joinedload carga la relación con un join (Una sola consulta, pero puede traer datos duplicados) : Select * from report join user on report.userId = user.id 

@router.get("/", response_model=list[ReportResponse])
async def get_reports(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Report).options(*report_with_relations()) #Se añaden las relaciones con options y se descomprime la lista con * (convierte el array en argumentos separados)
    )
    return result.scalars().all() #Todos en una lista

@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Report)
        .options(*report_with_relations())
        .where(Report.id == report_id)
    )
    report = result.scalar_one_or_none() #Un resultado o None

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} no encontrado"
        )

    return report

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReportResponse)
async def create_report(report_data: ReportCreate, db: AsyncSession = Depends(get_db)):
    new_report = Report(**report_data.model_dump()) #Convierte ReportCreate a diccionario y lo pasa al constructor de Report

    db.add(new_report) #pendiente enviar db
    await db.commit() #confirma y guarda en db
    await db.refresh(new_report) #actualiza con los datos de la db generados automaticamente

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
        .where(Report.id == report_id)
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} no encontrado"
        )

    update_data = report_data.model_dump(exclude_unset=True) #model_dump: convierte el modelo en un diccionario | exclude_unset : Actualiza solo los campos que vienen en el body, ignora los None (sin esto, actualizaría todos los campos no enviados a None (valor por defecto de ReportUpdate))
    for field, value in update_data.items():
        setattr(report, field, value)

    await db.commit()
    #await db.refresh(report)

    result = await db.execute(
        select(Report)
        .options(*report_with_relations())
        .where(Report.id == report_id)
    )
    return result.scalar_one()