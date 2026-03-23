# Proyecto de FastAPI

API REST construida con **FastAPI** usando **SQLAlchemy async** con **PostgreSQL**.

## Descripción

Este proyecto expone una API con FastAPI que:

- Inicia un admin por defecto usando seeds.
- Expone rutas básicas (como `/reports`). Más info en `/docs`.
- Utiliza base de datos PostgreSQL configurada mediante variables de entorno.

---

## 1. Preparar el entorno

El proyecto usa **uv**, por lo que puedes crear el entorno virtual y sincronizar dependencias con un solo comando:

```bash
uv sync
```

Esto creará `.venv` e instalará todas las dependencias automáticamente.

## 2. Configurar variables de entorno

Copia el archivo de ejemplo y edítalo con tus datos

```bash
cp .env.example .env
```

Ejemplo de .env

```markdown
DATABASE_URL=postgresql+asyncpg://usuario:contraseña@localhost:5432/nombre_db

ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@dominio.com
ADMIN_PASSWORD=contraseña_segura
```

## 3. Ejecutar la API

```bash
uvicorn app.main:app
```
