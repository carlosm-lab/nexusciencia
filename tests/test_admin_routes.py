"""
Tests para rutas de administración de NexusCiencia
Cubre: CRUD de artículos, sincronización, paginación de logs
"""
import pytest
from app.extensions import db
from app.models.articulo import Articulo
from app.models.usuario import Usuario
from app.models.log import LogActividad


class TestAdminRoutes:
    """Tests para rutas del panel de administración"""
    
    def test_admin_sin_auth_redirige_login(self, client):
        """Admin debe redirigir a login sin autenticación."""
        response = client.get('/admin/', follow_redirects=False)
        assert response.status_code == 302
        assert 'login' in response.location.lower()
    
    def test_admin_usuario_normal_denegado(self, client, app):
        """Usuario normal no puede acceder a admin."""
        with client.session_transaction() as sess:
            sess['user_email'] = 'usuario@normal.com'
            sess['user_name'] = 'Usuario Normal'
        
        response = client.get('/admin/')
        # Debe ser denegado (403 o redirect)
        assert response.status_code in [302, 403]
    
    def test_admin_eliminar_requiere_post(self, client, app):
        """Eliminación requiere POST, GET debe fallar."""
        with app.app_context():
            # Crear artículo de prueba
            art = Articulo(
                titulo='Test Delete',
                slug='test-delete',
                categoria='Test',
                tags='test',
                nombre_archivo='test.html'
            )
            db.session.add(art)
            db.session.commit()
            art_id = art.id
        
        # Simular sesión de admin
        with client.session_transaction() as sess:
            sess['user_email'] = app.config.get('ADMIN_EMAIL', 'admin@test.com')
            sess['user_name'] = 'Admin'
        
        # GET debe fallar (405 Method Not Allowed)
        response = client.get(f'/admin/eliminar/{art_id}')
        assert response.status_code == 405
    
    def test_admin_eliminar_con_post_funciona(self, client, app):
        """Eliminación con POST debe funcionar para admin."""
        with app.app_context():
            art = Articulo(
                titulo='Test Post Delete',
                slug='test-post-delete',
                categoria='Test',
                tags='test',
                nombre_archivo='test.html'
            )
            db.session.add(art)
            db.session.commit()
            art_id = art.id
        
        with client.session_transaction() as sess:
            sess['user_email'] = app.config.get('ADMIN_EMAIL', 'admin@test.com')
            sess['user_name'] = 'Admin'
        
        response = client.post(f'/admin/eliminar/{art_id}', follow_redirects=False)
        # Debe redirigir al admin con mensaje
        assert response.status_code == 302
        
        # Verificar soft delete
        with app.app_context():
            # REMEDIACIÓN: Usar db.session.get() en lugar de Query.get() deprecado
            art = db.session.get(Articulo, art_id)
            assert art is not None  # No eliminado físicamente
            assert art.deleted_at is not None  # Pero marcado como eliminado
    
    def test_admin_restaurar_requiere_post(self, client, app):
        """Restauración requiere POST."""
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
            art.soft_delete()
            art_id = art.id
        
        with client.session_transaction() as sess:
            sess['user_email'] = app.config.get('ADMIN_EMAIL', 'admin@test.com')
            sess['user_name'] = 'Admin'
        
        # GET debe fallar
        response = client.get(f'/admin/restaurar/{art_id}')
        assert response.status_code == 405


class TestLogPagination:
    """Tests para paginación de logs en admin"""
    
    def test_logs_paginados_en_admin(self, client, app):
        """Logs deben estar paginados en el dashboard."""
        with app.app_context():
            # Crear muchos logs
            for i in range(60):
                log = LogActividad(tipo_evento='test', detalle=f'Log entry {i}')
                db.session.add(log)
            db.session.commit()
        
        with client.session_transaction() as sess:
            sess['user_email'] = app.config.get('ADMIN_EMAIL', 'admin@test.com')
            sess['user_name'] = 'Admin'
        
        # Primera página
        response = client.get('/admin/')
        assert response.status_code == 200
        
        # Segunda página
        response = client.get('/admin/?log_page=2')
        assert response.status_code == 200


class TestArticleValidation:
    """Tests de validación de artículos"""
    
    def test_create_article_titulo_largo_falla(self, client, app):
        """Título muy largo debe ser rechazado."""
        with client.session_transaction() as sess:
            sess['user_email'] = app.config.get('ADMIN_EMAIL', 'admin@test.com')
            sess['user_name'] = 'Admin'
        
        # Título de 250 caracteres (límite es 200)
        long_title = 'A' * 250
        
        response = client.post('/admin/', data={
            'titulo': long_title,
            'slug': 'test-slug',
            'categoria': 'Test',
            'tags': 'test',
        }, follow_redirects=True)
        
        # Debe mostrar error de validación sobre límite de caracteres
        assert response.status_code == 200
        assert b'200 caracteres' in response.data or b'Error' in response.data
