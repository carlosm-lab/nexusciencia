"""
Blueprints de rutas
"""

from .main import main_bp
from .auth import auth_bp
from .admin import admin_bp
from .api import api_bp
from .static_pages import pages_bp
from .perfil import perfil_bp
from .debug import debug_bp
from .seo import seo_bp

__all__ = [
    'main_bp',
    'auth_bp',
    'admin_bp',
    'api_bp',
    'pages_bp',
    'perfil_bp',
    'debug_bp',
    'seo_bp'
]

