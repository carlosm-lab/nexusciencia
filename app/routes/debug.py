"""
Blueprint de Debug - Solo para desarrollo
Este blueprint solo se registra cuando DEBUG=True
"""

from flask import Blueprint, current_app, abort

# Blueprint de debug (solo desarrollo)
debug_bp = Blueprint('debug', __name__, url_prefix='/debug')


@debug_bp.route('/sentry')
def trigger_sentry_error():
    """
    Ruta para probar la integración con Sentry.
    Solo disponible en modo desarrollo.
    
    ---
    tags:
      - Debug
    responses:
      404:
        description: No disponible en producción
    """
    # Doble verificación de seguridad
    if not current_app.debug:
        abort(404)
    
    # Error intencional para testing de Sentry
    division_by_zero = 1 / 0  # noqa: F841
    return "Esta línea nunca se ejecuta"


@debug_bp.route('/config')
def show_config():
    """
    Muestra configuración actual (solo desarrollo).
    NUNCA exponer en producción.
    """
    if not current_app.debug:
        abort(404)
    
    # Solo mostrar configuración no sensible
    safe_config = {
        'ENV': current_app.config.get('ENV'),
        'DEBUG': current_app.config.get('DEBUG'),
        'TESTING': current_app.config.get('TESTING'),
        'RATELIMIT_ENABLED': current_app.config.get('RATELIMIT_ENABLED'),
    }
    
    from flask import jsonify
    return jsonify(safe_config)
