"""
Blueprint SEO: Sitemap, robots.txt y archivos de rastreo
Auditoría 1.2: Generación dinámica de sitemap.xml
"""

from flask import Blueprint, Response, url_for, current_app
from datetime import datetime, timezone

from app.models.articulo import Articulo
from app.constants import LISTA_CATEGORIAS, get_category_slug

# Blueprint
seo_bp = Blueprint('seo', __name__)


@seo_bp.route('/sitemap.xml')
def sitemap():
    """
    Genera sitemap XML dinámico para motores de búsqueda.
    
    Incluye:
    - Páginas estáticas (inicio, categorías, about, etc.)
    - Todas las categorías individuales
    - Todos los artículos activos
    
    SEO Impact: Mejora rastreabilidad e indexación de contenido.
    """
    base_url = current_app.config.get('SITE_URL', 'https://www.nexusciencia.com')
    
    # Construir lista de URLs
    urls = []
    
    # 1. Páginas estáticas principales
    static_pages = [
        {'loc': '/', 'priority': '1.0', 'changefreq': 'daily'},
        {'loc': '/categorias', 'priority': '0.9', 'changefreq': 'daily'},
        {'loc': '/info/nosotros', 'priority': '0.5', 'changefreq': 'monthly'},
        {'loc': '/info/filosofia', 'priority': '0.4', 'changefreq': 'monthly'},
        {'loc': '/info/editorial', 'priority': '0.5', 'changefreq': 'monthly'},  # E-E-A-T
        {'loc': '/info/politica', 'priority': '0.3', 'changefreq': 'yearly'},
        {'loc': '/info/contacto', 'priority': '0.5', 'changefreq': 'monthly'},
        {'loc': '/info/legal', 'priority': '0.3', 'changefreq': 'yearly'},
        {'loc': '/info/solicitar', 'priority': '0.6', 'changefreq': 'monthly'},
    ]
    
    for page in static_pages:
        urls.append({
            'loc': base_url.rstrip('/') + page['loc'],
            'lastmod': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            'changefreq': page['changefreq'],
            'priority': page['priority']
        })
    
    # 2. Páginas de categorías
    for cat in LISTA_CATEGORIAS:
        slug = get_category_slug(cat)
        urls.append({
            'loc': f"{base_url.rstrip('/')}/categoria/{slug}",
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'weekly',
            'priority': '0.8'
        })
    
    # 3. Artículos individuales
    articulos = Articulo.get_active().all()
    for art in articulos:
        cat_slug = get_category_slug(art.categoria)
        urls.append({
            'loc': f"{base_url.rstrip('/')}/categoria/{cat_slug}/{art.slug}",
            'lastmod': art.fecha.strftime('%Y-%m-%d') if art.fecha else datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'monthly',
            'priority': '0.7'
        })
    
    # Generar XML
    xml_content = generate_sitemap_xml(urls)
    
    return Response(xml_content, mimetype='application/xml')


def generate_sitemap_xml(urls: list) -> str:
    """Genera contenido XML del sitemap."""
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for url in urls:
        xml += '  <url>\n'
        xml += f'    <loc>{url["loc"]}</loc>\n'
        if url.get('lastmod'):
            xml += f'    <lastmod>{url["lastmod"]}</lastmod>\n'
        if url.get('changefreq'):
            xml += f'    <changefreq>{url["changefreq"]}</changefreq>\n'
        if url.get('priority'):
            xml += f'    <priority>{url["priority"]}</priority>\n'
        xml += '  </url>\n'
    
    xml += '</urlset>'
    return xml


@seo_bp.route('/robots.txt')
def robots():
    """
    Genera robots.txt dinámico mejorado.
    
    Auditoría 1.3: Corrección de rutas faltantes en robots.txt
    """
    base_url = current_app.config.get('SITE_URL', 'https://www.nexusciencia.com')
    
    content = f"""User-agent: *
Allow: /
Disallow: /admin
Disallow: /api/
Disallow: /login
Disallow: /logout
Disallow: /perfil
Disallow: /callback

# Archivos estáticos internos
Disallow: /static/css/
Disallow: /static/js/
Disallow: /static/gen/

# Sitemap
Sitemap: {base_url.rstrip('/')}/sitemap.xml

# Host preferido
Host: {base_url.rstrip('/')}
"""
    
    return Response(content, mimetype='text/plain')
