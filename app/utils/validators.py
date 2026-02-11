"""
Validadores para URLs, categorías y otros datos de entrada
"""

import os
import re
import logging
from urllib.parse import urlparse
from typing import Optional

logger = logging.getLogger(__name__)


def validar_slug(slug: Optional[str]) -> bool:
    """
    Valida que un slug sea seguro para uso en rutas de archivo.
    Previene path traversal y caracteres peligrosos.
    
    Formato válido: solo letras minúsculas, números y guiones.
    Ejemplos válidos: 'mi-articulo', 'articulo-2024', 'neurociencia-101'
    Ejemplos inválidos: '../etc/passwd', 'Mi Artículo', 'articulo.html'
    
    Args:
        slug: Slug a validar
        
    Returns:
        bool: True si el slug es seguro, False en caso contrario
    """
    if not slug:
        return False
    
    slug = slug.strip()
    
    # Verificar longitud
    if len(slug) < 3 or len(slug) > 200:
        return False
    
    # Solo permitir letras minúsculas, números y guiones
    # NO permitir: espacios, puntos, barras, caracteres especiales
    pattern = r'^[a-z0-9]+(-[a-z0-9]+)*$'
    return bool(re.match(pattern, slug))


def validar_url_segura(url: Optional[str]) -> bool:
    """
    Valida que una URL sea segura (solo http/https).
    Previene XSS vía javascript: URLs y rechaza protocol-relative URLs.
    
    Args:
        url: URL a validar
        
    Returns:
        bool: True si la URL es segura, False en caso contrario
    """
    if not url or url.strip() == '':
        return True  # URLs vacías son válidas (campo opcional)
    
    url = url.strip()
    
    try:
        # Rechazar protocol-relative URLs que podrían apuntar a dominios externos
        # Ej: "//evil.com/xss" se interpreta como https://evil.com/xss en HTTPS
        if url.startswith('//'):
            logger.warning(f"URL rechazada: protocol-relative URL no permitida - {url[:50]}")
            return False
        
        parsed = urlparse(url)
        
        # Si tiene scheme, debe ser http o https
        if parsed.scheme:
            return parsed.scheme in ['http', 'https']
        
        # Sin scheme: es una ruta relativa, permitida
        # urlparse trata URLs malformadas como rutas relativas (scheme='')
        # Ej: "ht!tp://bad" -> scheme='', path='ht!tp://bad'
        return True
        
    except Exception:
        return False


def validar_categoria_nombre(nombre: Optional[str]) -> bool:
    """
    Valida que un nombre de categoría exista en la base de datos.
    
    Args:
        nombre: Nombre de la categoría a validar
        
    Returns:
        bool: True si la categoría existe, False en caso contrario
    """
    # Importación tardía para evitar circular imports
    from app.models.categoria import Categoria
    
    if not nombre or nombre.strip() == '':
        return True  # Categoría vacía es válida (opcional)
    
    return Categoria.query.filter_by(nombre=nombre.strip(), activa=True).first() is not None


def validar_longitud(texto: Optional[str], max_length: int) -> bool:
    """
    Valida que un texto no exceda la longitud máxima.
    
    Args:
        texto: Texto a validar
        max_length: Longitud máxima permitida
        
    Returns:
        bool: True si cumple, False si excede
    """
    if not texto:
        return True
    return len(texto.strip()) <= max_length


def validar_extension_archivo(
    filename: Optional[str], 
    extensiones_permitidas: list
) -> bool:
    """
    Valida que un archivo tenga una extensión permitida.
    
    Args:
        filename: Nombre del archivo
        extensiones_permitidas: Lista de extensiones válidas (ej: ['.html', '.htm'])
        
    Returns:
        bool: True si la extensión es válida
    """
    if not filename:
        return False
    
    filename_lower = filename.lower()
    return any(filename_lower.endswith(ext) for ext in extensiones_permitidas)


def validar_mime_type(
    content_type: Optional[str],
    mime_types_permitidos: list,
    filename: Optional[str] = None
) -> bool:
    """
    Valida el tipo MIME de un archivo.
    
    Args:
        content_type: Tipo MIME reportado por el navegador
        mime_types_permitidos: Lista de tipos MIME válidos
        filename: Nombre del archivo (para validación secundaria)
        
    Returns:
        bool: True si el tipo es válido o aceptable
    """
    if not content_type:
        # Sin tipo reportado, verificar extensión si está disponible
        logger.warning(f"MIME type no proporcionado para archivo: {filename}")
        return True  # Permitir pero con warning
    
    if content_type in mime_types_permitidos:
        return True
    
    # Algunos navegadores reportan MIME incorrecto
    # Log y permitir solo si la extensión es explícitamente válida
    logger.warning(
        f"MIME type inesperado: {content_type} para {filename}. "
        f"Esperado: {mime_types_permitidos}"
    )
    
    # application/octet-stream: Solo permitir si la extensión es válida
    if content_type == 'application/octet-stream':
        if filename:
            # Validar extensión antes de aceptar octet-stream
            ext = os.path.splitext(filename.lower())[1]
            extensiones_seguras = ['.html', '.htm', '.css', '.txt']
            if ext in extensiones_seguras:
                logger.info(f"Aceptando octet-stream para extensión segura: {ext}")
                return True
            else:
                logger.warning(f"Rechazando octet-stream para extensión desconocida: {ext}")
                return False
        return False  # Sin filename, rechazar octet-stream
    
    return False

