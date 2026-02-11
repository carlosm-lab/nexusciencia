# =============================================================================
# NEXUSCIENCIA - DOCKERFILE OPTIMIZADO (Multi-Stage Build)
# =============================================================================
# REMEDIACIÓN DT-005: Multi-stage para reducir tamaño de imagen final
# =============================================================================

# -----------------------------------------------------------------------------
# STAGE 1: Builder - Instalación de dependencias
# -----------------------------------------------------------------------------
FROM python:3.13-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

# Instalar dependencias de compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar requirements
COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt

# -----------------------------------------------------------------------------
# STAGE 2: Runtime - Imagen final optimizada
# -----------------------------------------------------------------------------
FROM python:3.13-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/nexus/.local/bin:$PATH"

WORKDIR /app

# Instalar solo librerías runtime (sin compiladores)
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear usuario no-root
RUN useradd -m -u 1000 nexus

# Copiar dependencias instaladas desde builder
COPY --from=builder /root/.local /home/nexus/.local

# Copiar código de aplicación
COPY --chown=nexus:nexus . .

# Crear directorios necesarios
RUN mkdir -p instance logs backups static/gen \
    && chown -R nexus:nexus /app

# Cambiar a usuario no-root
USER nexus

# Exponer puerto
EXPOSE 8000

# Health check mejorado
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Comando de inicio con configuración optimizada
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "run:app"]
