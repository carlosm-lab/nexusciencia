"""
Tests de API para endpoints AJAX de NexusCiencia
"""
import pytest
from app.extensions import db
from app.models.usuario import Usuario
from app.models.articulo import Articulo


def test_api_toggle_biblioteca_sin_auth(client):
    """Test: API de biblioteca debe rechazar requests sin autenticación."""
    response = client.post('/api/toggle_biblioteca/1')
    assert response.status_code == 403
    data = response.get_json()
    assert data['status'] == 'error'


def test_api_vaciar_biblioteca_sin_auth(client):
    """Test: API de vaciar biblioteca debe rechazar sin autenticación."""
    response = client.post('/api/vaciar_biblioteca')
    assert response.status_code == 403


def test_api_toggle_biblioteca_articulo_inexistente(client, app):
    """Test: API debe retornar 404 para artículo inexistente."""
    with client.session_transaction() as sess:
        sess['user_email'] = 'test@example.com'
        sess['user_name'] = 'Test User'
    
    with app.app_context():
        # Crear usuario de prueba
        test_user = Usuario(email='test@example.com', nombre='Test User')
        db.session.add(test_user)
        db.session.commit()
    
    response = client.post('/api/toggle_biblioteca/99999')
    assert response.status_code == 404


def test_api_toggle_biblioteca_exito(client, app):
    """Test: API debe añadir/remover artículo de biblioteca correctamente."""
    with app.app_context():
        # Crear usuario y artículo de prueba
        test_user = Usuario(email='toggle-test@example.com', nombre='Toggle Test')
        test_article = Articulo(
            titulo='Test Toggle',
            slug='test-toggle-biblioteca',
            categoria='Test',
            tags='test',
            nombre_archivo='test.html'
        )
        db.session.add(test_user)
        db.session.add(test_article)
        db.session.commit()
        art_id = test_article.id
    
    with client.session_transaction() as sess:
        sess['user_email'] = 'toggle-test@example.com'
        sess['user_name'] = 'Toggle Test'
    
    # Añadir a biblioteca
    response = client.post(f'/api/toggle_biblioteca/{art_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert data['action'] == 'added'
    
    # Remover de biblioteca
    response = client.post(f'/api/toggle_biblioteca/{art_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert data['action'] == 'removed'


def test_api_vaciar_biblioteca_exito(client, app):
    """Test: API debe vaciar biblioteca correctamente."""
    with app.app_context():
        test_user = Usuario(email='vaciar-test@example.com', nombre='Vaciar Test')
        db.session.add(test_user)
        db.session.commit()
    
    with client.session_transaction() as sess:
        sess['user_email'] = 'vaciar-test@example.com'
        sess['user_name'] = 'Vaciar Test'
    
    response = client.post('/api/vaciar_biblioteca')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'


def test_api_health_check(client):
    """Test: Health endpoint debe responder OK."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'


class TestRateLimiting:
    """Tests para verificar rate limiting cuando está habilitado"""
    
    def test_rate_limit_disabled_in_testing(self, client, app):
        """Rate limiting debe estar deshabilitado en tests por defecto."""
        # Verificar configuración
        assert app.config.get('RATELIMIT_ENABLED') == False
        
        # Hacer múltiples requests
        for _ in range(10):
            response = client.post('/api/toggle_biblioteca/1')
            # Sin rate limiting, debe ser 403 (no auth) no 429
            assert response.status_code != 429

