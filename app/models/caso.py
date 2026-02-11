"""
Modelo de Caso Clínico con soporte para soft delete y archivos HTML
"""

from datetime import datetime, timezone
import logging
from app.extensions import db
from app.enums import LogEventType

logger = logging.getLogger(__name__)


class CasoClinico(db.Model):
    """Modelo de caso clínico para estudiantes de psicología"""
    
    __tablename__ = 'caso_clinico'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    numero = db.Column(db.String(10), nullable=False)  # Número de caso (01, 02, etc.)
    nivel = db.Column(db.String(50), default='Intermedio')  # Principiante, Intermedio, Avanzado
    nivel_color = db.Column(db.String(20), default='amber')  # emerald, amber, rose
    sintomatologia = db.Column(db.Text)  # Síntomas separados por |
    edad_paciente = db.Column(db.String(50))
    sexo = db.Column(db.String(20))
    nombre_archivo = db.Column(db.String(200), nullable=False)  # Referencia al HTML estático
    descripcion = db.Column(db.String(300), nullable=True)  # Meta description
    fecha = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft delete
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc), index=True)
    
    def __repr__(self):
        return f'<CasoClinico {self.titulo}>'
    
    def get_sintomas_lista(self):
        """Retorna la sintomatología como lista."""
        if self.sintomatologia:
            return [s.strip() for s in self.sintomatologia.split('|') if s.strip()]
        return []
    
    def set_sintomas_lista(self, lista):
        """Establece la sintomatología desde una lista."""
        self.sintomatologia = ' | '.join(lista) if lista else ''
    
    def soft_delete(self):
        """Marca el caso como eliminado sin borrarlo físicamente."""
        from app.models.log import LogActividad
        
        self.deleted_at = datetime.now(timezone.utc)
        db.session.add(LogActividad(tipo_evento=LogEventType.ADMIN, detalle=f"Caso eliminado: {self.titulo}"))
        logger.info(f"Caso soft-deleted: {self.slug}")
    
    def restore(self):
        """Restaura un caso previamente eliminado."""
        from app.models.log import LogActividad
        
        self.deleted_at = None
        db.session.add(LogActividad(tipo_evento=LogEventType.ADMIN, detalle=f"Caso restaurado: {self.titulo}"))
        logger.info(f"Caso restaurado: {self.slug}")
    
    @staticmethod
    def get_active():
        """Retorna query solo con casos no eliminados."""
        return CasoClinico.query.filter(CasoClinico.deleted_at.is_(None))
    
    @staticmethod
    def get_deleted():
        """Retorna query solo con casos eliminados."""
        return CasoClinico.query.filter(CasoClinico.deleted_at.isnot(None))
    
    @staticmethod
    def get_next_number():
        """Calcula el siguiente número de caso disponible."""
        ultimo = CasoClinico.query.order_by(CasoClinico.id.desc()).first()
        if ultimo:
            try:
                num = int(ultimo.numero) + 1
            except (ValueError, TypeError):
                num = CasoClinico.query.count() + 1
        else:
            num = 1
        return str(num).zfill(2)
