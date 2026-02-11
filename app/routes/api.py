"""
Blueprint de API REST para interacciones AJAX
"""

import logging
from flask import Blueprint, jsonify, session, current_app, Response
from typing import Tuple
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from datetime import datetime, timezone

from app.extensions import db, limiter
from app.models.articulo import Articulo
from app.models.usuario import Usuario
from app.models.log import LogActividad
from app.utils.helpers import get_rate_limit_key

# Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

logger = logging.getLogger(__name__)


@api_bp.route('/toggle_biblioteca/<int:articulo_id>', methods=['POST'])
@limiter.limit("20 per minute", key_func=get_rate_limit_key)  # Remediación RATE-001: Límite más conservador
def toggle_biblioteca(articulo_id: int) -> Tuple[Response, int]:
    """
    Endpoint para Guardar/Quitar artículos de la biblioteca personal.
    ---
    tags:
      - Biblioteca
    parameters:
      - name: articulo_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Artículo añadido o removido exitosamente
      403:
        description: No autorizado
      404:
        description: Artículo o usuario no encontrado
    """
    if 'user_email' not in session:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 403
    
    usuario = Usuario.query.filter_by(email=session['user_email']).first()
    articulo = Articulo.query.get_or_404(articulo_id)
    
    if not usuario:
        return jsonify({'status': 'error', 'message': 'Usuario no encontrado'}), 404
    
    # REMEDIACIÓN FUNCIONAL-002: Transacción atómica para prevenir race conditions
    try:
        with db.session.begin_nested():
            action = ''
            if articulo in usuario.articulos_guardados:
                usuario.articulos_guardados.remove(articulo)
                action = 'removed'
                logger.info(f"Biblioteca: artículo {articulo_id} removido por usuario hash")
            else:
                usuario.articulos_guardados.append(articulo)
                action = 'added'
                logger.info(f"Biblioteca: artículo {articulo_id} guardado por usuario hash")
        
        db.session.commit()
        return jsonify({'status': 'ok', 'action': action})
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error en toggle_biblioteca: {e.__class__.__name__}")
        return jsonify({'status': 'error', 'message': 'Error de base de datos'}), 500


@api_bp.route('/vaciar_biblioteca', methods=['POST'])
@limiter.limit("5 per minute", key_func=get_rate_limit_key)
def vaciar_biblioteca() -> Tuple[Response, int]:
    """
    Endpoint para eliminar TODOS los artículos de la biblioteca del usuario.
    ---
    tags:
      - Biblioteca
    responses:
      200:
        description: Biblioteca vaciada exitosamente
      403:
        description: No autorizado
      404:
        description: Usuario no encontrado
    """
    if 'user_email' not in session:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 403
    
    usuario = Usuario.query.filter_by(email=session['user_email']).first()
    if not usuario:
        return jsonify({'status': 'error', 'message': 'Usuario no encontrado'}), 404
    
    # Limpiar la lista de artículos guardados (Disociación)
    try:
        usuario.articulos_guardados = []
        db.session.commit()
        return jsonify({'status': 'ok', 'message': 'Biblioteca vaciada'})
    except Exception:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Error al vaciar biblioteca'}), 500


@api_bp.route('/health')
def health_check() -> Tuple[Response, int]:
    """
    Endpoint para verificar estado del servicio.
    
    REMEDIACIÓN MED-002: Información detallada solo para admins.
    Usuarios anónimos solo reciben status básico.
    ---
    tags:
      - Health
    responses:
      200:
        description: Servicio funcionando correctamente
      503:
        description: Servicio no disponible
    """
    try:
        # Verificar conexión a base de datos
        db.session.execute(text('SELECT 1'))
        db_status = 'ok'
    except (OperationalError, SQLAlchemyError) as e:
        logger.error(f"Health check failed - DB error: {e.__class__.__name__}")
        db_status = 'error'
        # Respuesta mínima en caso de error (sin exponer detalles)
        return jsonify({
            'status': 'unhealthy',
            'database': db_status
        }), 503
    
    # Respuesta básica para usuarios no autenticados
    basic_response = {
        'status': 'healthy',
        'database': db_status
    }
    
    # REMEDIACIÓN MED-002: Detalles extendidos solo para admins autenticados
    admin_email = current_app.config.get('ADMIN_EMAIL', '')
    user_email = session.get('user_email', '')
    is_admin = user_email and admin_email and user_email.strip().lower() == admin_email.strip().lower()
    
    if is_admin:
        # Admin obtiene información completa para debugging
        basic_response.update({
            'environment': 'production' if not current_app.debug else 'development',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'version': current_app.config.get('RELEASE_VERSION', 'unknown')
        })
    
    return jsonify(basic_response), 200


# DEBUG: El endpoint /debug-sentry ha sido movido a app/routes/debug.py
# Este blueprint solo se registra en modo desarrollo para mayor seguridad
