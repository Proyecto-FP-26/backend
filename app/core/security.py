from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token") #https://fastapi.tiangolo.com/es/tutorial/security/simple-oauth2/ | https://cosasdedevs.com/posts/autenticacion-login-jwt-fastapi/

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
    to_encode["sub"] = str(to_encode["sub"]) #Sub no puede ser int (se le pasa el ID)
    expire = datetime.now(timezone.utc) + (expires_delta)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"))
    return encoded_jwt

async def decode_token(token: str = Depends(oauth2_scheme)):
    try:
        decoded_token = jwt.decode(token, os.getenv("SECRET_KEY"))
        decoded_token["sub"] = int(decoded_token["sub"])
    except JWTError as e:
        #print(f"DEBUG JWT: {e}")
        return None

    return decoded_token