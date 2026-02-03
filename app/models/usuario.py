"""
Modelo de Usuario con relaciones a artículos y notificaciones
"""

from datetime import datetime, timezone
from app.extensions import db
from app.models.biblioteca import biblioteca


class Usuario(db.Model):
    """Modelo de usuario autenticado vía OAuth"""
    
    __tablename__ = 'usuario'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(120))
    fecha_registro = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    fecha_ultimo_login = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relaciones: ORDEN DESCENDENTE (Global para la biblioteca personal)
    articulos_guardados = db.relationship(
        'Articulo',
        secondary=biblioteca,
        order_by='Articulo.fecha.desc()',
        backref=db.backref('guardado_por', lazy='dynamic')
    )
    notificaciones = db.relationship('Notificacion', backref='usuario', lazy=True)
    
    def __repr__(self):
        return f'<Usuario {self.email}>'
