from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.user import User, UserSession
from app.core.security import oauth2_scheme, decode_token
from app.core.settings import settings
from app.core.errors import NO_AUTENTICADO

class Get_Current_User:
    def __init__(self, cookie_name: str = settings.ACCESS_COOKIE_NAME):
        self.cookie_name = cookie_name

    async def __call__(self, request: Request, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
        payload = self._get_token_payload(request, token)

        user = await self._get_user_from_payload(payload.get("sub"), db)
        jti = payload.get("jti")

        #Verificar que el type del token sea el correcto
        is_valid_access = payload.get("type") == "access" and self.cookie_name == settings.ACCESS_COOKIE_NAME
        is_valid_refresh = payload.get("type") == "refresh" and self.cookie_name == settings.REFRESH_COOKIE_NAME
        if not (is_valid_access or is_valid_refresh):
            raise NO_AUTENTICADO
        
        await self._verify_jti(jti, db)

        return user, jti

    def _get_token_payload(self, request: Request, token: str):
        if not token: 
            cookie_token = request.cookies.get(self.cookie_name)
            if cookie_token:
                token = cookie_token
            else:
                raise NO_AUTENTICADO
            
        return decode_token(token)

    async def _get_user_from_payload(self, user_id: str, db: AsyncSession):   
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        
        user = result.scalar_one_or_none()

        if not user:
            raise NO_AUTENTICADO
        
        return user

    async def _verify_jti(self, jti: str, db: AsyncSession):
        result = await db.execute(select(UserSession).where(UserSession.jti == jti))
        session = result.scalar_one_or_none()

        if not session or session.isRevoked:
            raise NO_AUTENTICADO