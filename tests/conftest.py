# Configuración de pytest para NexusCiencia
"""
Test Configuration - Usando Factory Pattern
"""
import pytest
import sys
import os

# Añadir directorio raíz al PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Mantener una referencia global al app para evitar conflictos de webassets
_test_app = None


def get_test_app():
    """Obtiene o crea la aplicación de test."""
    global _test_app
    
    if _test_app is None:
        from app import create_app
        _test_app = create_app()
        _test_app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'RATELIMIT_ENABLED': False,
        })
    
    return _test_app


@pytest.fixture
def app():
    """Fixture que proporciona la aplicación Flask configurada para testing."""
    from app.extensions import db
    
    test_app = get_test_app()
    
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Fixture que proporciona un cliente de test."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Fixture que proporciona un runner CLI."""
    return app.test_cli_runner()


@pytest.fixture
def admin_session(client, app):
    """Fixture que simula sesión de administrador."""
    with client.session_transaction() as sess:
        sess['user_email'] = app.config.get('ADMIN_EMAIL', 'admin@test.com')
        sess['user_name'] = 'Admin Test'
    return client
