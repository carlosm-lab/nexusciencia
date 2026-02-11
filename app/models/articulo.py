"""
Modelo de Artículo con soporte para soft delete
"""

from datetime import datetime, timezone
import logging
from app.extensions import db
from app.enums import LogEventType

logger = logging.getLogger(__name__)


class Articulo(db.Model):
    """Modelo de artículo educativo"""
    
    __tablename__ = 'articulo'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    categoria = db.Column(db.String(100), index=True)  # Índice para búsquedas
    tags = db.Column(db.String(200), index=True)  # Índice para búsquedas
    nombre_archivo = db.Column(db.String(200), nullable=False)  # Referencia al HTML estático
    url_pdf = db.Column(db.String(500))
    url_audio = db.Column(db.String(500))
    fecha = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)  # Timezone aware
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft delete
    # SEO Optimization: descripción para meta tags únicos (Auditoría SEO 3.1)
    descripcion = db.Column(db.String(300), nullable=True)  # Meta description única por artículo
    # SEO Optimization: fecha de última actualización para schema.org dateModified
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc), index=True)
    
    def __repr__(self):
        return f'<Articulo {self.titulo}>'
    
    def soft_delete(self):
        """
        Marca el artículo como eliminado sin borrarlo físicamente.
        
        NOTA LOG-001: Este método NO hace commit. La capa de rutas es responsable
        de llamar db.session.commit() para garantizar transaccionalidad.
        """
        from app.models.log import LogActividad
        
        self.deleted_at = datetime.now(timezone.utc)
        db.session.add(LogActividad(tipo_evento=LogEventType.ADMIN, detalle=f"Eliminado (soft): {self.titulo}"))
        logger.info(f"Artículo soft-deleted: {self.slug}")
    
    def restore(self):
        """
        Restaura un artículo previamente eliminado.
        
        NOTA LOG-001: Este método NO hace commit. La capa de rutas es responsable
        de llamar db.session.commit() para garantizar transaccionalidad.
        """
        from app.models.log import LogActividad
        
        self.deleted_at = None
        db.session.add(LogActividad(tipo_evento=LogEventType.ADMIN, detalle=f"Restaurado: {self.titulo}"))
        logger.info(f"Artículo restaurado: {self.slug}")
    
    @staticmethod
    def get_active():
        """Retorna query solo con artículos no eliminados."""
        return Articulo.query.filter(Articulo.deleted_at.is_(None))
    
    @staticmethod
    def get_deleted():
        """Retorna query solo con artículos eliminados."""
        return Articulo.query.filter(Articulo.deleted_at.isnot(None))
