"""
Modelo de Categoría para sistema dinámico de categorías
"""

from datetime import datetime, timezone
from app.extensions import db


class Categoria(db.Model):
    """Modelo de categoría de artículos (reemplaza lista hardcoded)"""
    
    __tablename__ = 'categoria'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True, index=True)
    icono = db.Column(db.String(10))  # Emoji
    orden = db.Column(db.Integer, default=0)  # Para ordenamiento
    activa = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Nota: Relación con artículos se define después de migración completa
    # articulos = db.relationship('Articulo', backref='categoria_obj', lazy='dynamic')
    
    def __repr__(self):
        return f'<Categoria {self.nombre}>'
    
    @staticmethod
    def get_activas():
        """Retorna solo categorías activas ordenadas."""
        return Categoria.query.filter_by(activa=True).order_by(Categoria.orden).all()
    
    @staticmethod
    def get_nombres_activos():
        """Retorna lista de nombres de categorías activas (para validación)."""
        return [cat.nombre for cat in Categoria.get_activas()]
    
    @staticmethod
    def get_nombres_con_fallback():
        """
        Obtiene nombres de categorías desde BD con fallback a constantes.
        
        REMEDIACIÓN: Centraliza lógica que estaba duplicada en form_validators.py
        y __init__.py context processor.
        
        Returns:
            Lista de nombres de categorías válidas
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            categorias_db = Categoria.get_nombres_activos()
            if categorias_db:
                return categorias_db
        except Exception as e:
            logger.debug(f"Usando categorías estáticas: {e.__class__.__name__}")
        
        from app.constants import LISTA_CATEGORIAS
        return LISTA_CATEGORIAS.copy()
