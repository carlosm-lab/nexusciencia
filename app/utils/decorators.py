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


# Dominios educativos reconocidos a nivel mundial
DOMINIOS_EDUCATIVOS = [
    '.edu',       # Estados Unidos
    '.edu.es',    # España
    '.edu.mx',    # México
    '.edu.ar',    # Argentina
    '.edu.co',    # Colombia
    '.edu.pe',    # Perú
    '.edu.cl',    # Chile
    '.edu.br',    # Brasil
    '.edu.ec',    # Ecuador
    '.edu.uy',    # Uruguay
    '.edu.ve',    # Venezuela
    '.edu.bo',    # Bolivia
    '.edu.py',    # Paraguay
    '.edu.gt',    # Guatemala
    '.edu.sv',    # El Salvador
    '.edu.hn',    # Honduras
    '.edu.ni',    # Nicaragua
    '.edu.cr',    # Costa Rica
    '.edu.pa',    # Panamá
    '.edu.do',    # República Dominicana
    '.edu.cu',    # Cuba
    '.ac.uk',     # Reino Unido
    '.ac.jp',     # Japón
    '.ac.kr',     # Corea del Sur
    '.ac.in',     # India
    '.ac.za',     # Sudáfrica
    '.edu.au',    # Australia
    '.ac.nz',     # Nueva Zelanda
    '.edu.cn',    # China
    '.edu.tw',    # Taiwán
    '.edu.sg',    # Singapur
]


def es_email_educativo(email: str) -> bool:
    """
    Verifica si un email pertenece a una institución educativa.
    
    Comprueba contra una lista de dominios educativos internacionales.
    
    Args:
        email: Dirección de correo electrónico
    
    Returns:
        True si el dominio es educativo
    """
    if not email:
        return False
    email_lower = email.strip().lower()
    return any(email_lower.endswith(dominio) for dominio in DOMINIOS_EDUCATIVOS)


def edu_required(f):
    """
    Decorador que requiere acceso educativo verificado.
    
    Verifica que el usuario:
    1. Esté autenticado
    2. Tenga acceso_edu = True (correo .edu o aprobado por admin)
    
    Si no tiene acceso, muestra la página de acceso restringido.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import render_template
        from app.models.usuario import Usuario
        
        if 'user_email' not in session:
            return redirect(url_for('auth.login'))
        
        usuario = Usuario.query.filter_by(email=session['user_email']).first()
        
        # Admin siempre tiene acceso
        admin_email = current_app.config.get('ADMIN_EMAIL', '')
        if admin_email and session.get('user_email', '').strip().lower() == admin_email.strip().lower():
            return f(*args, **kwargs)
        
        if not usuario or not usuario.acceso_edu:
            return render_template('acceso_edu_requerido.html'), 403
        
        return f(*args, **kwargs)
    return decorated_function
