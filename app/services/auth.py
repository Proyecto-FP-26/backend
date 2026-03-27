from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import UserLogin
from app.core.security import verify_password, create_access_token
from app.core.security import oauth2_scheme, decode_token
from datetime import timedelta

no_autenticado = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )

sin_credenciales = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    payload = await decode_token(token) 

    if payload is None:
        raise no_autenticado
    
    user_id = payload.get("sub")
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    
    user = result.scalar_one_or_none()

    if not user:
        raise no_autenticado
    
    return user

async def authenticate_user(auth_data: UserLogin, db: AsyncSession):
    result = await db.execute(
        select(User).where(User.username == auth_data.username)
    )

    user = result.scalar_one_or_none()

    if not user:
        raise sin_credenciales

    if not verify_password(auth_data.password, user.passwordHash):
        raise sin_credenciales
    
    access_token = create_access_token(
        data={"sub": user.id, "role": user.role.value, "username": user.username},
        expires_delta=timedelta(minutes=30)
    )

    return {"access_token": access_token, "token_type": "bearer"}