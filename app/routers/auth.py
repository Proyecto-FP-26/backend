from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.auth import UserLogin, UserResponse, LoginResponse
from app.dependencies.auth import get_current_user, get_current_user_jti
from app.services.auth import authenticate_user, refresh_tokens
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse)
async def auth_login(response: Response, request: Request, auth_data: UserLogin, db: AsyncSession = Depends(get_db)):
    return await authenticate_user(auth_data = auth_data, db=db, response=response, request=request)


@router.post("/token", include_in_schema=False)
async def auth_login(response: Response, request: Request, auth_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    #auth_data_login = UserLogin(username=auth_data.username, password=auth_data.password)
    return await authenticate_user(auth_data = UserLogin(**auth_data.__dict__), db=db, response=response, request=request)

@router.post("/refresh", response_model=LoginResponse)
async def auth_refresh(response: Response, request: Request, current_user_jti=Depends(get_current_user_jti), db: AsyncSession = Depends(get_db)):
    '''Se envía el refresh token en la cookie o en el header Authorization (Bearer) para obtener nuevos tokens.'''
    return await refresh_tokens(user_jti=current_user_jti, db=db, response=response, request=request)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    return current_user