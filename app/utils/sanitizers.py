"""
Sanitizadores HTML para protección contra XSS.

Este módulo usa nh3 (reemplazo moderno de bleach) para sanitización
de HTML subido por administradores.
"""

import nh3
from bs4 import BeautifulSoup


# Etiquetas HTML permitidas para contenido de artículos
ALLOWED_TAGS = {
    'p', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'a', 'img', 'br', 'div', 'span', 'blockquote',
    'code', 'pre', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'sup', 'sub', 'hr'
}

# Atributos permitidos por etiqueta
ALLOWED_ATTRS = {
    'a': {'href', 'title'},
    'img': {'src', 'alt', 'title'},
    'div': {'class'},
    'span': {'class'},
    'td': {'colspan', 'rowspan'},
    'th': {'colspan', 'rowspan'},
    'code': {'class'},
    'pre': {'class'},
}


def limpiar_html_google(contenido_raw: str) -> str:
    """
    Sanitiza el HTML subido por el administrador.
    
    Proceso de limpieza:
        1. Elimina scripts, estilos y contenido peligroso con BeautifulSoup
        2. Sanitiza con nh3 (más rápido que bleach)
        3. Post-procesa para añadir atributos de seguridad y UX
    
    Args:
        contenido_raw: HTML sin sanitizar
        
    Returns:
        HTML sanitizado y seguro
    """
    if not contenido_raw:
        return ''
    
    # PASO 1: Eliminar tags peligrosos con BeautifulSoup
    soup = BeautifulSoup(contenido_raw, 'html.parser')
    
    # Eliminar completamente script, style, head, etc.
    tags_peligrosos = ['script', 'style', 'head', 'meta', 'link', 'title', 
                       'xml', 'iframe', 'object', 'embed', 'form']
    for tag in soup.find_all(tags_peligrosos):
        tag.decompose()
    
    # Obtener HTML pre-limpiado
    html_prelimpiado = str(soup)
    
    # PASO 2: Sanitizar con nh3 (más rápido y moderno que bleach)
    cleaned = nh3.clean(
        html_prelimpiado,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        strip_comments=True,
    )
    
    # PASO 3: Post-procesamiento para UX y seguridad
    soup_final = BeautifulSoup(cleaned, 'html.parser')
    
    # Asegurar target="_blank" y rel="noopener" en enlaces externos
    for link in soup_final.find_all('a'):
        href = link.get('href', '')
        # Solo aplicar a enlaces externos
        if href.startswith(('http://', 'https://')):
            link['target'] = '_blank'
            link['rel'] = 'noopener noreferrer'
    
    # Añadir clases responsive y lazy loading a imágenes
    for img in soup_final.find_all('img'):
        existing_classes = img.get('class', [])
        if isinstance(existing_classes, str):
            existing_classes = existing_classes.split()
        new_classes = list(set(existing_classes + ['img-fluid', 'rounded', 'my-3']))
        img['class'] = ' '.join(new_classes)
        img['loading'] = 'lazy'
        # Asegurar alt text para accesibilidad
        if not img.get('alt'):
            img['alt'] = 'Imagen del artículo'
    
    return str(soup_final)


def sanitizar_texto_plano(texto: str, max_length: int = 500) -> str:
    """
    Sanitiza texto plano eliminando cualquier HTML.
    
    Args:
        texto: Texto a sanitizar
        max_length: Longitud máxima permitida
        
    Returns:
        Texto limpio sin HTML
    """
    if not texto:
        return ''
    
    # Eliminar todo HTML
    cleaned = nh3.clean(texto, tags=set())
    
    # Truncar si es necesario
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length-3] + '...'
    
    return cleaned.strip()


def validar_css_seguro(contenido_css: str) -> tuple[bool, str]:
    """
    Valida y sanitiza contenido CSS para prevenir inyección de código.
    
    Detecta y bloquea patrones peligrosos como:
        - @import (puede cargar recursos externos)
        - expression() (ejecución de JS en IE)
        - javascript: en URLs
        - behavior: (ejecución de HTC en IE)
        - -moz-binding (ejecución de XBL en Firefox antiguo)
    
    Args:
        contenido_css: CSS a validar
        
    Returns:
        Tuple (es_valido, mensaje_error o css_limpio)
    """
    import re
    import logging
    
    logger = logging.getLogger(__name__)
    
    if not contenido_css:
        return True, ''
    
    # Patrones peligrosos en CSS
    # REMEDIACIÓN FUNCIONAL-001: Añadido patrón url() para prevenir exfiltración
    PATRONES_PELIGROSOS = [
        (r'@import\s', 'Regla @import no permitida'),
        (r'expression\s*\(', 'expression() no permitido'),
        (r'javascript\s*:', 'URLs javascript: no permitidas'),
        (r'vbscript\s*:', 'URLs vbscript: no permitidas'),
        (r'behavior\s*:', 'Propiedad behavior: no permitida'),
        (r'-moz-binding\s*:', 'Propiedad -moz-binding no permitida'),
        (r'<\s*script', 'Tags script no permitidos'),
        (r'<\s*style', 'Tags style anidados no permitidos'),
        # NUEVO: Detectar URLs externas (exfiltración de datos)
        (r'url\s*\(\s*["\']?https?://', 'URLs externas en CSS no permitidas (usar recursos locales)'),
    ]
    
    css_lower = contenido_css.lower()
    
    for patron, mensaje in PATRONES_PELIGROSOS:
        if re.search(patron, css_lower, re.IGNORECASE):
            logger.warning(f"CSS rechazado: {mensaje}")
            return False, f"Error de seguridad: {mensaje}"
    
    # Verificar que solo contenga CSS válido (no HTML ni JS)
    # Detectar apertura de tags HTML
    if re.search(r'<\s*[a-z]', css_lower):
        logger.warning("CSS rechazado: contiene tags HTML")
        return False, "Error: El archivo parece contener HTML, no CSS puro"
    
    logger.info("CSS validado correctamente")
    return True, contenido_css
