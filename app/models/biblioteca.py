"""
Tabla de asociación para relación Muchos-a-Muchos entre Usuario y Artículo
"""

from app.extensions import db

# Tabla intermedia para relación Muchos-a-Muchos (Usuario <-> Artículos Guardados)
biblioteca = db.Table('biblioteca',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuario.id'), primary_key=True),
    db.Column('articulo_id', db.Integer, db.ForeignKey('articulo.id'), primary_key=True)
)
