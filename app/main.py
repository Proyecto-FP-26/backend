from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal
from app.db.seeds.admin import seed_admin
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.db.database import get_db
from app.models.user import User

from app.routers.reports import router as reports_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    #Todo lo que este aqui se ejecuta al principio
    async with AsyncSessionLocal() as db:
        await seed_admin(db)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(reports_router)

@app.get("/")
async def root():
    return {"status": "ok"}

@app.get("/usuarios")
async def listar_usuarios(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()