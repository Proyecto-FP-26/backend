from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login") #https://fastapi.tiangolo.com/es/tutorial/security/simple-oauth2/ | https://cosasdedevs.com/posts/autenticacion-login-jwt-fastapi/

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=5)): #https://www.rfc-editor.org/rfc/rfc7519#section-4.1.2
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"))
    return encoded_jwt

async def get_username(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"))
        username: str = payload.get("sub")
    except JWTError:
        return None

    return username