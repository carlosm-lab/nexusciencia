"""
Flask Application Factory
Crea y configura la aplicación Flask con todas las extensiones y blueprints
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template
from app.config import get_config
from app.extensions import db, migrate, oauth, csrf, cache, limiter, assets
import pymysql

# Parche para SQLAlchemy + MySQL
pymysql.install_as_MySQLdb()


def create_app() -> Flask:
    """
    Factory pattern para crear aplicación Flask.
    
    La configuración se determina automáticamente según FLASK_ENV.
        
    Returns:
        Flask: Aplicación Flask configurada
    """
    # Definir rutas a templates y static en raíz del proyecto
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    template_dir = os.path.join(basedir, 'templates')
    static_dir = os.path.join(basedir, 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # REMEDIACIÓN: Simplificado - get_config() ya lee FLASK_ENV internamente
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Configurar logging
    configure_logging(app)
    
    logger = logging.getLogger(__name__)
    # REMEDIACIÓN: Mostrar ambiente real de config_class, no el parámetro ignorado
    env_name = getattr(config_class, 'ENV', 'unknown')
    logger.info(f"🚀 Iniciando NexusCiencia en modo: {env_name}")
    
    # Inicializar extensiones
    register_extensions(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Registrar error handlers
    register_error_handlers(app)
    
    # Context processors
    register_context_processors(app)
    
    # Request hooks para logging automático
    register_request_hooks(app)
    
    # Configuraciones adicionales según ambiente
    configure_production_features(app)
    
    # Comandos CLI
    from app import cli
    cli.init_app(app)
    
    return app


def configure_logging(app):
    """Configura logging estructurado con rotación. Usa JSON en producción."""
    from app.constants import MAX_LOG_SIZE_BYTES, MAX_LOG_BACKUP_COUNT
    
    log_level = logging.INFO if not app.debug else logging.DEBUG
    
    carpeta_base = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # Mover logs a carpeta dedicada fuera del web root (Auditoría: seguridad)
    log_dir = os.path.join(carpeta_base, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'app.log')
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=MAX_LOG_SIZE_BYTES,
        backupCount=MAX_LOG_BACKUP_COUNT
    )
    file_handler.setLevel(log_level)
    
    # REMEDIACIÓN AUD-006: Forzar UTF-8 en consola para evitar UnicodeEncodeError
    # con emojis en Windows (cp1252)
    import sys
    try:
        utf8_stream = open(sys.stdout.fileno(), mode='w', encoding='utf-8', errors='replace', closefd=False)
        stream_handler = logging.StreamHandler(stream=utf8_stream)
    except (OSError, ValueError):
        stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    
    # Use JSON formatter in production for log analytics
    if not app.debug:
        try:
            from pythonjsonlogger import jsonlogger
            json_formatter = jsonlogger.JsonFormatter(
                '%(asctime)s %(levelname)s %(name)s %(message)s',
                rename_fields={'asctime': 'timestamp', 'levelname': 'level'}
            )
            file_handler.setFormatter(json_formatter)
            stream_handler.setFormatter(json_formatter)
        except ImportError:
            # Fallback to text format if json logger not available
            text_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
            file_handler.setFormatter(text_formatter)
            stream_handler.setFormatter(text_formatter)
    else:
        text_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        file_handler.setFormatter(text_formatter)
        stream_handler.setFormatter(text_formatter)
    
    logging.basicConfig(
        level=log_level,
        handlers=[file_handler, stream_handler]
    )



def register_extensions(app):
    """Inicializa todas las extensiones Flask"""
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    cache.init_app(app)
    
    # Rate limiter con protección DoS global
    # REMEDIACIÓN CRÍTICO-002: Límites globales para prevenir ataques DoS
    limiter.init_app(app)
    limiter._storage_uri = app.config.get('RATELIMIT_STORAGE_URL', 'memory://')
    limiter._default_limits_enabled = app.config.get('RATELIMIT_ENABLED', True)
    
    # Límites globales por defecto (aplicados a todas las rutas sin límite explícito)
    if app.config.get('RATELIMIT_ENABLED', True):
        limiter._default_limits = ["1000 per hour", "200 per minute"]
    
    # OAuth
    oauth.init_app(app)
    oauth.register(
        name='google',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )
    
    # Flask-Assets
    assets.init_app(app)
    configure_assets(app)
    
    # Swagger/Flasgger
    from flasgger import Swagger
    swagger_config = {
        "headers": [],
        "specs": [{
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs"
    }
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "NexusCiencia API",
            "description": "API REST para gestión de artículos educativos",
            "version": "3.0.0",
            "contact": {"name": "NexusCiencia Team", "email": "api@nexusciencia.com"},
            "license": {"name": "MIT", "url": "https://opensource.org/licenses/MIT"}
        },
        "securityDefinitions": {
            "CSRF": {"type": "apiKey", "name": "X-CSRFToken", "in": "header"}
        },
        "security": [{"CSRF": []}]
    }
    
    Swagger(app, config=swagger_config, template=swagger_template)


def configure_assets(app):
    """Configura bundles de CSS/JS optimizados por página."""
    from flask_assets import Bundle
    
    # Evitar registro duplicado en tests
    if 'css_all' in assets._named_bundles:
        return
    
    # REMEDIACIÓN DT-004: Bundle CSS base (cargado en todas las páginas)
    css_bundle = Bundle(
        'css/variables.css',
        'css/layout.css',
        'css/components.css',
        'css/generic.css',
        filters='cssmin',
        output='gen/packed.css'
    )
    assets.register('css_all', css_bundle)
    
    # Bundle CSS específico para Dashboard
    css_dashboard = Bundle(
        'css/dashboard.css',
        filters='cssmin',
        output='gen/dashboard.min.css'
    )
    assets.register('css_dashboard', css_dashboard)
    
    # Bundle CSS específico para Admin
    css_admin = Bundle(
        'css/admin.css',
        filters='cssmin',
        output='gen/admin.min.css'
    )
    assets.register('css_admin', css_admin)
    
    # Bundle CSS específico para páginas de error
    css_error = Bundle(
        'css/error.css',
        filters='cssmin',
        output='gen/error.min.css'
    )
    assets.register('css_error', css_error)
    
    # Bundle CSS específico para artículos
    css_article = Bundle(
        'css/article.css',
        filters='cssmin',
        output='gen/article.min.css'
    )
    assets.register('css_article', css_article)
    
    # Bundle CSS específico para Homepage
    css_home = Bundle(
        'css/home.css',
        filters='cssmin',
        output='gen/home.min.css'
    )
    assets.register('css_home', css_home)
    
    # JS Bundles
    js_main = Bundle('js/main.js', filters='jsmin', output='gen/main.min.js')
    js_dashboard = Bundle('js/dashboard.js', filters='jsmin', output='gen/dashboard.min.js')
    js_admin = Bundle('js/admin.js', filters='jsmin', output='gen/admin.min.js')
    
    assets.register('js_main', js_main)
    assets.register('js_dashboard', js_dashboard)
    assets.register('js_admin', js_admin)


def register_blueprints(app):
    """Registra todos los blueprints de rutas"""
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp
    from app.routes.static_pages import pages_bp
    from app.routes.perfil import perfil_bp
    from app.routes.seo import seo_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(perfil_bp)
    app.register_blueprint(seo_bp)
    
    # Diagnostics blueprint: herramientas de admin
    from app.routes.diagnostics import diagnostics_bp
    app.register_blueprint(diagnostics_bp)
    
    # Debug blueprint: SOLO en desarrollo
    # Esto previene exposición de endpoints de debug en producción
    if app.debug:
        from app.routes.debug import debug_bp
        app.register_blueprint(debug_bp)
        logging.getLogger(__name__).info("🔧 Debug blueprint registrado (solo desarrollo)")


def register_error_handlers(app):
    """Registra manejadores de errores HTTP"""
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        logger = logging.getLogger(__name__)
        logger.error(f"Internal server error: {str(e)}", exc_info=True)
        return render_template('500.html'), 500
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        from flask import jsonify, make_response
        # Remediación ERR-001: Añadir Retry-After header
        response = make_response(jsonify({
            'error': 'Demasiadas peticiones',
            'message': 'Por favor espera un momento antes de intentar nuevamente'
        }), 429)
        response.headers['Retry-After'] = '60'
        return response


def register_context_processors(app):
    """Registra procesadores de contexto globales"""
    
    @app.context_processor
    def inject_global_vars():
        """Inyecta variables globales en templates"""
        from flask import session
        from app.constants import LISTA_CATEGORIAS, get_category_slug
        
        # Check si es admin
        es_admin = False
        admin_email = app.config.get('ADMIN_EMAIL', '')
        
        if 'user_email' in session and admin_email:
            es_admin = session['user_email'].strip().lower() == admin_email.strip().lower()
        
        # REMEDIACIÓN: Usar método centralizado en lugar de lógica duplicada
        from app.models.categoria import Categoria
        todas_las_categorias = Categoria.get_nombres_con_fallback()
        
        # Verificar acceso educativo (.edu)
        tiene_acceso_edu = False
        if es_admin:
            tiene_acceso_edu = True  # Admin siempre tiene acceso
        elif 'user_email' in session:
            from app.models.usuario import Usuario
            user = Usuario.query.filter_by(email=session['user_email']).first()
            tiene_acceso_edu = user.acceso_edu if user else False
        
        return dict(
            todas_las_categorias=todas_las_categorias,
            es_admin=es_admin,
            get_category_slug=get_category_slug,  # Nueva función para URLs jerárquicas
            tiene_acceso_edu=tiene_acceso_edu  # Acceso educativo verificado
        )


def register_request_hooks(app):
    """Registra hooks para logging automático de peticiones HTTP."""
    import time
    import uuid
    from flask import request, g
    from app.utils.helpers import check_session_timeout
    
    @app.before_request
    def before_request_logging():
        """Registra timestamp, correlation ID y verifica timeout de sesión."""
        g.request_start_time = time.time()
        # REMEDIACIÓN: Correlation ID para trazabilidad de requests
        g.request_id = str(uuid.uuid4())[:8]
        # Remediación AUTH-001: Verificar inactividad de sesión
        check_session_timeout()
    
    @app.after_request
    def after_request_logging(response):
        """Registra logs automáticos después de cada petición."""
        # Calcular tiempo de respuesta
        if hasattr(g, 'request_start_time'):
            elapsed = time.time() - g.request_start_time
            elapsed_ms = round(elapsed * 1000, 2)
        else:
            elapsed_ms = 0
        
        # REMEDIACIÓN: Agregar correlation ID al header de respuesta
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        
        # Solo loguear en producción o para rutas significativas
        if not app.debug:
            request_logger = logging.getLogger('request')
            req_id = getattr(g, 'request_id', 'unknown')
            request_logger.info(
                f"[{req_id}] {request.method} {request.path} - "
                f"Status: {response.status_code} - "
                f"Tiempo: {elapsed_ms}ms"
            )
        
        return response


def configure_production_features(app):
    """Configura características específicas de producción"""
    if app.debug or app.testing:
        return
    
    # HTTPS redirect con Flask-Talisman
    from flask_talisman import Talisman
    import secrets
    from flask import g
    
    # =======================================================================
    # REMEDIACIÓN CRÍTICO-001: CSP con Nonces (eliminado unsafe-inline)
    # =======================================================================
    # Genera un nonce único por request para estilos inline seguros.
    # Los templates deben usar: <style nonce="{{ csp_nonce }}">
    # =======================================================================
    
    @app.before_request
    def generate_csp_nonce():
        """Genera nonce criptográfico único por request para CSP."""
        g.csp_nonce = secrets.token_urlsafe(16)
    
    @app.context_processor
    def inject_csp_nonce():
        """Inyecta nonce CSP en todos los templates."""
        return dict(csp_nonce=getattr(g, 'csp_nonce', ''))
    
    def get_csp_policy():
        """Genera política CSP dinámica con nonce del request actual."""
        nonce = getattr(g, 'csp_nonce', '')
        return {
            'default-src': "'self'",
            'script-src': ["'self'", 'cdn.jsdelivr.net'],
            'style-src': [
                "'self'", 
                'cdn.jsdelivr.net', 
                'fonts.googleapis.com',
                f"'nonce-{nonce}'" if nonce else "'unsafe-inline'"  # Fallback seguro
            ],
            'font-src': ["'self'", 'fonts.gstatic.com'],
            'img-src': ["'self'", 'data:', 'https:'],
            'connect-src': ["'self'"],
        }
    
    # Usar callback para CSP dinámico con nonce por request
    # OPTIMIZACIÓN 10/10: Headers de seguridad enterprise-grade completos
    Talisman(
        app,
        force_https=True,
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,  # 1 año
        strict_transport_security_include_subdomains=True,
        strict_transport_security_preload=True,
        content_security_policy=get_csp_policy,
        content_security_policy_nonce_in=['script-src', 'style-src'],
        content_security_policy_report_only=False,
        # Headers adicionales de seguridad
        x_content_type_options=True,  # Previene MIME sniffing
        x_xss_protection=True,  # XSS filter del navegador
        referrer_policy='strict-origin-when-cross-origin',
        # Permissions Policy (moderno reemplazo de Feature-Policy)
        permissions_policy={
            'geolocation': '()',
            'microphone': '()',
            'camera': '()',
            'payment': '()',
            'usb': '()',
        }
    )
    
    # CORS explícito para API (si se necesita acceso cross-origin)
    @app.after_request
    def add_cors_headers(response):
        """Añade headers CORS restrictivos para API."""
        # Solo permitir mismo origen por defecto (máxima seguridad)
        response.headers['X-Permitted-Cross-Domain-Policies'] = 'none'
        return response
    
    # Sentry monitoring
    sentry_dsn = app.config.get('SENTRY_DSN')
    if sentry_dsn:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        
        # REMEDIACIÓN LOW-001: Propagar correlation ID a Sentry
        def before_send_handler(event, hint):
            """Añade correlation ID del request al evento de Sentry."""
            with app.app_context():
                request_id = getattr(g, 'request_id', None)
                if request_id:
                    if 'tags' not in event:
                        event['tags'] = {}
                    event['tags']['request_id'] = request_id
            return event
        
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[FlaskIntegration()],
            traces_sample_rate=0.2,  # REMEDIACIÓN: Reducido de 1.0 para optimizar costos
            profiles_sample_rate=0.2,  # REMEDIACIÓN: Reducido de 1.0 para optimizar rendimiento
            environment='production' if not app.debug else 'development',
            release=app.config.get('RELEASE_VERSION', 'v3.0.0'),
            before_send=before_send_handler,  # REMEDIACIÓN LOW-001
        )
        
        logger = logging.getLogger(__name__)
        logger.info("✅ Sentry monitoring initialized with correlation ID support")
