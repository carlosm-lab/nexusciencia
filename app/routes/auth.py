"""
Blueprint de autenticación con Google OAuth
"""

import hashlib
import logging
from datetime import datetime, timezone
from urllib.parse import urlparse
from flask import Blueprint, redirect, url_for, session, request, Response, abort
from app.extensions import db, oauth, limiter
from app.models.usuario import Usuario
from app.models.notificacion import Notificacion
from app.models.log import LogActividad
from app.enums import LogEventType
from app.utils.helpers import get_rate_limit_key
from app.constants import DEFAULT_AVATAR_PATH

# Logger configurado al inicio del módulo (Auditoría: evitar definición tardía)
logger = logging.getLogger(__name__)

# Blueprint
auth_bp = Blueprint('auth', __name__)


def validar_imagen_oauth(url: str) -> str:
    """
    Valida que la URL de imagen OAuth sea segura.
    
    Solo permite URLs HTTPS de dominios Google conocidos para prevenir
    inyección de URLs maliciosas via tokens OAuth manipulados.
    
    Args:
        url: URL de imagen del usuario
        
    Returns:
        URL validada o DEFAULT_AVATAR_PATH si es inválida
    """
    if not url:
        return DEFAULT_AVATAR_PATH
    
    # REMEDIACIÓN DT-002: urlparse importado al inicio del archivo
    try:
        parsed = urlparse(url)
        
        # Solo HTTPS permitido
        if parsed.scheme != 'https':
            logger.warning(f"Imagen OAuth rechazada: scheme no es HTTPS - {parsed.scheme}")
            return DEFAULT_AVATAR_PATH
        
        # Solo dominios Google específicos de imágenes de perfil
        # REMEDIACIÓN SEC-003: Eliminado 'googleusercontent.com' genérico
        dominios_permitidos = [
            'lh3.googleusercontent.com',
            'lh4.googleusercontent.com',
            'lh5.googleusercontent.com',
            'lh6.googleusercontent.com',
        ]
        
        dominio_valido = any(
            parsed.netloc == d or parsed.netloc.endswith('.' + d)
            for d in dominios_permitidos
        )
        
        if not dominio_valido:
            logger.warning(f"Imagen OAuth rechazada: dominio no permitido - {parsed.netloc}")
            return DEFAULT_AVATAR_PATH
        
        return url
        
    except Exception as e:
        logger.warning(f"Error validando imagen OAuth: {e}")
        return DEFAULT_AVATAR_PATH

# Obtener cliente OAuth de extensiones
google = oauth


def get_client_info() -> dict:
    """
    Obtiene información del cliente para logging de seguridad.
    
    Remediación LOG-001: Almacena User-Agent completo con hash para auditoría.
    
    Returns:
        dict con ip, user_agent, user_agent_hash y otros metadatos
    """
    import hashlib
    
    user_agent = request.headers.get('User-Agent', 'Unknown')
    user_agent_hash = hashlib.sha256(user_agent.encode()).hexdigest()[:16]
    
    return {
        'ip': request.headers.get('X-Forwarded-For', request.remote_addr),
        'user_agent': user_agent,
        'user_agent_hash': user_agent_hash,  # Para correlación en logs
        'referrer': request.headers.get('Referer', '')[:200]
    }


@auth_bp.route('/login')
@limiter.limit("10 per minute")
def login() -> Response:
    """Inicia el flujo de OAuth con Google."""
    redirect_uri = url_for('auth.google_callback', _external=True)
    return google.google.authorize_redirect(redirect_uri)


@auth_bp.route('/google/callback')
@limiter.limit("10 per minute", key_func=get_rate_limit_key)
def google_callback() -> Response:
    """Recibe la respuesta de Google y crea/loguea al usuario."""
    try:
        token = google.google.authorize_access_token()
    except Exception as e:
        logger.error(f"Error al obtener token de Google: {e.__class__.__name__}")
        abort(400, description="Error de autenticación con Google. Por favor intenta de nuevo.")
    
    user_info = token.get('userinfo')
    
    # Validación defensiva: verificar que los datos críticos existen (Auditoría: seguridad)
    if not user_info:
        logger.error("OAuth callback sin userinfo en token")
        abort(400, description="No se pudo obtener información del usuario de Google.")
    
    email = user_info.get('email')
    if not email:
        logger.error("OAuth callback sin email en userinfo")
        abort(400, description="El email es requerido para autenticación.")
    
    # REMEDIACIÓN CRT-001: Verificar que el email esté verificado por Google
    # Previene login con cuentas Google que tienen emails no verificados
    if not user_info.get('email_verified', False):
        # REMEDIACIÓN CRT-002: Hashear email en logs para proteger PII
        # (hashlib importado al inicio del archivo - DT-002)
        email_hash = hashlib.sha256(email.encode()).hexdigest()[:16]
        logger.warning(f"Intento de login con email no verificado: hash={email_hash}")
        abort(403, description="Solo se permiten cuentas con email verificado por Google.")
    
    nombre = user_info.get('name', email.split('@')[0])  # Fallback al usuario del email
    
    # Obtener información del cliente para auditoría
    client_info = get_client_info()
    
    usuario_existente = Usuario.query.filter_by(email=email).first()
    
    if usuario_existente:
        usuario_existente.fecha_ultimo_login = datetime.now(timezone.utc)
        # Remediación LOG-001: User-Agent completo con hash para correlación
        log_detalle = f"Login: {email} | IP: {client_info['ip']} | UA_HASH: {client_info['user_agent_hash']}"
    else:
        # Nuevo Usuario: Registrar y crear notificación de bienvenida
        nuevo_usuario = Usuario(email=email, nombre=nombre)
        db.session.add(nuevo_usuario)
        
        bienvenida = Notificacion(
            usuario=nuevo_usuario,
            titulo="¡Bienvenido a Nexus Ciencia!",
            mensaje="Gracias por unirte. Ahora puedes guardar artículos en tu biblioteca personal y recibir actualizaciones."
        )
        db.session.add(bienvenida)
        db.session.add(LogActividad(
            tipo_evento=LogEventType.SISTEMA, 
            detalle=f"Nuevo Usuario: {email} | IP: {client_info['ip']}"
        ))
        log_detalle = f"Login (nuevo): {email} | IP: {client_info['ip']} | UA_HASH: {client_info['user_agent_hash']}"
    
    # Log con información de seguridad
    db.session.add(LogActividad(tipo_evento=LogEventType.LOGIN, detalle=log_detalle))
    db.session.commit()
    
    # Log adicional para monitoreo (REMEDIACIÓN CRT-002: Solo hash de email)
    logger.info(
        f"Auth success: email_hash={client_info['user_agent_hash'][:8]} ip={client_info['ip']} "
        f"ua_hash={client_info['user_agent_hash']}"
    )
    
    # REMEDIACIÓN SEC-001: Regenerar sesión para prevenir session fixation
    # Guardar datos temporalmente, limpiar sesión, y reasignar
    session.clear()
    session.modified = True
    
    # Guardar sesión con validación defensiva
    session['user_email'] = email
    session['user_name'] = nombre
    # Validar URL de imagen para prevenir inyección de URLs maliciosas
    session['user_picture'] = validar_imagen_oauth(user_info.get('picture'))
    session.permanent = True  # Usar PERMANENT_SESSION_LIFETIME
    
    return redirect(url_for('main.inicio'))


@auth_bp.route('/logout')
@limiter.limit("10 per minute")
def logout() -> Response:
    """Cierra la sesión del usuario."""
    # Log de logout con email hasheado para proteger PII
    if 'user_email' in session:
        from app.utils.helpers import hash_email
        client_info = get_client_info()
        email_hash = hash_email(session['user_email'])
        logger.info(
            f"Logout: hash={email_hash} from {client_info['ip']}"
        )
    
    session.clear()
    return redirect(url_for('main.inicio'))

