"""
Tests de Modelos de Base de Datos para NexusCiencia
"""
import pytest
from datetime import datetime
from app.extensions import db
from app.models.articulo import Articulo
from app.models.usuario import Usuario
from app.models.log import LogActividad


def test_crear_usuario(app):
    """Test: Crear un nuevo usuario en la base de datos."""
    with app.app_context():
        usuario = Usuario(
            email='test@example.com',
            nombre='Usuario de Prueba'
        )
        db.session.add(usuario)
        db.session.commit()
        
        # Verificar que se guardó correctamente
        usuario_db = Usuario.query.filter_by(email='test@example.com').first()
        assert usuario_db is not None
        assert usuario_db.nombre == 'Usuario de Prueba'
        assert usuario_db.fecha_registro is not None


def test_crear_articulo(app):
    """Test: Crear un nuevo artículo."""
    with app.app_context():
        articulo = Articulo(
            titulo='Artículo de Prueba',
            slug='articulo-prueba',
            categoria='Test',
            tags='test, prueba',
            nombre_archivo='prueba.html'
        )
        db.session.add(articulo)
        db.session.commit()
        
        articulo_db = Articulo.query.filter_by(slug='articulo-prueba').first()
        assert articulo_db is not None
        assert articulo_db.titulo == 'Artículo de Prueba'


def test_usuario_articulos_guardados(app):
    """Test: Relación muchos-a-muchos usuario-artículos."""
    with app.app_context():
        # Crear usuario y artículo
        usuario = Usuario(email='test@example.com', nombre='Test')
        articulo = Articulo(
            titulo='Test Article',
            slug='test-article',
            categoria='Test',
            tags='test',
            nombre_archivo='test.html'
        )
        db.session.add(usuario)
        db.session.add(articulo)
        db.session.commit()
        
        # Guardar artículo en biblioteca
        usuario.articulos_guardados.append(articulo)
        db.session.commit()
        
        # Verificar relación
        usuario_db = Usuario.query.filter_by(email='test@example.com').first()
        assert len(usuario_db.articulos_guardados) == 1
        assert usuario_db.articulos_guardados[0].slug == 'test-article'


def test_log_actividad(app):
    """Test: Crear registro de log de actividad."""
    with app.app_context():
        log = LogActividad(
            tipo_evento='test',
            detalle='Test log entry'
        )
        db.session.add(log)
        db.session.commit()
        
        log_db = LogActividad.query.filter_by(tipo_evento='test').first()
        assert log_db is not None
        assert 'Test log' in log_db.detalle
