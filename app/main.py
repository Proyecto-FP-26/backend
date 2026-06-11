from fastapi import FastAPI, Request
from app.db.database import AsyncSessionLocal
from app.db.seeds.admin import seed_admin
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.routers.reports import router as reports_router
from app.routers.auth import router as auth_router
from app.routers.reports_category import router as reports_categories_router

from fastapi.middleware.cors import CORSMiddleware
from app.core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    #Todo lo que este aqui se ejecuta al principio
    async with AsyncSessionLocal() as db:
        try:
            await seed_admin(db)
            #yield
        except Exception as e:
            print(f"Error lifespan: {type(e).__name__} | {e}") 
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
app.include_router(reports_categories_router)
app.include_router(auth_router)

#Captura de errores | https://fastapi.tiangolo.com/tutorial/handling-errors/#install-custom-exception-handlers
#OSError: Error de conexión a la base de datos
@app.exception_handler(OSError)
async def connection_error_handler(request: Request, exc: OSError):
    return JSONResponse(
        status_code=503,
        content={"message": "No se pudo establecer conexión con la base de datos. Verifica el estado del servidor de la base de datos o la configuración de la conexión."},
    )

#SQLAlchemyError: Errores relacionados con la base de datos, como consultas mal formadas o problemas de integridad de datos
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"message": "Error interno en la base de datos."},
    )

@app.get("/", include_in_schema=False)
async def root():
    return {"status": "ok", "message": "Check API Docs at /docs or /redoc"}