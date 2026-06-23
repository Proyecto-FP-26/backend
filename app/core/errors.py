from fastapi import HTTPException, status


def http_error(detail: str, status_code: int):
    return HTTPException(status_code=status_code, detail=detail)


NO_AUTENTICADO = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No autenticado",
    headers={"WWW-Authenticate": "Bearer"},
)

SIN_CREDENCIALES = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas"
)
