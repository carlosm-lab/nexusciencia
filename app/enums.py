"""
Enumeraciones globales de NexusCiencia.

Este módulo centraliza todas las enumeraciones usadas en la aplicación
para evitar magic strings y garantizar consistencia.
"""

from enum import Enum


class LogEventType(str, Enum):
    """
    Tipos de eventos para el sistema de auditoría.
    
    Hereda de str para serialización automática y comparación directa.
    
    Uso:
        from app.enums import LogEventType
        LogActividad(tipo_evento=LogEventType.LOGIN, detalle="...")
    """
    LOGIN = 'login'
    LOGOUT = 'logout'
    ADMIN = 'admin'
    LECTURA = 'lectura'
    SISTEMA = 'sistema'
    ERROR = 'error'
    
    def __str__(self) -> str:
        return self.value


class ArticleStatus(str, Enum):
    """Estados posibles de un artículo."""
    ACTIVE = 'active'
    DELETED = 'deleted'
    DRAFT = 'draft'
    
    def __str__(self) -> str:
        return self.value
