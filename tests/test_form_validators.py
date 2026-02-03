"""
Tests para validadores de formularios centralizados
"""

import pytest
from app.utils.form_validators import (
    validar_formulario_articulo,
    validar_archivo_upload,
    obtener_categorias_validas
)


class TestValidarFormularioArticulo:
    """Tests para validación de formularios de artículo"""
    
    def test_campos_obligatorios_vacios(self):
        """Debe rechazar formulario sin título ni slug"""
        form_data = {
            'titulo': '',
            'slug': '',
            'categoria': '',
            'tags': '',
            'url_pdf': '',
            'url_audio': ''
        }
        errores = validar_formulario_articulo(form_data)
        assert len(errores) >= 2  # Al menos título y slug obligatorios
        assert any('título' in e.lower() for e in errores)
        assert any('slug' in e.lower() for e in errores)
    
    def test_titulo_muy_largo(self):
        """Debe rechazar título que excede límite"""
        form_data = {
            'titulo': 'A' * 250,  # Más de 200 caracteres
            'slug': 'slug-valido',
            'categoria': '',
            'tags': '',
            'url_pdf': '',
            'url_audio': ''
        }
        errores = validar_formulario_articulo(form_data)
        assert any('200 caracteres' in e for e in errores)
    
    def test_slug_con_path_traversal(self):
        """Debe rechazar slug con path traversal"""
        form_data = {
            'titulo': 'Artículo de prueba',
            'slug': '../etc/passwd',
            'categoria': '',
            'tags': '',
            'url_pdf': '',
            'url_audio': ''
        }
        errores = validar_formulario_articulo(form_data)
        assert any('slug' in e.lower() for e in errores)
    
    def test_slug_valido(self):
        """Debe aceptar formulario con datos válidos"""
        form_data = {
            'titulo': 'Artículo de prueba',
            'slug': 'articulo-de-prueba',
            'categoria': '',
            'tags': 'test, prueba',
            'url_pdf': 'https://example.com/doc.pdf',
            'url_audio': ''
        }
        errores = validar_formulario_articulo(form_data)
        # Sin errores para datos básicos válidos
        assert not any('título' in e.lower() for e in errores)
        assert not any('slug inválido' in e.lower() for e in errores)
    
    def test_url_javascript_rechazada(self):
        """Debe rechazar URLs con javascript:"""
        form_data = {
            'titulo': 'Test',
            'slug': 'test-slug',
            'categoria': '',
            'tags': '',
            'url_pdf': 'javascript:alert(1)',
            'url_audio': ''
        }
        errores = validar_formulario_articulo(form_data)
        assert any('url' in e.lower() for e in errores)
    
    def test_url_https_aceptada(self):
        """Debe aceptar URLs HTTPS válidas"""
        form_data = {
            'titulo': 'Test',
            'slug': 'test-slug',
            'categoria': '',
            'tags': '',
            'url_pdf': 'https://example.com/document.pdf',
            'url_audio': 'https://example.com/audio.mp3'
        }
        errores = validar_formulario_articulo(form_data)
        assert not any('url' in e.lower() for e in errores)


class TestValidarArchivoUpload:
    """Tests para validación de archivos"""
    
    def test_archivo_html_requerido_faltante(self):
        """Debe rechazar si archivo HTML requerido falta"""
        es_valido, error = validar_archivo_upload(None, 'html', requerido=True)
        assert es_valido == False
        assert 'HTML' in error
    
    def test_archivo_css_opcional_faltante(self):
        """Debe aceptar si archivo CSS opcional falta"""
        es_valido, error = validar_archivo_upload(None, 'css', requerido=False)
        assert es_valido == True
        assert error == ""


class TestObtenerCategoriasValidas:
    """Tests para obtención de categorías"""
    
    def test_retorna_lista(self, app):
        """Debe retornar una lista de categorías"""
        with app.app_context():
            categorias = obtener_categorias_validas()
            assert isinstance(categorias, list)
            assert len(categorias) > 0
    
    def test_categorias_son_strings(self, app):
        """Todas las categorías deben ser strings"""
        with app.app_context():
            categorias = obtener_categorias_validas()
            assert all(isinstance(c, str) for c in categorias)
