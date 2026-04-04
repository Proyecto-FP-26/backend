from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: list[str] = []

    DATABASE_URL: str
    DATABASE_URL_SYNC: str

    DB_POOL_SIZE: int = 1 #TODO: Añadir esta configuración a la conexión de SQLAlchemy
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 3600
    DB_POOL_TIMEOUT: int = 30
    DB_ECHO: bool = False

    ADMIN_USERNAME: str
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    ACCESS_COOKIE_NAME: str
    REFRESH_COOKIE_NAME: str

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env") #extra="ignore" : Si se ponen variables en .env que no se quieren declarar aquí

settings = Settings()