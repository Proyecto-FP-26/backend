from fastapi import Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import UserLogin, UserSessionCreate
from app.core.security import verify_password, create_access_token
from app.core.security import oauth2_scheme, decode_token
from datetime import timedelta
from app.core.settings import settings
from app.core.errors import SIN_CREDENCIALES
from app.models.user import UserSession
from datetime import datetime, timezone
from typing import Tuple

async def authenticate_user(auth_data: UserLogin, db: AsyncSession, response: Response, request: Request):
    result = await db.execute(
        select(User).where(User.username == auth_data.username)
    )

    user = result.scalar_one_or_none()

    if not user:
        raise SIN_CREDENCIALES

    if not verify_password(auth_data.password, user.passwordHash):
        raise SIN_CREDENCIALES
    
    return await _create_auth(response, request, db, user)

async def refresh_tokens(user_jti: Tuple[User, str], db: AsyncSession, response: Response, request: Request):
    user, jti = user_jti

    #Revocar sesión actual
    result = await db.execute(select(UserSession).where(UserSession.jti == jti))
    session = result.scalar_one_or_none()

    if session:
        session.isRevoked = True
        await db.commit()
    
    return await _create_auth(response, request, db, user)

async def _create_auth(response: Response, request: Request, db: AsyncSession, user: User):
    #Buscar si hay sesiones abiertas para este usuario (y dispositivo) para cerrarlas
    sessions = await db.execute(select(UserSession).where(
        UserSession.userId == user.id,
        #UserSession.deviceInfo == request.headers.get("user-agent"),
        UserSession.isRevoked == False
        ))
    sessions = sessions.scalars().all() 

    for session in sessions:
        session.isRevoked = True

    await db.commit()

    #Crear nueva sesión
    user_session_data = UserSessionCreate(
        userId=user.id,
        deviceInfo=request.headers.get("user-agent"),
        ip=request.headers.get("x-forwarded-for", request.client.host),
        rememberMe=False,
        expiresAt=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    user_session = UserSession(**user_session_data.model_dump())

    db.add(user_session)
    await db.commit()
    await db.refresh(user_session)

    access_token = create_access_token(
        data={"sub": user.id, "role": user.role.value, "username": user.username, "jti": user_session.jti, "type": "access"},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    refresh_token = create_access_token(
        data={"sub": user.id, "role": user.role.value, "username": user.username, "jti": user_session.jti, "type": "refresh"},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    response.set_cookie(
            key=settings.ACCESS_COOKIE_NAME,
            value=access_token,
            httponly=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            #expires=datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            samesite="lax",
            secure=False,
            path="/",
        )
    
    response.set_cookie(
            key=settings.REFRESH_COOKIE_NAME,
            value=refresh_token,
            httponly=True,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            #expires=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            samesite="lax",
            secure=False,
            path="/auth/refresh",
        )
    
    return {settings.ACCESS_COOKIE_NAME: access_token, settings.REFRESH_COOKIE_NAME: refresh_token, "token_type": "bearer"}