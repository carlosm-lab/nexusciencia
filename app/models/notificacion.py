"""
Modelo de Notificación para usuarios
"""

from datetime import datetime, timezone
from app.extensions import db


class Notificacion(db.Model):
    """Modelo de notificación para usuarios"""
    
    __tablename__ = 'notificacion'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    titulo = db.Column(db.String(100), nullable=False)
    mensaje = db.Column(db.String(500), nullable=False)
    fecha = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    leido = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Notificacion {self.titulo}>'
