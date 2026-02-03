"""
Decoradores de autenticación y autorización para NexusCiencia.

Este módulo proporciona decoradores reutilizables para proteger rutas
que requieren autenticación o privilegios de administrador.
"""

from functools import wraps
from flask import redirect, url_for, session, current_app, abort


def login_required(f):
    """
    Decorador que requiere que el usuario esté autenticado.
    
    Redirige a la página de login si no hay sesión activa.
    
    Uso:
        @perfil_bp.route('/perfil')
        @login_required
        def perfil():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorador que requiere privilegios de administrador.
    
    Verifica que:
    1. El usuario esté autenticado
    2. El email del usuario coincida con ADMIN_EMAIL configurado
    
    Retorna 403 Forbidden si el usuario no es admin.
    
    Uso:
        @admin_bp.route('/dashboard')
        @admin_required
        def dashboard():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar autenticación primero
        if 'user_email' not in session:
            return redirect(url_for('auth.login'))
        
        # Verificar privilegios de admin
        admin_email = current_app.config.get('ADMIN_EMAIL', '')
        if not admin_email:
            # Si no hay email de admin configurado, denegar acceso
            abort(403, description="No hay administrador configurado en el sistema.")
        
        user_email = session.get('user_email', '').strip().lower()
        if user_email != admin_email.strip().lower():
            abort(403, description="Acceso denegado. Se requieren privilegios de administrador.")
        
        return f(*args, **kwargs)
    return decorated_function
