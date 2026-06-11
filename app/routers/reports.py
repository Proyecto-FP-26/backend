from fastapi import APIRouter, Depends, status, Query, Response, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.dependencies.auth import Get_Current_User
from app.schemas.report import *
from app.models.report import Report
from app.services.reports import create_new_report, get_all_reports, get_report_by_id, delete_report_by_id, update_report_by_id, save_files
from app.dependencies.reports import valid_report_id


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
async def upload_report_image(file: UploadFile = File(...), report: Report = Depends(valid_report_id), db: AsyncSession = Depends(get_db), current_user=Depends(Get_Current_User())):
    saved_files = await save_files([file], report.id, current_user[0].id, db)
    return {"message": f"Imagen subida para el reporte {report.title} | {report.id}",
            "saved_files": saved_files}

@router.get("/{id}/images", response_model=list[str])
async def get_report_images(report: Report = Depends(valid_report_id)):
    #TODO: Lógica para obtener las imágenes asociadas al reporte
    return [f"https://example.com/reports/{report.id}/images/1.jpg", f"https://example.com/reports/{report.id}/images/2.jpg"]

async def _set_pagination_header(response: Response, page_size: int, total: int):
    #Añadir a la cabecera el total paginas e items
    response.headers["X-Total-Pages"] = str((total + page_size - 1) // page_size)
    response.headers["X-Total-Items"] = str(total)