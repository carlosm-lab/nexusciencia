"""
Tests para endpoints de diagnósticos del sistema.
Verifica que todos requieren autenticación de administrador.
"""

import pytest
from flask import url_for


class TestDiagnosticsAuth:
    """Tests de autenticación para endpoints de diagnósticos."""
    
    def test_run_all_requires_admin(self, client):
        """Endpoint run-all debe requerir autenticación admin."""
        response = client.post('/api/diagnostics/run-all')
        # Sin auth debe redirigir a login o dar 403
        assert response.status_code in [302, 403]
    
    def test_database_check_requires_admin(self, client):
        """Endpoint database debe requerir autenticación admin."""
        response = client.post('/api/diagnostics/database')
        assert response.status_code in [302, 403]
    
    def test_config_check_requires_admin(self, client):
        """Endpoint config debe requerir autenticación admin."""
        response = client.post('/api/diagnostics/config')
        assert response.status_code in [302, 403]
    
    def test_security_check_requires_admin(self, client):
        """Endpoint security debe requerir autenticación admin."""
        response = client.post('/api/diagnostics/security')
        assert response.status_code in [302, 403]


class TestDiagnosticsWithAdmin:
    """Tests de funcionalidad con usuario admin autenticado."""
    
    def test_run_all_returns_json(self, admin_session, app):
        """run-all debe retornar JSON con resultados de checks."""
        with app.app_context():
            response = admin_session.post('/api/diagnostics/run-all')
            assert response.status_code == 200
            data = response.get_json()
            assert 'summary' in data
            assert 'checks' in data
            assert 'timestamp' in data
            assert data['summary']['total'] >= 1
    
    def test_database_check_returns_status(self, admin_session, app):
        """database check debe retornar estado de conexión."""
        with app.app_context():
            response = admin_session.post('/api/diagnostics/database')
            assert response.status_code == 200
            data = response.get_json()
            assert 'name' in data
            assert 'status' in data
            assert data['name'] == 'Base de Datos'
    
    def test_config_check_returns_status(self, admin_session, app):
        """config check debe retornar estado de configuración."""
        with app.app_context():
            response = admin_session.post('/api/diagnostics/config')
            assert response.status_code == 200
            data = response.get_json()
            assert 'name' in data
            assert data['name'] == 'Configuración'
    
    def test_health_score_calculation(self, admin_session, app):
        """Health score debe calcularse correctamente."""
        with app.app_context():
            response = admin_session.post('/api/diagnostics/run-all')
            data = response.get_json()
            summary = data['summary']
            
            # Verificar cálculo: (passed / total) * 100
            expected_score = round((summary['passed'] / summary['total']) * 100, 1)
            assert summary['health_score'] == expected_score
