"""
Validadores de formularios centralizados para NexusCiencia.

Este módulo proporciona funciones de validación reutilizables para
formularios de administración, evitando duplicación de código.
"""

import os
import logging
from typing import Dict, List, Tuple, Optional
from werkzeug.datastructures import FileStorage

from app.constants import (
    MAX_FIELD_LENGTHS,
    ALLOWED_MIME_TYPES,
    ALLOWED_EXTENSIONS,
    LISTA_CATEGORIAS
)
from app.utils.validators import validar_url_segura, validar_longitud, validar_slug

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Excepción para errores de validación de formulario."""
    pass


def validar_archivo_upload(
    archivo: Optional[FileStorage],
    tipo: str,
    requerido: bool = True
) -> Tuple[bool, str]:
    """
    Valida un archivo subido verificando extensión, tipo MIME y magic bytes.
    
    Remediación VAL-001: Añadida validación de contenido real del archivo.
    
    Args:
        archivo: Objeto FileStorage de Flask
        tipo: Tipo de archivo esperado ('html' o 'css')
        requerido: Si el archivo es obligatorio
        
    Returns:
        Tuple de (es_valido, mensaje_error)
    """
    if not archivo or archivo.filename == '':
        if requerido:
            return False, f"El archivo {tipo.upper()} es requerido."
        return True, ""
    
    # Validar extensión
    filename = archivo.filename.lower()
    extensiones_validas = ALLOWED_EXTENSIONS.get(tipo, [])
    tiene_extension_valida = any(filename.endswith(ext) for ext in extensiones_validas)
    
    if not tiene_extension_valida:
        return False, f"Extensión inválida. Se esperaba: {', '.join(extensiones_validas)}"
    
    # REMEDIACIÓN FUN-001: Validar tamaño explícito del archivo
    # Complementa MAX_CONTENT_LENGTH con validación granular por tipo
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB para archivos HTML/CSS
    archivo.stream.seek(0, 2)  # Ir al final
    file_size = archivo.stream.tell()
    archivo.stream.seek(0)  # Volver al inicio
    
    if file_size > MAX_FILE_SIZE:
        logger.warning(f"Archivo rechazado por tamaño: {file_size} bytes (máx: {MAX_FILE_SIZE})")
        return False, f"El archivo excede el tamaño máximo permitido (5MB)."
    
    # Validar tipo MIME
    mime_types_validos = ALLOWED_MIME_TYPES.get(tipo, [])
    if archivo.content_type and archivo.content_type not in mime_types_validos:
        # Log el intento pero permitir si la extensión es válida
        # (algunos navegadores reportan MIME incorrecto)
        logger.warning(
            f"MIME type inesperado para {tipo}: {archivo.content_type} "
            f"(archivo: {archivo.filename}). Extensión válida, continuando."
        )
    
    # Remediación VAL-001: Validar contenido real del archivo (magic bytes)
    from app.utils.helpers import validate_file_magic_bytes
    
    # Leer primeros bytes para validación
    current_pos = archivo.stream.tell()
    header = archivo.stream.read(2048)
    archivo.stream.seek(current_pos)  # Restaurar posición
    
    if not validate_file_magic_bytes(header, tipo):
        logger.warning(
            f"Archivo rechazado: contenido no coincide con tipo {tipo} "
            f"(archivo: {archivo.filename})"
        )
        return False, f"El contenido del archivo no parece ser {tipo.upper()} válido."
    
    return True, ""


def validar_formulario_articulo(form_data: Dict[str, str]) -> List[str]:
    """
    Valida todos los campos del formulario de artículo.
    
    Args:
        form_data: Diccionario con datos del formulario
        
    Returns:
        Lista de mensajes de error (vacía si todo es válido)
    """
    errores = []
    
    # Campos de texto con límites de longitud
    campos_texto = ['titulo', 'slug', 'tags', 'categoria']
    
    for campo in campos_texto:
        valor = form_data.get(campo, '').strip()
        max_length = MAX_FIELD_LENGTHS.get(campo, 200)
        
        if not validar_longitud(valor, max_length):
            errores.append(
                f"Error: {campo.capitalize()} no puede exceder {max_length} caracteres."
            )
    
    # Campos obligatorios
    if not form_data.get('titulo', '').strip():
        errores.append("Error: El título es obligatorio.")
    
    if not form_data.get('slug', '').strip():
        errores.append("Error: El slug es obligatorio.")
    else:
        # Validar formato de slug para prevenir path traversal
        slug = form_data.get('slug', '').strip()
        if not validar_slug(slug):
            errores.append(
                "Error: Slug inválido. Solo puede contener letras minúsculas, "
                "números y guiones (ej: 'mi-articulo-2024')."
            )
    
    # Validar URLs
    url_pdf = form_data.get('url_pdf', '').strip()
    url_audio = form_data.get('url_audio', '').strip()
    
    if not validar_url_segura(url_pdf):
        errores.append("Error: La URL del PDF no es válida (solo http/https).")
    
    if not validar_url_segura(url_audio):
        errores.append("Error: La URL del audio no es válida (solo http/https).")
    
    # Validar categoría usando método centralizado (REMEDIACIÓN: elimina duplicación)
    categoria = form_data.get('categoria', '').strip()
    if categoria:
        from app.models.categoria import Categoria
        categorias_validas = Categoria.get_nombres_con_fallback()
        
        if categoria not in categorias_validas:
            errores.append("Error: La categoría seleccionada no es válida.")
    
    return errores


def obtener_categorias_validas() -> List[str]:
    """
    Obtiene la lista de categorías válidas.
    REMEDIACIÓN: Ahora usa método centralizado del modelo.
    
    Returns:
        Lista de nombres de categorías válidas
    """
    from app.models.categoria import Categoria
    return Categoria.get_nombres_con_fallback()
