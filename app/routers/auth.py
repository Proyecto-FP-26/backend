from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.auth import UserLogin, UserResponse
from app.services.auth import get_current_user, authenticate_user
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
async def auth_login(auth_data: UserLogin, db: AsyncSession = Depends(get_db)):
    return await authenticate_user(auth_data = auth_data, db=db)


@router.post("/token", include_in_schema=False)
async def auth_login(auth_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    #auth_data_login = UserLogin(username=auth_data.username, password=auth_data.password)
    return await authenticate_user(auth_data = UserLogin(**auth_data.__dict__), db=db)


@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user=Depends(get_current_user)):
    return current_user