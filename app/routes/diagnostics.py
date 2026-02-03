"""
Blueprint de Diagnósticos del Sistema - Panel de Administración
Provee endpoints para verificar el estado del sistema desde la UI de admin.
"""

import os
import logging
from datetime import datetime, timezone
from flask import Blueprint, jsonify, current_app
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError, OperationalError

from app.extensions import db, cache, limiter
from app.models.articulo import Articulo
from app.models.usuario import Usuario
from app.models.categoria import Categoria
from app.utils.decorators import admin_required

# Rate limit para endpoints de diagnóstico (REMEDIACIÓN CRT-001)
DIAGNOSTICS_RATE_LIMIT = "5 per minute"

# Blueprint
diagnostics_bp = Blueprint('diagnostics', __name__, url_prefix='/api/diagnostics')

logger = logging.getLogger(__name__)


def run_check(name: str, check_func) -> dict:
    """Ejecuta una verificación y captura errores."""
    start_time = datetime.now(timezone.utc)
    try:
        result = check_func()
        duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        return {
            'name': name,
            'status': 'pass' if result.get('success', False) else 'fail',
            'message': result.get('message', ''),
            'details': result.get('details', {}),
            'duration_ms': round(duration_ms, 2)
        }
    except Exception as e:
        duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        logger.error(f"Diagnostic check '{name}' failed: {e}", exc_info=True)
        return {
            'name': name,
            'status': 'error',
            'message': str(e),
            'details': {},
            'duration_ms': round(duration_ms, 2)
        }


# ============================================================================
# CHECKS INDIVIDUALES
# ============================================================================

def check_database():
    """Verifica conexión a base de datos."""
    db.session.execute(text('SELECT 1'))
    
    # Contar registros
    articulos = Articulo.query.count()
    usuarios = Usuario.query.count()
    
    return {
        'success': True,
        'message': 'Conexión a BD exitosa',
        'details': {
            'articulos': articulos,
            'usuarios': usuarios,
            'engine': str(db.engine.url).split('@')[-1] if '@' in str(db.engine.url) else 'sqlite'
        }
    }


def check_templates():
    """Verifica que los templates principales existan."""
    from app.config import BASE_DIR
    
    required_templates = [
        'base.html',
        'index.html',
        'admin.html',
        'articulo_detalle.html',
        '404.html',
        '500.html'
    ]
    
    missing = []
    for template in required_templates:
        path = os.path.join(BASE_DIR, 'templates', template)
        if not os.path.exists(path):
            missing.append(template)
    
    if missing:
        return {
            'success': False,
            'message': f'Templates faltantes: {", ".join(missing)}',
            'details': {'missing': missing}
        }
    
    return {
        'success': True,
        'message': f'{len(required_templates)} templates verificados',
        'details': {'verified': required_templates}
    }


def check_static_files():
    """Verifica archivos estáticos críticos."""
    from app.config import BASE_DIR
    
    required_files = [
        'css/variables.css',
        'css/layout.css',
        'js/main.js',
        'manifest.json',
        'img/favicon.ico'
    ]
    
    missing = []
    for file in required_files:
        path = os.path.join(BASE_DIR, 'static', file)
        if not os.path.exists(path):
            missing.append(file)
    
    if missing:
        return {
            'success': False,
            'message': f'Archivos estáticos faltantes: {", ".join(missing)}',
            'details': {'missing': missing}
        }
    
    return {
        'success': True,
        'message': f'{len(required_files)} archivos estáticos verificados',
        'details': {'verified': required_files}
    }


def check_articles_integrity():
    """Verifica integridad de artículos (archivos HTML existen)."""
    from app.config import BASE_DIR
    
    articulos = Articulo.get_active().all()
    orphaned = []
    
    for art in articulos:
        html_path = os.path.join(BASE_DIR, 'templates', 'articulos', art.nombre_archivo)
        if not os.path.exists(html_path):
            orphaned.append({'id': art.id, 'titulo': art.titulo, 'archivo': art.nombre_archivo})
    
    if orphaned:
        return {
            'success': False,
            'message': f'{len(orphaned)} artículos sin archivo HTML',
            'details': {'orphaned': orphaned[:5]}  # Limitar a 5
        }
    
    return {
        'success': True,
        'message': f'{len(articulos)} artículos con archivos verificados',
        'details': {'total': len(articulos)}
    }


def check_config():
    """Verifica configuración crítica."""
    issues = []
    
    if not current_app.config.get('SECRET_KEY'):
        issues.append('SECRET_KEY no configurada')
    
    if not current_app.config.get('GOOGLE_CLIENT_ID'):
        issues.append('GOOGLE_CLIENT_ID no configurada')
    
    if not current_app.config.get('ADMIN_EMAIL'):
        issues.append('ADMIN_EMAIL no configurada')
    
    # Verificar si CSRF está habilitado
    csrf_enabled = current_app.config.get('WTF_CSRF_ENABLED', True)
    
    if issues:
        return {
            'success': False,
            'message': f'{len(issues)} problemas de configuración',
            'details': {'issues': issues}
        }
    
    return {
        'success': True,
        'message': 'Configuración verificada',
        'details': {
            'environment': current_app.config.get('ENV', 'unknown'),
            'debug': current_app.debug,
            'csrf_enabled': csrf_enabled
        }
    }


def check_security():
    """Verifica configuración de seguridad."""
    issues = []
    details = {}
    
    # Verificar cookies seguras
    if current_app.config.get('SESSION_COOKIE_SECURE', False):
        details['secure_cookies'] = True
    else:
        if not current_app.debug:
            issues.append('SESSION_COOKIE_SECURE deshabilitado en producción')
        details['secure_cookies'] = False
    
    # Verificar rate limiting
    ratelimit = current_app.config.get('RATELIMIT_ENABLED', True)
    details['rate_limiting'] = ratelimit
    if not ratelimit and not current_app.debug:
        issues.append('Rate limiting deshabilitado')
    
    # Verificar CSRF
    csrf = current_app.config.get('WTF_CSRF_ENABLED', True)
    details['csrf_protection'] = csrf
    if not csrf:
        issues.append('CSRF protection deshabilitado')
    
    if issues:
        return {
            'success': False,
            'message': f'{len(issues)} issues de seguridad',
            'details': {'issues': issues, **details}
        }
    
    return {
        'success': True,
        'message': 'Seguridad configurada correctamente',
        'details': details
    }


def check_disk_space():
    """Verifica espacio en disco disponible."""
    from app.config import BASE_DIR
    import shutil
    
    try:
        total, used, free = shutil.disk_usage(BASE_DIR)
        free_gb = free / (1024 ** 3)
        total_gb = total / (1024 ** 3)
        used_percent = (used / total) * 100
        
        if free_gb < 1:
            return {
                'success': False,
                'message': f'Poco espacio en disco: {free_gb:.2f} GB libres',
                'details': {
                    'free_gb': round(free_gb, 2),
                    'total_gb': round(total_gb, 2),
                    'used_percent': round(used_percent, 1)
                }
            }
        
        return {
            'success': True,
            'message': f'{free_gb:.1f} GB disponibles',
            'details': {
                'free_gb': round(free_gb, 2),
                'total_gb': round(total_gb, 2),
                'used_percent': round(used_percent, 1)
            }
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'No se pudo verificar: {str(e)}',
            'details': {}
        }


def check_log_file():
    """Verifica estado del archivo de log."""
    from app.config import BASE_DIR
    
    # Corregido: logs están en la carpeta 'logs/' según configure_logging()
    log_path = os.path.join(BASE_DIR, 'logs', 'app.log')
    
    if not os.path.exists(log_path):
        return {
            'success': True,
            'message': 'Archivo de log no existe aún',
            'details': {'exists': False}
        }
    
    size_mb = os.path.getsize(log_path) / (1024 * 1024)
    
    return {
        'success': True,
        'message': f'Log: {size_mb:.2f} MB',
        'details': {
            'exists': True,
            'size_mb': round(size_mb, 2),
            'path': log_path
        }
    }


# ============================================================================
# ENDPOINTS
# ============================================================================

@diagnostics_bp.route('/run-all', methods=['POST'])
@admin_required
@limiter.limit(DIAGNOSTICS_RATE_LIMIT)
def run_all_checks():
    """Ejecuta todos los diagnósticos del sistema."""
    checks = [
        ('Base de Datos', check_database),
        ('Configuración', check_config),
        ('Seguridad', check_security),
        ('Templates', check_templates),
        ('Archivos Estáticos', check_static_files),
        ('Integridad Artículos', check_articles_integrity),
        ('Espacio en Disco', check_disk_space),
        ('Archivo de Log', check_log_file),
    ]
    
    results = []
    for name, func in checks:
        results.append(run_check(name, func))
    
    # Resumen
    passed = sum(1 for r in results if r['status'] == 'pass')
    failed = sum(1 for r in results if r['status'] == 'fail')
    errors = sum(1 for r in results if r['status'] == 'error')
    
    return jsonify({
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'summary': {
            'total': len(results),
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'health_score': round((passed / len(results)) * 100, 1)
        },
        'checks': results
    })


@diagnostics_bp.route('/database', methods=['POST'])
@admin_required
@limiter.limit(DIAGNOSTICS_RATE_LIMIT)
def check_db():
    """Verifica conexión a base de datos."""
    result = run_check('Base de Datos', check_database)
    return jsonify(result)


@diagnostics_bp.route('/config', methods=['POST'])
@admin_required
@limiter.limit(DIAGNOSTICS_RATE_LIMIT)
def check_cfg():
    """Verifica configuración."""
    result = run_check('Configuración', check_config)
    return jsonify(result)


@diagnostics_bp.route('/security', methods=['POST'])
@admin_required
@limiter.limit(DIAGNOSTICS_RATE_LIMIT)
def check_sec():
    """Verifica seguridad."""
    result = run_check('Seguridad', check_security)
    return jsonify(result)


@diagnostics_bp.route('/templates', methods=['POST'])
@admin_required
@limiter.limit(DIAGNOSTICS_RATE_LIMIT)
def check_tpl():
    """Verifica templates."""
    result = run_check('Templates', check_templates)
    return jsonify(result)


@diagnostics_bp.route('/static', methods=['POST'])
@admin_required
@limiter.limit(DIAGNOSTICS_RATE_LIMIT)
def check_stc():
    """Verifica archivos estáticos."""
    result = run_check('Archivos Estáticos', check_static_files)
    return jsonify(result)


@diagnostics_bp.route('/articles', methods=['POST'])
@admin_required
@limiter.limit(DIAGNOSTICS_RATE_LIMIT)
def check_art():
    """Verifica integridad de artículos."""
    result = run_check('Integridad Artículos', check_articles_integrity)
    return jsonify(result)


@diagnostics_bp.route('/disk', methods=['POST'])
@admin_required
@limiter.limit(DIAGNOSTICS_RATE_LIMIT)
def check_dsk():
    """Verifica espacio en disco."""
    result = run_check('Espacio en Disco', check_disk_space)
    return jsonify(result)


@diagnostics_bp.route('/logs', methods=['POST'])
@admin_required
@limiter.limit(DIAGNOSTICS_RATE_LIMIT)
def check_logs():
    """Verifica archivo de log."""
    result = run_check('Archivo de Log', check_log_file)
    return jsonify(result)
