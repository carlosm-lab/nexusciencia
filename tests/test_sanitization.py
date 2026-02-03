"""
Tests para funciones de sanitización HTML
"""

import pytest
from app.utils.sanitizers import limpiar_html_google


def test_elimina_scripts():
    """Debe eliminar completamente tags script"""
    html = '<p>Hello</p><script>alert("XSS")</script><p>World</p>'
    result = limpiar_html_google(html)
    assert '<script>' not in result
    assert 'alert' not in result
    assert 'Hello' in result
    assert 'World' in result


def test_elimina_estilos_inline():
    """Debe eliminar estilos inline no permitidos"""
    html = '<p style="color:red; background:blue;">Text</p>'
    result = limpiar_html_google(html)
    assert 'style=' not in result
    assert 'Text' in result


def test_elimina_tags_peligrosos():
    """Debe eliminar tags potencialmente peligrosos"""
    html = '<p>Safe</p><iframe src="evil.com"></iframe><embed src="bad.swf">'
    result = limpiar_html_google(html)
    assert '<iframe' not in result
    assert '<embed' not in result
    assert 'Safe' in result


def test_permite_tags_seguros():
    """Debe permitir tags HTML seguros en la lista blanca"""
    html = '<h1>Title</h1><p><strong>Bold</strong> <em>italic</em></p><ul><li>Item</li></ul>'
    result = limpiar_html_google(html)
    assert '<h1>' in result
    assert '<strong>' in result
    assert '<em>' in result
    assert '<ul>' in result
    assert '<li>' in result


def test_añade_target_blank_enlaces():
    """Debe añadir target='_blank' a todos los enlaces"""
    html = '<a href="http://example.com">Link</a>'
    result = limpiar_html_google(html)
    assert 'target="_blank"' in result
    assert 'rel="noopener noreferrer"' in result


def test_añade_clases_imagenes():
    """Debe añadir clases responsive a imágenes"""
    html = '<img src="test.jpg" alt="Test">'
    result = limpiar_html_google(html)
    # Verificar que cada clase esté presente (el orden puede variar)
    assert 'img-fluid' in result
    assert 'rounded' in result
    assert 'my-3' in result
    assert 'loading="lazy"' in result  # Lazy loading añadido


def test_limpia_html_vacio():
    """Debe manejar HTML vacío sin errores"""
    result = limpiar_html_google('')
    assert result == ''


def test_limpia_solo_texto():
    """Debe preservar texto plano"""
    html = 'Just plain text without tags'
    result = limpiar_html_google(html)
    assert 'Just plain text without tags' in result
