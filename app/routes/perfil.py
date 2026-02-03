"""
Blueprint de perfil de usuario.

Este módulo maneja la vista del perfil personal del usuario,
incluyendo su biblioteca de artículos guardados y notificaciones.
"""

from flask import Blueprint, render_template, redirect, url_for, session, current_app
from sqlalchemy.orm import selectinload
from app.extensions import db
from app.models.usuario import Usuario
from app.models.articulo import Articulo
from app.utils.decorators import login_required
from app.constants import LISTA_CATEGORIAS

# Blueprint
perfil_bp = Blueprint('perfil', __name__)


@perfil_bp.route('/perfil')
@login_required
def perfil():
    """Vista del perfil de usuario."""
    
    # Redirigir admin a su panel propio
    admin_email = current_app.config.get('ADMIN_EMAIL', '')
    if admin_email and session['user_email'].strip().lower() == admin_email.strip().lower():
        return redirect(url_for('admin.admin'))
    
    # OPTIMIZACIÓN: Usar selectinload para evitar consultas N+1
    usuario = Usuario.query.options(
        selectinload(Usuario.articulos_guardados),
        selectinload(Usuario.notificaciones)
    ).filter_by(email=session['user_email']).first()
    
    articulos_guardados = usuario.articulos_guardados if usuario else []
    notificaciones = sorted(
        usuario.notificaciones if usuario else [],
        key=lambda n: n.fecha,
        reverse=True
    )
    
    # Stats para el componente de estadísticas
    total_articulos = Articulo.get_active().count()
    total_categorias = len(LISTA_CATEGORIAS)
    
    return render_template('perfil.html',
                           articulos_guardados=articulos_guardados,
                           notificaciones=notificaciones,
                           total_articulos=total_articulos,
                           total_categorias=total_categorias)

