from fastapi import APIRouter, Depends, status, Query, Response, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.report import *
from app.models.report import Report
from app.services import reports as report_services
from app.dependencies import reports as report_dependencies
from app.dependencies import auth as auth_dependencies


router = APIRouter(prefix="/reports", tags=["reports"])

async def _set_pagination_header(response: Response, page_size: int, total: int):
    #Añadir a la cabecera el total paginas e items
    response.headers["X-Total-Pages"] = str((total + page_size - 1) // page_size)
    response.headers["X-Total-Items"] = str(total)

@router.get("/", response_model=PaginatedReportsResponse)
async def get_reports(response: Response, page: int = Query(1, ge=1, description="Pagina actual"),
    page_size: int = Query(10, ge=1, description="Cantidad de registros por pagina"),
    db: AsyncSession = Depends(get_db)):

    reports, total_items = await report_services.get_all_reports(page, page_size, db)

    await _set_pagination_header(response, page_size, total_items) #Añadir a la cabecera el total paginas e items

    return PaginatedReportsResponse(
        page=page,
        page_size=page_size,
        reports=reports
    )

@router.get("/{id}", response_model=ReportResponse)
async def get_report(id: int, db: AsyncSession = Depends(get_db)):
    return await report_services.get_report_by_id(id, db)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReportResponse)
async def create_report(report_data: ReportCreate, db: AsyncSession = Depends(get_db)):
    return await report_services.create_new_report(report_data, db)


@router.patch("/{id}", response_model=ReportResponse)
async def update_report(id: int, report_data: ReportUpdate, db: AsyncSession = Depends(get_db)):
    return await report_services.update_report_by_id(id, report_data, db)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT) #TODO: Al borrar un reporte, borrar sus imagenes y comentarios asociados
async def delete_report(id: int, db: AsyncSession = Depends(get_db)):
    await report_services.delete_report_by_id(id, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

#Imágenes #TODO: Crear endpoint para multiples imagenes
@router.post("/{id}/images", status_code=status.HTTP_201_CREATED) #TODO: Añadir limites de cantidad y validaciones de tipo de archivo
async def upload_report_image(file: UploadFile = File(...), report: Report = Depends(report_dependencies.valid_report_id), db: AsyncSession = Depends(get_db), current_user=Depends(auth_dependencies.Get_Current_User())):
    saved_files = await report_services.save_images([file], report.id, current_user[0].id, db)
    return {"message": f"Imagen subida para el reporte {report.title} | {report.id}",
            "saved_files": saved_files}

@router.get("/{id}/images", response_model=ReportImagesResponse)
async def get_report_images(report: Report = Depends(report_dependencies.valid_report_id), db: AsyncSession = Depends(get_db)):
    images = await report_services.get_report_images(report.id, db)
    return ReportImagesResponse(num_images=len(images), images=images)

@router.delete("/{id}/image/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report_image(image_id: int, report: Report = Depends(report_dependencies.valid_report_id), db: AsyncSession = Depends(get_db)):
    await report_services.delete_report_image(report.id, image_id, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete("/{id}/images", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_report_images(report: Report = Depends(report_dependencies.valid_report_id), db: AsyncSession = Depends(get_db)):
    await report_services.delete_all_report_images(report.id, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

#Comentarios
@router.get("/{id}/comments", response_model=ReportCommentsResponse)
async def get_report_comments(report: Report = Depends(report_dependencies.valid_report_id), db: AsyncSession = Depends(get_db)):
    comments = await report_services.get_report_comments(report.id, db)
    return ReportCommentsResponse(num_comments=len(comments), comments=comments)

@router.post("/{id}/comments", status_code=status.HTTP_201_CREATED, response_model=ReportCommentResponse)
async def create_report_comment(comment_data: str, report: Report = Depends(report_dependencies.valid_report_id), db: AsyncSession = Depends(get_db), current_user=Depends(auth_dependencies.Get_Current_User())):
    comment = await report_services.create_report_comment(report.id, comment_data, current_user[0].id, db)
    return comment

@router.delete("/{id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report_comment(comment_id: int, report: Report = Depends(report_dependencies.valid_report_id), db: AsyncSession = Depends(get_db), current_user=Depends(auth_dependencies.Get_Current_User())):
    await report_services.delete_report_comment(report.id, comment_id, current_user[0].id, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

