from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.report import Report, ReportCategory, ReportPriority
from app.schemas.report import *
from app.services.reports import create_new_report, get_all_reports, get_report_by_id, delete_report_by_id, update_report_by_id

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/", response_model=PaginatedReportsResponse)
async def get_reports(response: Response, page: int = Query(1, ge=1, description="Pagina actual"),
    page_size: int = Query(10, ge=1, description="Cantidad de registros por pagina"),
    db: AsyncSession = Depends(get_db)):

    reports, total_items = await get_all_reports(page, page_size, db)

    await _set_pagination_header(response, page_size, total_items) #Añadir a la cabecera el total paginas e items

    return PaginatedReportsResponse(
        page=page,
        page_size=page_size,
        reports=reports
    )

@router.get("/{id}", response_model=ReportResponse)
async def get_report(id: int, db: AsyncSession = Depends(get_db)):
    return await get_report_by_id(id, db)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReportResponse)
async def create_report(report_data: ReportCreate, db: AsyncSession = Depends(get_db)):
    return await create_new_report(report_data, db)


@router.patch("/{id}", response_model=ReportResponse)
async def update_report(id: int, report_data: ReportUpdate, db: AsyncSession = Depends(get_db)):
    return await update_report_by_id(id, report_data, db)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(id: int, db: AsyncSession = Depends(get_db)):
    await delete_report_by_id(id, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

#Imágenes
@router.post("/{id}/images", status_code=status.HTTP_201_CREATED)
async def upload_report_image(id: int):
    #TODO: Lógica para subir la imagen y asociarla al reporte
    return {"message": f"Imagen subida para el reporte {id}"}

@router.get("/{id}/images", response_model=list[str])
async def get_report_images(id: int):
    #TODO: Lógica para obtener las imágenes asociadas al reporte
    return [f"https://example.com/reports/{id}/images/1.jpg", f"https://example.com/reports/{id}/images/2.jpg"]

async def _set_pagination_header(response: Response, page_size: int, total: int):
    #Añadir a la cabecera el total paginas e items
    response.headers["X-Total-Pages"] = str((total + page_size - 1) // page_size)
    response.headers["X-Total-Items"] = str(total)