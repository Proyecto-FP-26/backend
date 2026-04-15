from fastapi import FastAPI
from app.db.database import AsyncSessionLocal
from app.db.seeds.admin import seed_admin
from contextlib import asynccontextmanager

from app.routers.reports import router as reports_router
from app.routers.auth import router as auth_router

from fastapi.middleware.cors import CORSMiddleware
from app.core.settings import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    #Todo lo que este aqui se ejecuta al principio
    async with AsyncSessionLocal() as db:
        await seed_admin(db)
    yield

app = FastAPI(lifespan=lifespan)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(reports_router)
app.include_router(auth_router)

@app.get("/", include_in_schema=False)
async def root():
    return {"status": "ok", "message": "Check API Docs at /docs or /redoc"}