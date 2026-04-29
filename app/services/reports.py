from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func
from app.db.database import get_db
from app.models.report import Report, ReportCategory, ReportPriority
from app.schemas.report import *

def report_with_relations(): #Se cargan las relaciones desde el modelo
    return [
        selectinload(Report.user), #selectinload carga la relación en la misma consulta(Pero ejecuta más de una query) : Select * from report; Select * from user where user.id in (1,2,3)
        selectinload(Report.resolvedBy),
        selectinload(Report.category)
    ]
#joinedload carga la relación con un join (Una sola consulta, pero puede traer datos duplicados) : Select * from report join user on report.userId = user.id 

async def get_all_reports(response: Response, page: int, page_size: int, db: AsyncSession):
    offset = (page - 1) * page_size 

    main_query = select(Report)
    await _set_pagination_header(db, response, page_size, main_query) #Añadir a la cabecera el total paginas e items

    result = await db.execute(
        main_query
        .options(*report_with_relations()) #Se añaden las relaciones con options y se descomprime la lista con * (convierte el array en argumentos separados)
        .offset(offset)
        .limit(page_size) # offset y limit para paginación
        .order_by(Report.id))  

    reports = result.scalars().all() #Todos en una lista

    return reports

async def get_report_by_id(response: Response, report_id: int, db: AsyncSession):
    main_query = select(Report).where(Report.id == report_id)
    await _set_pagination_header(db, response, 1, main_query) #Añadir a la cabecera el total paginas e items

    result = await db.execute(
        main_query
        .options(*report_with_relations())
    )
    report = result.scalar_one_or_none() #Un resultado o None

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} no encontrado"
        )
    
    return report

async def create_new_report(report_data: ReportCreate, db: AsyncSession):
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
    report = result.scalar_one_or_none()

    return report

async def update_report_by_id(report_id: int, report_data: ReportUpdate, db: AsyncSession):
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
    report = result.scalar_one()

    return report

async def delete_report_by_id(report_id: int, db: AsyncSession):
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} no encontrado"
        )
    
    await db.delete(report)
    await db.commit()

async def _set_pagination_header(db: AsyncSession, response: Response, page_size: int, query: any):
    #Obtener el total de registros
    count_query = select(func.count()).select_from(query.subquery()) #func.count() es como COUNT(*) y la subquery para contar sin obtener todas la informacion
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    #Añadir a la cabecera el total paginas e items
    response.headers["X-Total-Pages"] = str((total + page_size - 1) // page_size)
    response.headers["X-Total-Items"] = str(total)