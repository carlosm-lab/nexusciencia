"""
Tests para funciones de validación
"""

import pytest
from app.utils.validators import (
    validar_url_segura, 
    validar_longitud, 
    validar_categoria_nombre,
    validar_slug
)


class TestValidarUrlSegura:
    """Tests para validación de URLs"""
    
    def test_valida_http_https(self):
        """Debe aceptar URLs HTTP y HTTPS"""
        assert validar_url_segura('http://example.com') == True
        assert validar_url_segura('https://example.com') == True
        assert validar_url_segura('https://www.example.com/path?query=1') == True
    
    def test_rechaza_javascript(self):
        """Debe rechazar javascript: URLs (XSS)"""
        assert validar_url_segura('javascript:alert(1)') == False
        assert validar_url_segura('javascript:void(0)') == False
    
    def test_rechaza_data_urls(self):
        """Debe rechazar data: URLs"""
        assert validar_url_segura('data:text/html,<script>alert(1)</script>') == False
    
    def test_rechaza_file_urls(self):
        """Debe rechazar file:// URLs"""
        assert validar_url_segura('file:///etc/passwd') == False
    
    def test_permite_urls_vacias(self):
        """Debe permitir URLs vacías (opcional)"""
        assert validar_url_segura('') == True
        assert validar_url_segura(None) == True
    
    def test_maneja_urls_malformadas(self):
        """Debe manejar URLs malformadas sin crash - parsed as relative paths"""
        # Note: urlparse treats malformed URLs as relative paths (empty scheme)
        # which are valid. We test that the function doesn't crash.
        result = validar_url_segura('ht!tp://bad url')
        assert result == True  # Parsed as relative path, not as dangerous scheme


class TestValidarLongitud:
    """Tests para validación de longitud"""
    
    def test_valida_longitud_exacta(self):
        """Debe validar longitud exacta al límite"""
        assert validar_longitud('a' * 200, 200) == True
        assert validar_longitud('a' * 201, 200) == False
    
    def test_permite_texto_vacio(self):
        """Debe permitir texto vacío"""
        assert validar_longitud('', 100) == True
        assert validar_longitud(None, 100) == True
    
    def test_valida_con_espacios(self):
        """Debe contar después de strip()"""
        assert validar_longitud('   test   ', 10) == True


class TestValidarCategoriaNombre:
    """Tests para validación de categorías (requiere app context)"""
    
    def test_permite_categoria_vacia(self, app):
        """Debe permitir categoría vacía (opcional)"""
        with app.app_context():
            assert validar_categoria_nombre('') == True
            assert validar_categoria_nombre(None) == True
    
    # Nota: Tests adicionales requieren setup de categorías en BD
    # Se implementarán después de migración de categorías dinámicas


class TestValidarSlug:
    """Tests para validación de slugs (prevención de path traversal)"""
    
    def test_acepta_slugs_validos(self):
        """Debe aceptar slugs con formato correcto"""
        assert validar_slug('mi-articulo') == True
        assert validar_slug('articulo-2024') == True
        assert validar_slug('neurociencia-101') == True
        assert validar_slug('articulo-de-psicologia-clinica') == True
        assert validar_slug('abc') == True  # Mínimo 3 caracteres
    
    def test_rechaza_path_traversal(self):
        """Debe rechazar intentos de path traversal"""
        assert validar_slug('../etc/passwd') == False
        assert validar_slug('..\\windows\\system32') == False
        assert validar_slug('../../secret') == False
        assert validar_slug('.htaccess') == False
    
    def test_rechaza_caracteres_especiales(self):
        """Debe rechazar caracteres especiales peligrosos"""
        assert validar_slug('articulo.html') == False  # Puntos
        assert validar_slug('articulo/test') == False  # Barras
        assert validar_slug('articulo\\test') == False  # Backslash
        assert validar_slug('articulo test') == False  # Espacios
        assert validar_slug('articulo@test') == False  # @
        assert validar_slug('articulo#test') == False  # #
    
    def test_rechaza_slugs_vacios_o_cortos(self):
        """Debe rechazar slugs vacíos o muy cortos"""
        assert validar_slug('') == False
        assert validar_slug(None) == False
        assert validar_slug('ab') == False  # Menos de 3 caracteres
        assert validar_slug('  ') == False  # Solo espacios
    
    def test_rechaza_slugs_muy_largos(self):
        """Debe rechazar slugs que excedan 200 caracteres"""
        assert validar_slug('a' * 200) == True  # Exactamente 200
        assert validar_slug('a' * 201) == False  # Excede límite
    
    def test_rechaza_mayusculas(self):
        """Debe rechazar slugs con mayúsculas (seguridad: no normalizar silenciosamente)"""
        # REMEDIACIÓN AUD-011: Los slugs deben ser estrictamente minúsculas
        assert validar_slug('Mi-Articulo') == False
        assert validar_slug('ARTICULO-GRANDE') == False

