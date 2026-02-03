"""
Blueprint de páginas estáticas: about, legal, privacy, contact, etc.
"""

from flask import Blueprint, render_template, abort

# Blueprint
pages_bp = Blueprint('pages', __name__, url_prefix='/info')


@pages_bp.route('/<pagina>')
def pagina_estatica(pagina):
    """Renderizador genérico para páginas estáticas (About, Legal, etc)."""
    templates_permitidos = {
        'nosotros': 'about.html',
        'filosofia': 'philosophy.html',
        'politica': 'privacy.html',
        'contacto': 'contact.html',
        'legal': 'legal.html',
        'solicitar': 'request.html',
        'editorial': 'editorial.html'  # SEO E-E-A-T: Política editorial
    }
    
    if pagina not in templates_permitidos:
        abort(404)
    
    titulos = {
        'legal': 'Aviso Legal',
        'politica': 'Política de Privacidad',
        'filosofia': 'Nuestra Filosofía',
        'nosotros': 'Sobre Nosotros',
        'contacto': 'Contacto',
        'solicitar': 'Solicitar Artículo',
        'editorial': 'Política Editorial'  # SEO E-E-A-T
    }
    
    return render_template(
        templates_permitidos[pagina],
        titulo=titulos.get(pagina, 'Información'),
        tipo=pagina
    )
