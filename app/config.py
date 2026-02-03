# ==========================================================================
#  NEXUS CIENCIA - CONFIGURACIÓN POR AMBIENTE
# ==========================================================================
#  Descripción: Configuración separada para desarrollo y producción
# ==========================================================================

import os
from datetime import timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Directorio base del proyecto (evita recalcularlo en múltiples lugares)
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def _get_secret_key():
    """
    Obtiene SECRET_KEY con validación de seguridad completa.
    
    Validaciones:
        1. Existencia de la clave
        2. Longitud mínima (32 caracteres)
        3. Entropía mínima (al menos 10 caracteres únicos)
    
    En testing, genera una clave temporal segura si no existe.
    """
    secret = os.getenv('SECRET_KEY')
    env = os.getenv('FLASK_ENV', 'development')
    
    # En testing, generar una clave temporal si no existe
    if env == 'testing' and not secret:
        import secrets
        return secrets.token_hex(32)
    
    if not secret:
        raise RuntimeError(
            "⚠️ SECRET_KEY no configurada. "
            "Por seguridad, la aplicación requiere una SECRET_KEY en el archivo .env. "
            "Genera una con: python -c 'import secrets; print(secrets.token_hex(32))'"
        )
    
    # Validar longitud mínima (excepto en testing)
    if len(secret) < 32 and env != 'testing':
        raise RuntimeError(
            f"⚠️ SECRET_KEY demasiado corta ({len(secret)} caracteres). "
            "Por seguridad, debe tener al menos 32 caracteres. "
            "Genera una con: python -c 'import secrets; print(secrets.token_hex(32))'"
        )
    
    # REMEDIACIÓN: Validar entropía mínima (caracteres únicos)
    # Previene claves débiles como 'aaaa...' que pasan validación de longitud
    MIN_UNIQUE_CHARS = 10
    unique_chars = len(set(secret))
    if unique_chars < MIN_UNIQUE_CHARS and env != 'testing':
        raise RuntimeError(
            f"⚠️ SECRET_KEY con baja entropía ({unique_chars} caracteres únicos). "
            f"Por seguridad, debe tener al menos {MIN_UNIQUE_CHARS} caracteres únicos. "
            "Genera una con: python -c 'import secrets; print(secrets.token_hex(32))'"
        )
    
    return secret


class Config:
    """Configuración base compartida entre todos los ambientes."""
    
    # Seguridad - usar función helper para validación
    SECRET_KEY = _get_secret_key()
    
    # OAuth Google
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    
    # Validar credenciales de OAuth (solo si no es testing)
    @classmethod
    def _validate_oauth(cls):
        env = os.getenv('FLASK_ENV', 'development')
        if env != 'testing':
            if not cls.GOOGLE_CLIENT_ID or not cls.GOOGLE_CLIENT_SECRET:
                raise RuntimeError(
                    "⚠️ Credenciales de Google OAuth no configuradas. "
                    "Por favor configura GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET en el archivo .env"
                )
    
    # Admin
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', '')
    
    # Base de datos - Opciones de conexión optimizadas
    # =========================================================================
    # DOCUMENTACIÓN DE VALORES:
    # - pool_recycle (3600s = 1 hora): Evita errores "MySQL has gone away"
    #   Valor estándar para MySQL con wait_timeout=28800s (8h)
    # - pool_pre_ping: Verifica conexión antes de usar (overhead mínimo, alta fiabilidad)
    # - pool_size (10): Conexiones persistentes en pool
    #   Regla: workers * 2 para Gunicorn. Con 4 workers = 8, redondeado a 10
    # - max_overflow (20): Conexiones adicionales temporales bajo carga
    #   Permite picos de tráfico sin rechazar peticiones
    # =========================================================================
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20
    }
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Session Security
    SESSION_COOKIE_SECURE = True  # Solo HTTPS
    SESSION_COOKIE_HTTPONLY = True  # No JS access
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Caching
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutos
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_ENABLED = True
    
    # Seguridad - Limite de tamaño de archivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB máximo
    
    # Constantes de Aplicación (centralizadas)
    ARTICLES_PER_PAGE = 20
    DEFAULT_READING_TIME = 5
    LOGS_PER_PAGE = 50
    TOAST_DURATION_MS = 5000
    MAX_FILE_SIZE_MB = 16 * 1024 * 1024
    ASSET_VERSION = os.getenv('ASSET_VERSION', 'v3.1.0')  # Versión actualizada


class DevelopmentConfig(Config):
    """Configuración para ambiente de desarrollo."""
    
    DEBUG = True
    TESTING = False
    ENV = 'development'
    
    # Base de datos local (SQLite)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'instance', 'datos.db')
    )
    
    # Permitir OAuth en HTTP para desarrollo
    OAUTHLIB_INSECURE_TRANSPORT = '1'
    
    # Session cookies en desarrollo (HTTP permitido)
    SESSION_COOKIE_SECURE = False
    
    # Rate limiting más permisivo en desarrollo
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'False') == 'True'


class ProductionConfig(Config):
    """Configuración para ambiente de producción."""
    
    DEBUG = False
    TESTING = False
    ENV = 'production'
    
    # Base de datos en producción (MySQL)
    uri_db = os.getenv('DATABASE_URL')
    if not uri_db:
        # Fallback a SQLite si no hay DATABASE_URL configurada
        # Esto permite testing de producción en local
        import warnings
        warnings.warn(
            "DATABASE_URL no configurada. Usando SQLite para testing de producción. "
            "En producción real, DEBES configurar DATABASE_URL en .env",
            UserWarning
        )
        uri_db = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'instance', 'datos.db')
    
    # Fix para SQLAlchemy moderno
    if uri_db.startswith('mysql://'):
        uri_db = uri_db.replace('mysql://', 'mysql+pymysql://')
    
    SQLALCHEMY_DATABASE_URI = uri_db
    
    # Rate limiting activo en producción
    RATELIMIT_ENABLED = True
    
    # Rate limiting con Redis (más robusto que memoria)
    # Usa Redis si está disponible, fallback a memoria con warning
    _redis_url = os.getenv('REDIS_URL')
    if not _redis_url:
        import warnings
        warnings.warn(
            "⚠️ REDIS_URL no configurado. Rate limiting usa memoria en lugar de Redis. "
            "Esto NO es recomendado en producción: los límites se resetean al reiniciar workers. "
            "Configura REDIS_URL en .env para persistencia de rate limits.",
            RuntimeWarning
        )
    RATELIMIT_STORAGE_URL = _redis_url or 'memory://'
    
    # Sentry (opcional)
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    RELEASE_VERSION = os.getenv('RELEASE_VERSION', 'v3.0.0')


class TestingConfig(Config):
    """Configuración para testing."""
    
    DEBUG = False
    TESTING = True
    ENV = 'testing'
    
    # Base de datos en memoria para tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Deshabilitar CSRF en tests
    WTF_CSRF_ENABLED = False
    
    # Deshabilitar rate limiting en tests
    RATELIMIT_ENABLED = False
    
    # Session cookies en testing
    SESSION_COOKIE_SECURE = False


# Mapeo de ambientes a configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Obtiene la configuración según la variable FLASK_ENV."""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
