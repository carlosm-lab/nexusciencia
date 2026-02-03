"""
Tests para nuevas funcionalidades de remediación.

Cubre:
- AUTH-001: Session timeout por inactividad
- VAL-001: Validación de magic bytes
"""

import pytest
from datetime import datetime, timezone, timedelta
from io import BytesIO

from app.utils.helpers import (
    check_session_timeout,
    validate_file_magic_bytes,
    SESSION_INACTIVITY_TIMEOUT
)


class TestSessionTimeout:
    """Tests para timeout de sesión por inactividad."""
    
    def test_session_timeout_no_session(self, app):
        """No debe hacer nada si no hay sesión activa."""
        with app.test_request_context():
            from flask import session
            # No hay sesión, no debe fallar
            check_session_timeout()
            assert 'user_email' not in session
    
    def test_session_updates_last_activity(self, app):
        """Debe actualizar last_activity en cada request."""
        with app.test_request_context():
            from flask import session
            session['user_email'] = 'test@example.com'
            
            check_session_timeout()
            
            assert 'last_activity' in session
    
    def test_session_expires_after_inactivity(self, app):
        """Debe expirar sesión después del timeout."""
        with app.test_request_context():
            from flask import session
            session['user_email'] = 'test@example.com'
            
            # Simular actividad antigua
            old_time = datetime.now(timezone.utc) - SESSION_INACTIVITY_TIMEOUT - timedelta(minutes=1)
            session['last_activity'] = old_time.isoformat()
            
            check_session_timeout()
            
            # Sesión debe haber sido limpiada
            assert 'user_email' not in session


class TestMagicBytesValidation:
    """Tests para validación de magic bytes en uploads."""
    
    def test_html_valid_doctype(self):
        """Debe aceptar HTML con DOCTYPE."""
        content = b'<!DOCTYPE html><html><body>Test</body></html>'
        assert validate_file_magic_bytes(content, 'html') is True
    
    def test_html_valid_lowercase(self):
        """Debe aceptar HTML con tags en minúsculas."""
        content = b'<html><head></head><body>Test</body></html>'
        assert validate_file_magic_bytes(content, 'html') is True
    
    def test_html_valid_with_bom(self):
        """Debe aceptar HTML con BOM UTF-8."""
        content = b'\xef\xbb\xbf<!DOCTYPE html><html></html>'
        assert validate_file_magic_bytes(content, 'html') is True
    
    def test_html_valid_with_comment(self):
        """Debe aceptar HTML que comienza con comentario."""
        content = b'<!-- Comment --><html></html>'
        assert validate_file_magic_bytes(content, 'html') is True
    
    def test_html_invalid_binary(self):
        """Debe rechazar archivos binarios con extensión HTML."""
        content = b'\x00\x01\x02\x03\x04\x05'
        assert validate_file_magic_bytes(content, 'html') is False
    
    def test_css_valid(self):
        """Debe aceptar CSS válido."""
        content = b'body { color: red; }'
        assert validate_file_magic_bytes(content, 'css') is True
    
    def test_css_with_media_query(self):
        """Debe aceptar CSS con media queries."""
        content = b'@media screen { body { color: red; } }'
        assert validate_file_magic_bytes(content, 'css') is True
    
    def test_css_rejects_html(self):
        """Debe rechazar HTML disfrazado de CSS."""
        content = b'<html><head><style>body{}</style></head></html>'
        assert validate_file_magic_bytes(content, 'css') is False
    
    def test_empty_file_invalid(self):
        """Debe rechazar archivos vacíos."""
        assert validate_file_magic_bytes(b'', 'html') is False
        assert validate_file_magic_bytes(b'', 'css') is False
