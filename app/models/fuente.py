"""
Modelo de Fuente Académica para repositorio de papers y documentos
"""

from datetime import datetime, timezone
import logging
from app.extensions import db
from app.enums import LogEventType

logger = logging.getLogger(__name__)


class FuenteAcademica(db.Model):
    """Modelo de fuente académica (papers, DOIs, PDFs)"""
    
    __tablename__ = 'fuente_academica'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(300), nullable=False)
    autor = db.Column(db.String(200), nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    fuente_origen = db.Column(db.String(100), nullable=False)  # PubMed, Scopus, ScienceDirect, etc.
    tipo = db.Column(db.String(10), default='PDF')  # PDF o DOI
    doi = db.Column(db.String(200))
    url_descarga = db.Column(db.String(500))
    categoria = db.Column(db.String(100), index=True)  # Tag temático
    fecha = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft delete
    
    def __repr__(self):
        return f'<FuenteAcademica {self.titulo}>'
    
    def soft_delete(self):
        """Marca la fuente como eliminada sin borrarla físicamente."""
        from app.models.log import LogActividad
        
        self.deleted_at = datetime.now(timezone.utc)
        db.session.add(LogActividad(tipo_evento=LogEventType.ADMIN, detalle=f"Fuente eliminada: {self.titulo}"))
        logger.info(f"Fuente soft-deleted: {self.titulo}")
    
    def restore(self):
        """Restaura una fuente previamente eliminada."""
        from app.models.log import LogActividad
        
        self.deleted_at = None
        db.session.add(LogActividad(tipo_evento=LogEventType.ADMIN, detalle=f"Fuente restaurada: {self.titulo}"))
        logger.info(f"Fuente restaurada: {self.titulo}")
    
    @staticmethod
    def get_active():
        """Retorna query solo con fuentes no eliminadas."""
        return FuenteAcademica.query.filter(FuenteAcademica.deleted_at.is_(None))
    
    @staticmethod
    def get_deleted():
        """Retorna query solo con fuentes eliminadas."""
        return FuenteAcademica.query.filter(FuenteAcademica.deleted_at.isnot(None))
