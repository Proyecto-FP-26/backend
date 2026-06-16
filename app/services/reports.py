from fastapi import HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func
from app.models.report import Report, ReportImage, Comment as ReportComment
from app.schemas.report import *
from app.core.settings import settings
from pathlib import Path
from uuid import uuid4
from shutil import copyfileobj

uploads_root = settings.UPLOADS_ROOT

def report_with_relations(): #Se cargan las relaciones desde el modelo
    return [
        selectinload(Report.user), #selectinload carga la relación en la misma consulta(Pero ejecuta más de una query) : Select * from report; Select * from user where user.id in (1,2,3)
        selectinload(Report.resolvedBy),
        selectinload(Report.category)
    ]
#joinedload carga la relación con un join (Una sola consulta, pero puede traer datos duplicados) : Select * from report join user on report.userId = user.id 

async def get_all_reports(page: int, page_size: int, db: AsyncSession):
    #Obtener el total de registros
    count_query = select(func.count()).select_from(Report)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    if page == 0 or page_size == 0:
        main_query = (
            select(Report)
            .options(*report_with_relations())
            .order_by(Report.id)
        )
    else:
        offset = (page - 1) * page_size 

        #Obtener los registros paginados con relaciones
        main_query = (
            select(Report)
            .options(*report_with_relations())
            .offset(offset)
            .limit(page_size)
            .order_by(Report.id)
        )
    result = await db.execute(main_query)

    reports = result.scalars().all() #Todos en una lista

    return reports, total

async def get_report_by_id(report_id: int, db: AsyncSession):
    main_query = select(Report).where(Report.id == report_id).options(*report_with_relations())
    result = await db.execute(main_query)

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

async def save_images(files: list[UploadFile], report_id: int, user_id: int, db: AsyncSession):
    saved_files: list[Path] = []
    db_objects: list[ReportImage] = []
    ALLOWED_MIMES = ["image/jpeg", "image/png", "image/webp"]

    #Crear carpetas
    user_folder = Path(uploads_root) / f"{user_id}"
    report_folder = user_folder / f"{report_id}"
    user_folder.mkdir(parents=True, exist_ok=True)
    report_folder.mkdir(parents=True, exist_ok=True)

    #Guardar cada archivo
    for file in files:
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid4()}{file_extension}"
        file_path = report_folder / unique_filename
        url_file_path = file_path.as_posix()

        if file.content_type not in ALLOWED_MIMES:
            saved_files.append(f"Archivo {file.filename} con tipo {file.content_type} no permitido") #HACK: Temporal, cambiar por mensaje de error o algo similar
            continue #Ignorar archivos con tipo no permitido

        with file_path.open("wb") as buffer:
            try:
                copyfileobj(file.file, buffer)
            except Exception as e:
                #Borrar imagenes ya guardadas
                for saved_file in saved_files:
                    if saved_file.exists():
                        saved_file.unlink()

                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error al guardar el archivo: {e}"
                ) 
            
        #Guardar la ruta y preparar el objeto de base de datos
        saved_files.append(url_file_path)
        
        new_image = ReportImage(reportId=report_id, imageUrl=url_file_path)
        db_objects.append(new_image)

    db.add_all(db_objects)
    await db.commit()

    return saved_files

async def get_report_images(report_id: int, db: AsyncSession):
    result = await db.execute(select(ReportImage).where(ReportImage.reportId == report_id))
    images = result.scalars().all()
    return [ImageSchema(id=image.id, url=image.imageUrl) for image in images]

async def delete_report_image(report_id: int, image_id: int, db: AsyncSession):
    result = await db.execute(select(ReportImage).where(ReportImage.id == image_id, ReportImage.reportId == report_id))
    image = result.scalar_one_or_none()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Imagen {image_id} no encontrada para el reporte {report_id}"
        )
    
    #Borrar el archivo de la imagen
    file_path = Path(image.imageUrl)
    if file_path.exists():
        file_path.unlink()

    await db.delete(image)
    await db.commit()

async def delete_all_report_images(report_id: int, db: AsyncSession):
    result = await db.execute(select(ReportImage).where(ReportImage.reportId == report_id))
    images = result.scalars().all()

    for image in images:
        #Borrar el archivo de la imagen
        file_path = Path(image.imageUrl)
        if file_path.exists():
            file_path.unlink()

        await db.delete(image)

    await db.commit()

#Comentarios
async def get_report_comments(report_id: int, db: AsyncSession):
    result = await db.execute(
        select(ReportComment)
        .where(ReportComment.reportId == report_id)
        .options(selectinload(ReportComment.user))
    )
    comments = result.scalars().all()
    return comments

async def create_report_comment(report_id: int, comment_data: str, user_id: int, db: AsyncSession):
    new_comment = ReportComment(reportId=report_id, content=comment_data, userId=user_id)
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)

    result = await db.execute(
        select(ReportComment)
        .where(ReportComment.id == new_comment.id)
        .options(selectinload(ReportComment.user))
    )
    comment = result.scalar_one()

    return comment

async def delete_report_comment(report_id: int, comment_id: int, user_id: int, db: AsyncSession):
    result = await db.execute(
        select(ReportComment)
        .where(ReportComment.id == comment_id, ReportComment.reportId == report_id, ReportComment.userId == user_id)
    )
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comentario {comment_id} no encontrado para el reporte {report_id} y usuario {user_id}"
        )
    
    await db.delete(comment)
    await db.commit()