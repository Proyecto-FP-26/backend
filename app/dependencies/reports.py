from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db 
from app.services.reports import get_report_by_id

async def valid_report_id(id: int, db: AsyncSession = Depends(get_db)):
    return await get_report_by_id(id, db)
