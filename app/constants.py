"""
Constantes globales de la aplicación NexusCiencia.

Este módulo centraliza TODOS los valores constantes usados en la aplicación
para evitar duplicación y garantizar consistencia.

Nota: Para configuración que varía por ambiente, ver app/config.py
"""

# =============================================================================
# CATEGORÍAS DE ARTÍCULOS
# =============================================================================
# Lista maestra de categorías para consistencia en todo el sitio

LISTA_CATEGORIAS = [
    "🧠 Psi. del Estrés y la Ansiedad",
    "🍎 Psi. de la Alimentación y Conducta",
    "🏃‍♂️ Ejercicio, Actividad Física y Psi.",
    "⚖️ Psi. y Pérdida de Peso",
    "💻 Tecnología y Conducta",
    "🧩 Psi. y Neurociencia del Comportamiento",
    "🧬 Psi. Clínica y Salud Mental",
    "🧩 Psi. Social y del Comportamiento",
    "🌱 Psi. Positiva y Prevención",
    "🧠 Aplicaciones Avanzadas (IA y Datos)",
    "🌈 Psi. de la Sexualidad y Orientación",
    "💞 Comportamiento Sexual y Afectivo",
    "🧠 Psi. del Comportamiento Humano",
    "🧬 Psi. de la Personalidad",
    "❤️ Psi. de las Relaciones Humanas",
    "🧩 Psi. Cognitiva y Emocional",
    "🧠 Psi. Social y del Género",
    "🌿 Psi. Clínica y Salud Sexual",
    "💬 Psi. del Desarrollo y Edu. Sexual",
    "🧠 Psi. Contemporánea y Sociedad",
    "🧩 Fundamentos y Conceptos de Conducta",
    "⚙️ Psi. Experimental y Análisis",
    "🧠 Conducta y Neurociencia",
    "🧍‍♂️ Psi. del Comportamiento Individual",
    "👥 Conducta Social y Grupal",
    "🧬 Conducta y Aprendizaje",
    "💡 Psi. Cognitivo-Conductual",
    "⚖️ Conducta y Ética Psicológica",
    "🧩 Psi. Aplicada al Comportamiento",
    "🔬 Conducta y Ciencia del Comportamiento",
    "⚖️ Fundamentos de la Psi. Criminal",
    "🧠 Neuropsicología del Crimen",
    "👥 Psi. del Delincuente",
    "🧩 Psi. Forense y Evaluación",
    "🔪 Conducta Violenta y Agresiva",
    "🧬 Conducta Criminal y Desarrollo",
    "🔍 Perfilación Criminal y Predictiva",
    "💀 Psi. del Asesino Serial",
    "💬 Psi. Social del Crimen",
    "🧘‍♂️ Prevención y Psi. Penitenciaria",
    "🧠 Neurociencia y Conducta",
    "⚙️ Aprendizaje y Conducta Adaptativa",
    "🧬 Psicobiología del Estrés y Emoción",
    "🧩 Personalidad y Trastornos",
    "⚖️ Toma de Decisiones y Control",
    "👥 Psi. Social y Conducta Colectiva",
    "💀 Violencia, Agresión y Antisocial",
    "🧘 Autocontrol y Regulación Emocional",
    "💻 Psi. y Tecnología",
    "⚖️ Ética, Ciencia y Responsabilidad"
]

# =============================================================================
# VALIDACIÓN DE FORMULARIOS
# =============================================================================
# Longitudes máximas para campos de entrada

MAX_FIELD_LENGTHS = {
    'titulo': 200,
    'slug': 200,
    'tags': 200,
    'categoria': 100,
    'url_pdf': 500,
    'url_audio': 500,
    'detalle_log': 255,
}

# =============================================================================
# SEGURIDAD DE ARCHIVOS
# =============================================================================
# Tipos MIME permitidos para uploads
# NOTA DE SEGURIDAD: application/octet-stream se maneja en validators.py
# con validación secundaria de extensión, NO se incluye aquí por seguridad.

ALLOWED_MIME_TYPES = {
    'html': ['text/html', 'text/plain'],
    'css': ['text/css', 'text/plain'],
}

# Extensiones de archivo permitidas
ALLOWED_EXTENSIONS = {
    'html': ['.html', '.htm'],
    'css': ['.css'],
}

# =============================================================================
# LECTURA Y UI
# =============================================================================
# Velocidad de lectura para calcular tiempo estimado (palabras por minuto)
READING_SPEED_WPM = 200

# Tiempo de lectura por defecto si no se puede calcular
DEFAULT_READING_TIME_MINUTES = 5

# REMEDIACIÓN LOG-001: TOAST_DURATION_MS centralizado en Config (app/config.py)
# Importar así: from app.config import Config; Config.TOAST_DURATION_MS

# =============================================================================
# LOGGING Y SISTEMA
# =============================================================================
# Tamaño máximo de archivo de log antes de rotación
MAX_LOG_SIZE_BYTES = 10 * 1024 * 1024  # 10MB

# Número máximo de archivos de log de respaldo
MAX_LOG_BACKUP_COUNT = 5

# =============================================================================
# PAGINACIÓN
# =============================================================================
# NOTA: ARTICLES_PER_PAGE está definido en Config (app/config.py) para consistencia.
# Usar: from app.config import Config; Config.ARTICLES_PER_PAGE

# REMEDIACIÓN LOG-001: LOGS_PER_PAGE centralizado en Config (app/config.py)
# Importar así: from app.config import Config; Config.LOGS_PER_PAGE

# =============================================================================
# ASSETS Y RECURSOS
# =============================================================================
# Avatar por defecto para usuarios sin imagen de Google
DEFAULT_AVATAR_PATH = '/static/img/default-avatar.svg'


# =============================================================================
# FUNCIONES HELPER PARA CATEGORÍAS
# =============================================================================

def get_category_display_name(categoria: str) -> str:
    """
    Extrae el nombre de una categoría sin el emoji inicial.
    
    Maneja de forma robusta categorías con formato '🧠 Nombre'
    separando por el primer espacio.
    
    Args:
        categoria: Nombre completo de la categoría (ej: '🧠 Neurociencia')
        
    Returns:
        Nombre sin emoji (ej: 'Neurociencia')
        
    Examples:
        >>> get_category_display_name('🧠 Psi. del Estrés')
        'Psi. del Estrés'
        >>> get_category_display_name('Sin emoji')
        'Sin emoji'
    """
    if not categoria:
        return ''
    
    # Separar por el primer espacio para manejar emojis de cualquier longitud
    parts = categoria.split(' ', 1)
    return parts[1] if len(parts) > 1 else categoria


def get_category_emoji(categoria: str) -> str:
    """
    Extrae el emoji de una categoría.
    
    Args:
        categoria: Nombre completo de la categoría (ej: '🧠 Neurociencia')
        
    Returns:
        Emoji de la categoría (ej: '🧠') o string vacío si no tiene
    """
    if not categoria or ' ' not in categoria:
        return ''
    
    return categoria.split(' ', 1)[0]


def get_category_slug(categoria: str) -> str:
    """
    Genera un slug SEO-friendly a partir del nombre de una categoría.
    
    Transforma nombres como '🧠 Psi. del Estrés y la Ansiedad' 
    en slugs como 'psi-del-estres-y-la-ansiedad'.
    
    Args:
        categoria: Nombre completo de la categoría con emoji
        
    Returns:
        Slug URL-safe en minúsculas con guiones
        
    Examples:
        >>> get_category_slug('🧠 Psi. del Estrés y la Ansiedad')
        'psi-del-estres-y-la-ansiedad'
        >>> get_category_slug('🧬 Psi. Clínica y Salud Mental')
        'psi-clinica-y-salud-mental'
    """
    import unicodedata
    import re
    
    if not categoria:
        return ''
    
    # Extraer nombre sin emoji
    nombre = get_category_display_name(categoria)
    
    # Normalizar Unicode (quitar acentos)
    nombre = unicodedata.normalize('NFKD', nombre)
    nombre = ''.join(c for c in nombre if not unicodedata.combining(c))
    
    # Convertir a minúsculas
    nombre = nombre.lower()
    
    # Reemplazar caracteres especiales y espacios por guiones
    nombre = re.sub(r'[^a-z0-9\s-]', '', nombre)
    nombre = re.sub(r'[\s_]+', '-', nombre)
    nombre = re.sub(r'-+', '-', nombre)
    nombre = nombre.strip('-')
    
    return nombre


def get_category_by_slug(slug: str) -> str | None:
    """
    Encuentra la categoría original dado un slug.
    
    Args:
        slug: Slug SEO-friendly de la categoría
        
    Returns:
        Nombre completo de la categoría o None si no existe
    """
    for cat in LISTA_CATEGORIAS:
        if get_category_slug(cat) == slug:
            return cat
    return None


# Diccionario precalculado de slugs para mejor performance
CATEGORIAS_SLUGS = {get_category_slug(cat): cat for cat in LISTA_CATEGORIAS}

