"""
Tests para funcionalidad de soft delete
"""

import pytest
from datetime import datetime, timezone
from app import db
from app.models.articulo import Articulo


def test_soft_delete_marca_deleted_at(app):
    """Soft delete debe marcar deleted_at sin eliminar registro"""
    with app.app_context():
        art = Articulo(
            titulo='Test Article',
            slug='test-article',
            categoria='Test',
            tags='test',
            nombre_archivo='test.html'
        )
        db.session.add(art)
        db.session.commit()
        article_id = art.id
        
        # Soft delete
        art.soft_delete()
        
        # Verificar que deleted_at está marcado
        assert art.deleted_at is not None
        assert isinstance(art.deleted_at, datetime)
        
        # Verificar que el registro SIGUE en BD
        # Soft delete - verify article still exists
        # REMEDIACIÓN: Usar db.session.get() en lugar de Query.get() deprecado
        still_exists = db.session.get(Articulo, article_id)
        assert still_exists is not None


def test_restore_limpia_deleted_at(app):
    """Restore debe limpiar deleted_at"""
    with app.app_context():
        art = Articulo(
            titulo='Test Restore',
            slug='test-restore',
            categoria='Test',
            tags='test',
            nombre_archivo='test.html'
        )
        db.session.add(art)
        db.session.commit()
        
        # Soft delete
        art.soft_delete()
        assert art.deleted_at is not None
        
        # Restore
        art.restore()
        assert art.deleted_at is None


def test_get_active_excluye_eliminados(app):
    """get_active() debe retornar solo artículos no eliminados"""
    with app.app_context():
        # Crear artículo activo
        art_active = Articulo(
            titulo='Active',
            slug='active',
            categoria='Test',
            tags='test',
            nombre_archivo='active.html'
        )
        # Crear artículo eliminado
        art_deleted = Articulo(
            titulo='Deleted',
            slug='deleted',
            categoria='Test',
            tags='test',
            nombre_archivo='deleted.html'
        )
        db.session.add_all([art_active, art_deleted])
        db.session.commit()
        
        # Soft delete uno
        art_deleted.soft_delete()
        
        # Verificar get_active()
        activos = Articulo.get_active().all()
        assert art_active in activos
        assert art_deleted not in activos


def test_get_deleted_solo_eliminados(app):
    """get_deleted() debe retornar solo artículos eliminados"""
    with app.app_context():
        # Crear artículos
        art1 = Articulo(titulo='A1', slug='a1', categoria='T', tags='t', nombre_archivo='a.html')
        art2 = Articulo(titulo='A2', slug='a2', categoria='T', tags='t', nombre_archivo='b.html')
        db.session.add_all([art1, art2])
        db.session.commit()
        
        # Eliminar solo uno
        art2.soft_delete()
        
        # Verificar get_deleted()
        eliminados = Articulo.get_deleted().all()
        assert art1 not in eliminados
        assert art2 in eliminados
