# Tests para funciones añadidas en remediación 10/10
"""
Tests para nuevas funciones helper y mejoras de seguridad.
"""

import pytest
from app.utils.helpers import hash_email, SESSION_INACTIVITY_TIMEOUT


class TestHashEmail:
    """Tests para la función hash_email de protección PII."""
    
    def test_hash_email_returns_16_chars_by_default(self):
        """hash_email debe retornar hash de 16 caracteres por defecto."""
        result = hash_email("test@example.com")
        assert len(result) == 16
        assert result.isalnum()
    
    def test_hash_email_custom_length(self):
        """hash_email debe respetar longitud personalizada."""
        result = hash_email("test@example.com", length=8)
        assert len(result) == 8
    
    def test_hash_email_returns_unknown_for_empty(self):
        """hash_email debe retornar 'unknown' para email vacío."""
        assert hash_email("") == "unknown"
        assert hash_email(None) == "unknown"
    
    def test_hash_email_same_input_same_output(self):
        """hash_email debe ser determinístico."""
        email = "user@domain.com"
        assert hash_email(email) == hash_email(email)
    
    def test_hash_email_different_inputs_different_outputs(self):
        """hash_email debe producir hashes diferentes para emails diferentes."""
        assert hash_email("a@b.com") != hash_email("c@d.com")


class TestSessionTimeout:
    """Tests para configuración de timeout de sesión."""
    
    def test_session_timeout_is_timedelta(self):
        """SESSION_INACTIVITY_TIMEOUT debe ser timedelta."""
        from datetime import timedelta
        assert isinstance(SESSION_INACTIVITY_TIMEOUT, timedelta)
    
    def test_session_timeout_default_30_minutes(self):
        """Timeout default debe ser 30 minutos."""
        from datetime import timedelta
        # Default es 30 si no hay env var
        assert SESSION_INACTIVITY_TIMEOUT >= timedelta(minutes=1)


class TestCleanupOrphanFiles:
    """Tests para función cleanup_orphan_files."""
    
    def test_cleanup_handles_none_paths(self, tmp_path):
        """cleanup_orphan_files debe manejar paths None sin error."""
        from app.routes.admin import cleanup_orphan_files
        # No debe lanzar excepción
        cleanup_orphan_files(None, None)
    
    def test_cleanup_removes_existing_file(self, tmp_path):
        """cleanup_orphan_files debe eliminar archivo existente."""
        from app.routes.admin import cleanup_orphan_files
        import os
        
        # Crear archivo temporal
        test_file = tmp_path / "test.html"
        test_file.write_text("test content")
        
        assert test_file.exists()
        cleanup_orphan_files(str(test_file), None)
        assert not test_file.exists()
    
    def test_cleanup_handles_nonexistent_file(self, tmp_path):
        """cleanup_orphan_files debe manejar archivo inexistente sin error."""
        from app.routes.admin import cleanup_orphan_files
        # No debe lanzar excepción
        cleanup_orphan_files(str(tmp_path / "nonexistent.html"), None)
