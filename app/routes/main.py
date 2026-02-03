"""
Blueprint de rutas principales: inicio, artículos, páginas estáticas
"""

import os
import logging
from flask import Blueprint, render_template, request, session, abort, Response
from bs4 import BeautifulSoup
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db, limiter
from app.config import BASE_DIR, Config
from app.models.articulo import Articulo
from app.models.usuario import Usuario
from app.models.log import LogActividad
from app.enums import LogEventType
from app.utils.helpers import get_rate_limit_key
from app.constants import LISTA_CATEGORIAS, READING_SPEED_WPM

# Blueprint
main_bp = Blueprint('main', __name__)

# Usar directorio base centralizado de config.py
carpeta_base = BASE_DIR

logger = logging.getLogger(__name__)


@main_bp.route('/')
@limiter.limit("30 per minute", key_func=get_rate_limit_key)
def inicio() -> str:
    """
    Página principal (Content Hub) SEO-optimizada.
    
    Muestra 6 categorías destacadas curadas en Bento Grid,
    estadísticas y últimos artículos para SEO y conversión.
    """
    # Categorías destacadas CURADAS para el Bento Grid (solo 6)
    # Cada una con descripción SEO de 2 líneas y slug real
    categorias_destacadas = [
        {
            "nombre": "Estrés y Ansiedad",
            "emoji": "🧠",
            "slug": "psi-del-estres-y-la-ansiedad",
            "descripcion": "Investigación sobre trastornos de ansiedad, estrés crónico, y estrategias de afrontamiento basadas en evidencia científica."
        },
        {
            "nombre": "Neurociencia Conductual",
            "emoji": "🧬",
            "slug": "psi-y-neurociencia-del-comportamiento",
            "descripcion": "Estudios sobre bases neurológicas del comportamiento, plasticidad cerebral y neuropsicología aplicada."
        },
        {
            "nombre": "Psicología Social",
            "emoji": "👥",
            "slug": "psi-social-y-del-comportamiento",
            "descripcion": "Análisis de la influencia social, dinámicas grupales y comportamiento colectivo en contextos diversos."
        },
        {
            "nombre": "Psicología Clínica",
            "emoji": "💊",
            "slug": "psi-clinica-y-salud-mental",
            "descripcion": "Evaluación, diagnóstico y tratamiento de trastornos mentales con enfoques terapéuticos validados."
        },
        {
            "nombre": "Psicología Criminal",
            "emoji": "⚖️",
            "slug": "fundamentos-de-la-psi-criminal",
            "descripcion": "Perfilación criminal, psicología forense y análisis del comportamiento antisocial y delictivo."
        },
        {
            "nombre": "Desarrollo y Educación",
            "emoji": "📚",
            "slug": "psi-del-desarrollo-y-edu-sexual",
            "descripcion": "Psicología del desarrollo humano, aprendizaje y estrategias educativas basadas en ciencia."
        },
    ]
    
    # Estadísticas para hero section
    total_categorias = len(LISTA_CATEGORIAS)
    total_articulos = Articulo.get_active().count()
    
    # Últimos 6 artículos publicados (para grid de 3 columnas)
    ultimos_articulos = Articulo.get_active().order_by(
        Articulo.fecha.desc()
    ).limit(6).all()
    
    return render_template('index.html',
                           categorias_destacadas=categorias_destacadas,
                           total_categorias=total_categorias,
                           total_articulos=total_articulos,
                           ultimos_articulos=ultimos_articulos)


@main_bp.route('/categoria/<cat_slug>/<slug>')
def ver_articulo(cat_slug: str, slug: str) -> str:
    """
    Vista de lectura de un artículo específico.
    
    Nueva estructura SEO: /categoria/{cat_slug}/{art_slug}
    """
    from app.constants import CATEGORIAS_SLUGS, get_category_slug
    
    # Validar que la categoría existe
    categoria_completa = CATEGORIAS_SLUGS.get(cat_slug)
    if not categoria_completa:
        abort(404)
    
    articulo = Articulo.get_active().filter_by(slug=slug).first_or_404()
    
    # Verificar que el artículo pertenece a esta categoría
    # Si no coincide, redirigir a la URL correcta
    articulo_cat_slug = get_category_slug(articulo.categoria)
    if articulo_cat_slug != cat_slug:
        from flask import redirect, url_for
        return redirect(url_for('main.ver_articulo', cat_slug=articulo_cat_slug, slug=slug), code=301)
    
    # Cargar contenido HTML desde archivo físico
    ruta_html = os.path.join(carpeta_base, 'templates', 'articulos', articulo.nombre_archivo)
    contenido_html = ""
    tiempo_lectura = Config.DEFAULT_READING_TIME
    
    if os.path.exists(ruta_html):
        with open(ruta_html, 'r', encoding='utf-8') as f:
            contenido_html = f.read()
        
        # Calcular tiempo de lectura estimado
        try:
            # REMEDIACIÓN: READING_SPEED_WPM importado al inicio del archivo
            soup = BeautifulSoup(contenido_html, 'html.parser')
            texto_plano = soup.get_text(separator=' ')
            palabras = len(texto_plano.split())
            tiempo_lectura = max(1, round(palabras / READING_SPEED_WPM))
        except (AttributeError, TypeError, ZeroDivisionError) as e:
            # REMEDIACIÓN DT-003: Excepciones específicas en lugar de genérica
            logger.debug(f"Error calculando tiempo de lectura: {e.__class__.__name__}")
            tiempo_lectura = Config.DEFAULT_READING_TIME
    else:
        contenido_html = "<p><em>Error: El archivo de contenido no se encuentra en el servidor.</em></p>"
    
    # Registrar visita (Analytics interno)
    try:
        nuevo_log = LogActividad(tipo_evento=LogEventType.LECTURA, detalle=f"Leído: {slug}")
        db.session.add(nuevo_log)
        db.session.commit()
    except SQLAlchemyError as e:
        logger.error(f"Error de BD en analytics: {e.__class__.__name__}")
        db.session.rollback()
    
    # Verificar si existe CSS específico para este artículo
    # REMEDIACIÓN LOW-002: Cache-busting con timestamp de modificación
    ruta_css = os.path.join(carpeta_base, 'static', 'articulos_css', f"{slug}.css")
    tiene_css = os.path.exists(ruta_css)
    css_version = None
    if tiene_css:
        try:
            css_version = int(os.path.getmtime(ruta_css))
        except OSError:
            css_version = 0
    
    # Estado de guardado para el botón
    esta_guardado = False
    if 'user_email' in session:
        from app.models.biblioteca import biblioteca
        usuario = Usuario.query.filter_by(email=session['user_email']).first()
        if usuario:
            # Consulta directa a tabla intermedia en lugar de cargar lazy la relación
            from sqlalchemy import and_
            existe = db.session.query(biblioteca).filter(
                and_(
                    biblioteca.c.usuario_id == usuario.id,
                    biblioteca.c.articulo_id == articulo.id
                )
            ).first()
            esta_guardado = existe is not None
    
    return render_template('articulo_detalle.html',
                           articulo=articulo,
                           contenido_html=contenido_html,
                           tiene_css=tiene_css,
                           css_version=css_version,  # REMEDIACIÓN LOW-002
                           tiempo_lectura=tiempo_lectura,
                           esta_guardado=esta_guardado,
                           categoria_slug=cat_slug)


@main_bp.route('/categorias')
def categorias() -> str:
    """
    Hub de todas las categorías (SEO).
    
    Página principal que muestra las 50 categorías, estadísticas,
    búsqueda y últimas publicaciones con estructura SEO.
    """
    from app.constants import get_category_slug, get_category_display_name, get_category_emoji, CATEGORIAS_SLUGS
    
    busqueda = request.args.get('q')
    pagina = request.args.get('page', 1, type=int)
    per_page = Config.ARTICLES_PER_PAGE
    
    # IDs de artículos guardados por el usuario
    ids_guardados = []
    if 'user_email' in session:
        usuario = Usuario.query.options(
            selectinload(Usuario.articulos_guardados)
        ).filter_by(email=session['user_email']).first()
        if usuario:
            ids_guardados = [art.id for art in usuario.articulos_guardados]
    
    # Lógica de búsqueda y paginación
    if busqueda:
        search_pattern = f'%{busqueda}%'
        articulos_pag = Articulo.get_active().filter(
            (Articulo.titulo.ilike(search_pattern)) |
            (Articulo.categoria.ilike(search_pattern)) |
            (Articulo.tags.ilike(search_pattern))
        ).order_by(Articulo.fecha.desc()).paginate(
            page=pagina, per_page=per_page, error_out=False
        )
    else:
        articulos_pag = Articulo.get_active().order_by(
            Articulo.fecha.desc()
        ).paginate(page=pagina, per_page=per_page, error_out=False)
    
    articulos_recientes = articulos_pag.items
    total_articulos = articulos_pag.total
    total_categorias = len(LISTA_CATEGORIAS)
    
    # Diccionario de slugs para el template
    categorias_slugs = {cat: get_category_slug(cat) for cat in LISTA_CATEGORIAS}
    
    return render_template('categorias.html',
                           articulos_recientes=articulos_recientes,
                           articulos_pag=articulos_pag,
                           total_articulos=total_articulos,
                           total_categorias=total_categorias,
                           categorias_slugs=categorias_slugs,
                           ids_guardados=ids_guardados)


@main_bp.route('/categoria/<slug>')
def ver_categoria(slug: str) -> str:
    """
    Página individual de categoría (SEO).
    
    Muestra los artículos de una categoría específica con estructura SEO
    incluyendo JSON-LD CollectionPage, ItemList y breadcrumbs.
    """
    from app.constants import CATEGORIAS_SLUGS, get_category_display_name, get_category_emoji, get_category_slug
    
    # Buscar categoría por slug
    categoria = CATEGORIAS_SLUGS.get(slug)
    if not categoria:
        abort(404)
    
    pagina = request.args.get('page', 1, type=int)
    per_page = Config.ARTICLES_PER_PAGE
    
    # IDs de artículos guardados por el usuario
    ids_guardados = []
    if 'user_email' in session:
        usuario = Usuario.query.options(
            selectinload(Usuario.articulos_guardados)
        ).filter_by(email=session['user_email']).first()
        if usuario:
            ids_guardados = [art.id for art in usuario.articulos_guardados]
    
    # Obtener artículos de esta categoría con paginación
    articulos_pag = Articulo.get_active().filter(
        Articulo.categoria == categoria
    ).order_by(Articulo.fecha.desc()).paginate(
        page=pagina, per_page=per_page, error_out=False
    )
    
    # Preparar datos para JSON-LD
    articulos_json = []
    for art in articulos_pag.items:
        articulos_json.append({
            'nombre': art.titulo,
            'url': f"/categoria/{slug}/{art.slug}"
        })
    
    return render_template('categoria.html',
                           categoria=categoria,
                           categoria_nombre=get_category_display_name(categoria),
                           categoria_emoji=get_category_emoji(categoria),
                           categoria_slug=slug,
                           articulos=articulos_pag.items,
                           articulos_pag=articulos_pag,
                           articulos_json=articulos_json,
                           total_articulos=articulos_pag.total,
                           ids_guardados=ids_guardados)


@main_bp.route('/tag/<slug>')
@limiter.limit("30 per minute", key_func=get_rate_limit_key)
def ver_tag(slug: str) -> str:
    """
    Página de etiqueta individual (SEO).
    
    Muestra todos los artículos que contienen una etiqueta específica,
    con estructura SEO incluyendo JSON-LD CollectionPage.
    """
    import unicodedata
    import re
    
    # Convertir slug de vuelta a tag legible para buscar
    # El slug viene como 'neurociencia' y buscamos en tags 'neurociencia'
    tag_normalizado = slug.lower()
    
    pagina = request.args.get('page', 1, type=int)
    per_page = Config.ARTICLES_PER_PAGE
    
    # IDs de artículos guardados por el usuario
    ids_guardados = []
    if 'user_email' in session:
        usuario = Usuario.query.options(
            selectinload(Usuario.articulos_guardados)
        ).filter_by(email=session['user_email']).first()
        if usuario:
            ids_guardados = [art.id for art in usuario.articulos_guardados]
    
    # Buscar artículos que contengan este tag (case-insensitive)
    # Los tags están almacenados como "tag1, tag2, tag3"
    articulos_pag = Articulo.get_active().filter(
        Articulo.tags.ilike(f'%{tag_normalizado}%')
    ).order_by(Articulo.fecha.desc()).paginate(
        page=pagina, per_page=per_page, error_out=False
    )
    
    # Si no hay artículos con este tag, 404
    if articulos_pag.total == 0:
        abort(404)
    
    # Nombre legible del tag (capitalizado)
    tag_display = slug.replace('-', ' ').title()
    
    # Preparar datos para JSON-LD
    articulos_json = []
    from app.constants import get_category_slug
    for art in articulos_pag.items:
        cat_slug = get_category_slug(art.categoria) if art.categoria else ''
        articulos_json.append({
            'nombre': art.titulo,
            'url': f"/categoria/{cat_slug}/{art.slug}"
        })
    
    return render_template('tag.html',
                           tag_slug=slug,
                           tag_display=tag_display,
                           articulos=articulos_pag.items,
                           articulos_pag=articulos_pag,
                           articulos_json=articulos_json,
                           total_articulos=articulos_pag.total,
                           ids_guardados=ids_guardados)


# =============================================================================
# RUTAS DE SECCIONES ACADÉMICAS ESPECIALIZADAS
# =============================================================================

@main_bp.route('/fuentes')
@limiter.limit("30 per minute", key_func=get_rate_limit_key)
def repositorio_fuentes() -> str:
    """
    Repositorio de Fuentes Académicas.
    
    Papers crudos de Scopus, PubMed, ScienceDirect, etc.
    Diseño de lista compacta estilo bibliotecario.
    """
    # Datos dummy para desarrollo (reemplazar con modelo de BD)
    fuentes = [
        {
            "id": 1,
            "titulo": "Neurobiological Mechanisms of Stress-Related Disorders",
            "autor": "Chen, L., & Williams, R.",
            "año": 2023,
            "fuente": "PubMed",
            "tipo": "PDF",
            "doi": "10.1016/j.neuroscience.2023.05.012",
            "url": "#"
        },
        {
            "id": 2,
            "titulo": "Cognitive Behavioral Therapy for Anxiety: A Meta-Analysis",
            "autor": "Johnson, M., et al.",
            "año": 2024,
            "fuente": "Scopus",
            "tipo": "PDF",
            "doi": "10.1037/ccp0000821",
            "url": "#"
        },
        {
            "id": 3,
            "titulo": "The Role of Dopamine in Reward Processing",
            "autor": "García-Pérez, A.",
            "año": 2023,
            "fuente": "ScienceDirect",
            "tipo": "DOI",
            "doi": "10.1016/j.biopsych.2023.11.004",
            "url": "#"
        },
        {
            "id": 4,
            "titulo": "Attachment Styles and Adult Romantic Relationships",
            "autor": "Thompson, K., & Lee, S.",
            "año": 2022,
            "fuente": "APA PsycNet",
            "tipo": "PDF",
            "doi": "10.1037/pspi0000412",
            "url": "#"
        },
        {
            "id": 5,
            "titulo": "Neural Correlates of Mindfulness Meditation",
            "autor": "Patel, R., et al.",
            "año": 2024,
            "fuente": "PubMed",
            "tipo": "PDF",
            "doi": "10.1093/cercor/bhad298",
            "url": "#"
        },
        {
            "id": 6,
            "titulo": "Prevalence of Depression in Adolescents: Global Estimates",
            "autor": "WHO Mental Health Group",
            "año": 2023,
            "fuente": "Scopus",
            "tipo": "PDF",
            "doi": "10.1016/S2215-0366(23)00193-1",
            "url": "#"
        },
        {
            "id": 7,
            "titulo": "Trauma-Informed Care in Clinical Practice",
            "autor": "Martinez, J., & Brown, T.",
            "año": 2024,
            "fuente": "ScienceDirect",
            "tipo": "DOI",
            "doi": "10.1016/j.cpr.2024.102345",
            "url": "#"
        },
        {
            "id": 8,
            "titulo": "Executive Function Development in Early Childhood",
            "autor": "Anderson, P.",
            "año": 2023,
            "fuente": "APA PsycNet",
            "tipo": "PDF",
            "doi": "10.1037/dev0001543",
            "url": "#"
        },
    ]
    
    total_fuentes = len(fuentes)
    
    return render_template('fuentes.html',
                           fuentes=fuentes,
                           total_fuentes=total_fuentes)


@main_bp.route('/casos-clinicos')
@limiter.limit("30 per minute", key_func=get_rate_limit_key)
def casos_clinicos() -> str:
    """
    Estudios de Caso Clínicos.
    
    Casos prácticos para estudiantes de psicología.
    Diseño de expediente médico/historia clínica.
    """
    # Datos dummy para desarrollo (reemplazar con modelo de BD)
    casos = [
        {
            "id": 1,
            "numero": "01",
            "titulo": "Trastorno de Pánico con Agorafobia",
            "nivel": "Intermedio",
            "nivel_color": "amber",
            "sintomatologia": [
                "Ataques de pánico recurrentes",
                "Evitación de espacios abiertos",
                "Anticipación ansiosa constante",
                "Síntomas somáticos (palpitaciones, sudoración)"
            ],
            "edad_paciente": "28 años",
            "sexo": "Femenino",
            "slug": "caso-01-panico-agorafobia"
        },
        {
            "id": 2,
            "numero": "02",
            "titulo": "Depresión Mayor con Ideación Suicida",
            "nivel": "Avanzado",
            "nivel_color": "rose",
            "sintomatologia": [
                "Anhedonia severa",
                "Insomnio terminal",
                "Pensamientos de muerte recurrentes",
                "Aislamiento social progresivo"
            ],
            "edad_paciente": "45 años",
            "sexo": "Masculino",
            "slug": "caso-02-depresion-ideacion"
        },
        {
            "id": 3,
            "numero": "03",
            "titulo": "TDAH en Adulto no Diagnosticado",
            "nivel": "Principiante",
            "nivel_color": "emerald",
            "sintomatologia": [
                "Dificultad de concentración laboral",
                "Impulsividad en decisiones",
                "Historial de bajo rendimiento académico",
                "Problemas de organización"
            ],
            "edad_paciente": "32 años",
            "sexo": "Masculino",
            "slug": "caso-03-tdah-adulto"
        },
        {
            "id": 4,
            "numero": "04",
            "titulo": "Trastorno de Estrés Postraumático",
            "nivel": "Avanzado",
            "nivel_color": "rose",
            "sintomatologia": [
                "Flashbacks intrusivos",
                "Hipervigilancia constante",
                "Evitación de estímulos relacionados",
                "Alteraciones del sueño (pesadillas)"
            ],
            "edad_paciente": "35 años",
            "sexo": "Femenino",
            "slug": "caso-04-tept"
        },
        {
            "id": 5,
            "numero": "05",
            "titulo": "Trastorno Obsesivo-Compulsivo",
            "nivel": "Intermedio",
            "nivel_color": "amber",
            "sintomatologia": [
                "Obsesiones de contaminación",
                "Rituales de lavado compulsivo",
                "Pensamientos egodistónicos",
                "Interferencia funcional significativa"
            ],
            "edad_paciente": "24 años",
            "sexo": "Femenino",
            "slug": "caso-05-toc"
        },
        {
            "id": 6,
            "numero": "06",
            "titulo": "Fobia Social Generalizada",
            "nivel": "Principiante",
            "nivel_color": "emerald",
            "sintomatologia": [
                "Miedo a evaluación negativa",
                "Evitación de situaciones sociales",
                "Ruborización y temblor",
                "Anticipación ansiosa"
            ],
            "edad_paciente": "19 años",
            "sexo": "Masculino",
            "slug": "caso-06-fobia-social"
        },
    ]
    
    total_casos = len(casos)
    
    return render_template('casos.html',
                           casos=casos,
                           total_casos=total_casos)

