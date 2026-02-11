"""
Helper functions y utilidades generales
"""

import hashlib
from datetime import datetime, timezone, timedelta
from flask import session, current_app
from flask_limiter.util import get_remote_address


# =============================================================================
# SEGURIDAD: HASH DE INFORMACIÓN PERSONAL
# =============================================================================

def hash_email(email: str, length: int = 16) -> str:
    """
    Genera hash truncado de email para logging seguro.
    
    Previene exposición de PII en logs mientras mantiene
    capacidad de correlación para debugging.
    
    Args:
        email: Email a hashear
        length: Longitud del hash truncado (default: 16)
        
    Returns:
        str: Hash SHA256 truncado del email
    """
    if not email:
        return 'unknown'
    return hashlib.sha256(email.encode()).hexdigest()[:length]


# =============================================================================
# CONFIGURACIÓN DE SESIÓN
# =============================================================================

# Timeout de inactividad de sesión (configurable vía env)
import os
SESSION_INACTIVITY_MINUTES = int(os.getenv('SESSION_INACTIVITY_MINUTES', 30))
SESSION_INACTIVITY_TIMEOUT = timedelta(minutes=SESSION_INACTIVITY_MINUTES)


def get_rate_limit_key():
    """
    Key function para rate limiting.
    Usa email de usuario si está autenticado, sino usa IP.
    
    Returns:
        str: Email del usuario o IP address
    """
    return session.get('user_email') or get_remote_address()


def check_session_timeout():
    """
    Verifica si la sesión ha expirado por inactividad.
    
    Implementa timeout de 30 minutos de inactividad para prevenir
    sesiones robadas que permanecen válidas indefinidamente.
    
    Remediación: AUTH-001
    """
    if 'user_email' not in session:
        return  # No hay sesión activa
    
    last_activity = session.get('last_activity')
    now = datetime.now(timezone.utc)
    
    if last_activity:
        # Convertir si es necesario (sesiones antiguas pueden tener string)
        if isinstance(last_activity, str):
            try:
                last_activity = datetime.fromisoformat(last_activity)
                # REMEDIACIÓN FUN-001: Asegurar timezone-aware para comparación válida
                if last_activity.tzinfo is None:
                    last_activity = last_activity.replace(tzinfo=timezone.utc)
            except ValueError:
                last_activity = now
        # REMEDIACIÓN FUN-001: Manejar datetime objects sin timezone
        elif isinstance(last_activity, datetime) and last_activity.tzinfo is None:
            last_activity = last_activity.replace(tzinfo=timezone.utc)
        
        # Verificar timeout
        if now - last_activity > SESSION_INACTIVITY_TIMEOUT:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Sesión expirada por inactividad: {hash_email(session.get('user_email', ''))}")
            session.clear()
            return
    
    # Actualizar última actividad
    session['last_activity'] = now.isoformat()

# =============================================================================
# CONSTANTES DE VALIDACIÓN DE ARCHIVOS (REMEDIACIÓN DT-004)
# =============================================================================

# Longitud del BOM UTF-8 (Byte Order Mark: EF BB BF)
UTF8_BOM_LENGTH = 3

# Tamaño de muestra para validación de CSS (bytes)
# Suficiente para detectar patrones peligrosos sin procesar archivo completo
CSS_VALIDATION_SAMPLE_SIZE = 2048

# Magic bytes para validación de archivos
FILE_MAGIC_BYTES = {
    'html': [
        b'<!DOCTYPE',
        b'<!doctype',
        b'<html',
        b'<HTML',
        b'<head',
        b'<HEAD',
        b'<body',
        b'<BODY',
        b'<!--',
    ],
    'css': [
        # CSS no tiene magic bytes estándar, validamos por contenido
    ],
}


def validate_file_magic_bytes(file_content: bytes, expected_type: str) -> bool:
    """
    Valida el contenido real de un archivo usando magic bytes.
    
    Previene uploads de archivos renombrados con extensiones falsas.
    
    Args:
        file_content: Primeros bytes del archivo
        expected_type: Tipo esperado ('html', 'css')
        
    Returns:
        bool: True si el contenido coincide con el tipo esperado
        
    Remediación: VAL-001
    """
    if not file_content:
        return False
    
    # Limpiar BOM y whitespace inicial
    content = file_content.lstrip()
    if content.startswith(b'\xef\xbb\xbf'):  # UTF-8 BOM
        content = content[UTF8_BOM_LENGTH:].lstrip()  # REMEDIACIÓN DT-004
    
    if expected_type == 'html':
        magic_patterns = FILE_MAGIC_BYTES['html']
        return any(content.startswith(pattern) for pattern in magic_patterns)
    
    elif expected_type == 'css':
        # CSS: verificar que no contenga tags HTML y tenga estructura CSS válida
        # REMEDIACIÓN DT-004: Usar constante en lugar de magic number
        content_str = content[:CSS_VALIDATION_SAMPLE_SIZE].decode('utf-8', errors='ignore').lower()
        
        # Rechazar si parece HTML
        if any(tag in content_str for tag in ['<html', '<head', '<body', '<script', '<!doctype']):
            return False
        
        # Aceptar si tiene patrones CSS comunes
        # REMEDIACIÓN DT-003: @import removido (está bloqueado en sanitizers.py)
        css_patterns = ['{', ':', ';', '@media', '@font-face', '@keyframes']
        return any(pattern in content_str for pattern in css_patterns)
    
    return True  # Tipo no verificable, permitir
