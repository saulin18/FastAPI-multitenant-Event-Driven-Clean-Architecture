FROM python:3.11-slim AS base

# Instalar dependencias del sistema necesarias para compilar paquetes
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder

WORKDIR /app

# Instalar Poetry
RUN pip install --no-cache-dir poetry

# Configurar Poetry para crear venv en /app/.venv
RUN poetry config virtualenvs.create true && \
    poetry config virtualenvs.in-project true

# Copiar archivos de dependencias
COPY poetry.lock pyproject.toml ./

# Instalar dependencias en el venv
RUN poetry install --no-root --no-interaction --no-ansi

FROM base AS runtime

WORKDIR /app

# Copiar el venv del builder
COPY --from=builder /app/.venv /app/.venv

# Configurar PATH para usar el venv
ENV PATH="/app/.venv/bin:$PATH"

# Copiar el código de la aplicación
COPY ./app /app/app
COPY ./alembic /app/alembic
COPY ./alembic.ini /app/alembic.ini

# Exponer el puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]