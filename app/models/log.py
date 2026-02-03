"""
Modelo de Log de Actividad para auditoría del sistema.
"""

from datetime import datetime, timezone
from app.extensions import db
from app.enums import LogEventType


class LogActividad(db.Model):
    """
    Sistema de auditoría para registrar eventos clave del sistema.
    
    Tipos de evento:
        - LOGIN: Inicio de sesión de usuario
        - LOGOUT: Cierre de sesión
        - ADMIN: Acciones administrativas
        - LECTURA: Lectura de artículos
        - SISTEMA: Eventos del sistema
        - ERROR: Errores capturados
    """
    
    __tablename__ = 'log_actividad'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo_evento = db.Column(db.String(50), nullable=False, index=True)
    detalle = db.Column(db.String(255))
    fecha = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    def __init__(self, tipo_evento, detalle=None):
        """
        Crea un nuevo registro de log.
        
        Args:
            tipo_evento: LogEventType o string del tipo de evento
            detalle: Descripción del evento (máx 255 chars)
        """
        # Aceptar tanto Enum como string para compatibilidad
        if isinstance(tipo_evento, LogEventType):
            self.tipo_evento = tipo_evento.value
        else:
            self.tipo_evento = str(tipo_evento)
        self.detalle = detalle[:255] if detalle else None
    
    def __repr__(self):
        return f'<LogActividad {self.tipo_evento}: {self.detalle[:30] if self.detalle else "N/A"}>'
    
    @classmethod
    def registrar(cls, tipo: LogEventType, detalle: str = None):
        """
        Método de conveniencia para registrar eventos.
        
        Args:
            tipo: LogEventType del evento
            detalle: Descripción opcional
            
        Returns:
            LogActividad: Instancia creada (no commiteada)
        """
        return cls(tipo_evento=tipo, detalle=detalle)

