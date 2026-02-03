"""
Blueprint de administración: panel admin, CRUD de artículos, sincronización.

Este módulo maneja todas las operaciones administrativas del sitio,
incluyendo la creación, edición y eliminación de artículos.
"""

import os
import logging
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.extensions import db
from app.config import BASE_DIR
from app.models.articulo import Articulo
from app.models.usuario import Usuario
from app.models.log import LogActividad
from app.models.categoria import Categoria
from app.constants import LISTA_CATEGORIAS, ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES
from app.enums import LogEventType
from app.utils.sanitizers import limpiar_html_google, validar_css_seguro
from app.utils.validators import (
    validar_url_segura, 
    validar_longitud, 
    validar_extension_archivo,
    validar_mime_type,
    validar_slug
)
from app.utils.decorators import admin_required
from app.utils.form_validators import (
    validar_formulario_articulo,
    validar_archivo_upload,
    obtener_categorias_validas
)

# Blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Usar directorio base centralizado de config.py
carpeta_base = BASE_DIR

logger = logging.getLogger(__name__)


# =============================================================================
# REMEDIACIÓN DT-001: Helper para limpieza de archivos huérfanos
# =============================================================================
def cleanup_orphan_files(html_path: str = None, css_path: str = None) -> None:
    """
    Limpia archivos huérfanos creados cuando una transacción de BD falla.
    
    Previene acumulación de archivos sin registro en base de datos.
    
    Args:
        html_path: Ruta absoluta al archivo HTML (opcional)
        css_path: Ruta absoluta al archivo CSS (opcional)
    """
    for path in [html_path, css_path]:
        if path and os.path.exists(path):
            try:
                os.remove(path)
                logger.info(f"Archivo huérfano eliminado: {path}")
            except OSError as e:
                logger.warning(f"No se pudo limpiar archivo huérfano {path}: {e}")


@admin_bp.route('/', methods=['GET', 'POST'])
@admin_bp.route('', methods=['GET', 'POST'])
@admin_required
def admin():
    """Panel principal de administración."""
    mensaje = request.args.get('mensaje', "")
    
    # Procesar subida de artículo
    if request.method == 'POST':
        # REMEDIACIÓN DT-001: Variables explícitas para cleanup de archivos huérfanos
        # (reemplaza uso frágil de locals().get())
        ruta_guardado_html = None
        ruta_guardado_css = None
        
        try:
            # Obtener datos del formulario
            form_data = {
                'titulo': request.form.get('titulo', '').strip(),
                'slug': request.form.get('slug', '').strip(),
                'categoria': request.form.get('categoria', '').strip(),
                'tags': request.form.get('tags', '').strip(),
                'url_pdf': request.form.get('url_pdf', '').strip(),
                'url_audio': request.form.get('url_audio', '').strip(),
            }
            
            # VALIDACIÓN CENTRALIZADA: Usar función helper
            errores = validar_formulario_articulo(form_data)
            if errores:
                mensaje = errores[0]  # Mostrar primer error
                raise ValueError(mensaje)
            
            archivo_html = request.files.get('html_file')
            archivo_css = request.files.get('css_file')
            
            # Validación de archivo HTML (MIME type y extensión)
            html_valido, html_error = validar_archivo_upload(archivo_html, 'html', requerido=True)
            if not html_valido:
                mensaje = html_error
                raise ValueError(mensaje)
            
            # Validación de archivo CSS (opcional)
            if archivo_css and archivo_css.filename:
                css_valido, css_error = validar_archivo_upload(archivo_css, 'css', requerido=False)
                if not css_valido:
                    mensaje = css_error
                    raise ValueError(mensaje)
            
            if archivo_html and archivo_html.filename:
                # Guardar HTML limpio
                nombre_final_html = f"{form_data['slug']}.html"
                ruta_guardado_html = os.path.join(carpeta_base, 'templates', 'articulos', nombre_final_html)
                os.makedirs(os.path.dirname(ruta_guardado_html), exist_ok=True)
                
                contenido_sucio = archivo_html.read().decode('utf-8', errors='ignore')
                contenido_limpio = limpiar_html_google(contenido_sucio)
                
                with open(ruta_guardado_html, 'w', encoding='utf-8') as f:
                    f.write(contenido_limpio)
                
                # Guardar CSS opcional (con validación de seguridad)
                if archivo_css and archivo_css.filename != '':
                    contenido_css = archivo_css.read().decode('utf-8', errors='ignore')
                    css_valido, resultado_css = validar_css_seguro(contenido_css)
                    if not css_valido:
                        mensaje = resultado_css
                        raise ValueError(mensaje)
                    
                    ruta_guardado_css = os.path.join(carpeta_base, 'static', 'articulos_css', f"{form_data['slug']}.css")
                    os.makedirs(os.path.dirname(ruta_guardado_css), exist_ok=True)
                    with open(ruta_guardado_css, 'w', encoding='utf-8') as f:
                        f.write(resultado_css)
                
                # Registrar en DB
                nuevo_art = Articulo(
                    titulo=form_data['titulo'], 
                    slug=form_data['slug'], 
                    categoria=form_data['categoria'], 
                    tags=form_data['tags'],
                    nombre_archivo=nombre_final_html, 
                    url_pdf=form_data['url_pdf'], 
                    url_audio=form_data['url_audio']
                )
                db.session.add(nuevo_art)
                db.session.add(LogActividad(tipo_evento=LogEventType.ADMIN, detalle=f"Publicado: {form_data['titulo']}"))
                db.session.commit()
                mensaje = "¡Artículo publicado correctamente!"
            else:
                mensaje = "Error: Falta archivo HTML."
        except ValueError as ve:
            # Errores de validación esperados
            mensaje = str(ve)
            logger.warning(f"Validación fallida en admin: {ve}")
        except (IOError, OSError) as e:
            # Errores de filesystem
            mensaje = "Error: No se pudo guardar el archivo en el servidor."
            logger.error(f"Error de filesystem al guardar artículo: {e}", exc_info=True)
            db.session.rollback()
        except IntegrityError as e:
            # Error de integridad en BD (slug duplicado)
            # REMEDIACIÓN DT-001: Usar variables explícitas
            cleanup_orphan_files(ruta_guardado_html, ruta_guardado_css)
            mensaje = "Error: El slug ya existe. Usa un slug único."
            logger.error(f"Error de integridad en BD: {e}")
            db.session.rollback()
        except SQLAlchemyError as e:
            # Otros errores de base de datos
            # REMEDIACIÓN DT-001: Usar variables explícitas
            cleanup_orphan_files(ruta_guardado_html, ruta_guardado_css)
            mensaje = "Error de base de datos. Intenta nuevamente."
            logger.error(f"Error de BD al procesar artículo: {e}", exc_info=True)
            db.session.rollback()
        except Exception as e:
            # Errores inesperados: NO exponer detalles internos al usuario
            # REMEDIACIÓN DT-001: Usar variables explícitas
            cleanup_orphan_files(ruta_guardado_html, ruta_guardado_css)
            mensaje = "Error inesperado. Por favor contacta al administrador."
            logger.error(f"Error inesperado al procesar artículo: {e}", exc_info=True)
            db.session.rollback()
    
    # Cargar datos para el dashboard
    per_page = current_app.config.get('LOGS_PER_PAGE', 50)
    pagina_logs = request.args.get('log_page', 1, type=int)
    
    lista_articulos = Articulo.get_active().order_by(Articulo.fecha.desc()).all()
    total_usuarios = Usuario.query.count()
    total_visitas = LogActividad.query.filter_by(tipo_evento=LogEventType.LECTURA).count()
    
    # Paginación de logs
    logs_pag = LogActividad.query.order_by(LogActividad.fecha.desc()).paginate(
        page=pagina_logs, per_page=per_page, error_out=False
    )
    ultimos_eventos = logs_pag.items
    
    usuarios_recientes = Usuario.query.order_by(Usuario.fecha_ultimo_login.desc()).limit(5).all()
    
    return render_template('admin.html',
                           mensaje=mensaje,
                           usuario=session['user_name'],
                           articulos=lista_articulos,
                           total_usuarios=total_usuarios,
                           total_visitas=total_visitas,
                           ultimos_eventos=ultimos_eventos,
                           logs_pag=logs_pag,
                           usuarios_recientes=usuarios_recientes,
                           total_articulos=len(lista_articulos),
                           total_categorias=len(LISTA_CATEGORIAS))


@admin_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_editar(id):
    """Edición de artículos existentes con validación mejorada."""
    art = Articulo.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # VALIDACIÓN DE ENTRADAS COMPLETA
            titulo = request.form.get('titulo', '').strip()
            nuevo_slug = request.form.get('slug', '').strip()
            url_pdf = request.form.get('url_pdf', '').strip()
            url_audio = request.form.get('url_audio', '').strip()
            categoria = request.form.get('categoria', '').strip()
            tags = request.form.get('tags', '').strip()
            
            # Validar longitudes
            if not validar_longitud(titulo, 200):
                return redirect(url_for('admin.admin', mensaje="Error: Título muy largo"))
            if not validar_longitud(nuevo_slug, 200):
                return redirect(url_for('admin.admin', mensaje="Error: Slug muy largo"))
            if not validar_longitud(tags, 200):
                return redirect(url_for('admin.admin', mensaje="Error: Tags muy largo"))
            
            # Validar formato de slug (previene path traversal)
            if not validar_slug(nuevo_slug):
                return redirect(url_for('admin.admin', mensaje="Error: Slug inválido. Solo letras minúsculas, números y guiones."))
            
            # Validate URL security (only http/https allowed)
            if not validar_url_segura(url_pdf):
                return redirect(url_for('admin.admin', mensaje="Error: URL PDF inválida"))
            if not validar_url_segura(url_audio):
                return redirect(url_for('admin.admin', mensaje="Error: URL audio inválida"))
            
            # Validar que la categoría sea válida (usar función helper)
            if categoria:
                categorias_validas = obtener_categorias_validas()
                if categoria not in categorias_validas:
                    return redirect(url_for('admin.admin', mensaje="Error: Categoría inválida"))
            
            # Actualizar campos básicos
            art.titulo = titulo
            art.url_pdf = url_pdf
            art.url_audio = url_audio
            art.categoria = categoria
            art.tags = tags
            
            # Handle slug change with proper error handling
            if nuevo_slug != art.slug:
                try:
                    # Renombrar CSS
                    ruta_css_old = os.path.join(carpeta_base, 'static', 'articulos_css', f"{art.slug}.css")
                    ruta_css_new = os.path.join(carpeta_base, 'static', 'articulos_css', f"{nuevo_slug}.css")
                    if os.path.exists(ruta_css_old):
                        os.rename(ruta_css_old, ruta_css_new)
                    
                    # Si no se sube HTML nuevo, renombrar el viejo
                    # REMEDIACIÓN: Reutilizar archivo_html obtenido después del bloque
                    archivo_html_check = request.files.get('html_file')
                    if not archivo_html_check or archivo_html_check.filename == '':
                        ruta_html_old = os.path.join(carpeta_base, 'templates', 'articulos', art.nombre_archivo)
                        nombre_html_new = f"{nuevo_slug}.html"
                        ruta_html_new = os.path.join(carpeta_base, 'templates', 'articulos', nombre_html_new)
                        if os.path.exists(ruta_html_old):
                            os.rename(ruta_html_old, ruta_html_new)
                        art.nombre_archivo = nombre_html_new
                    
                    art.slug = nuevo_slug
                    
                except (IOError, OSError) as e:
                    db.session.rollback()
                    logger.error(f"Error filesystem en renombrado: {e}", exc_info=True)
                    return redirect(url_for('admin.admin', mensaje="Error al renombrar archivos"))
            
            # Procesar nuevos archivos si se subieron
            archivo_html = request.files.get('html_file')
            archivo_css = request.files.get('css_file')
            
            try:
                if archivo_html and archivo_html.filename != '':
                    nombre_final_html = f"{art.slug}.html"
                    ruta_guardado_html = os.path.join(carpeta_base, 'templates', 'articulos', nombre_final_html)
                    contenido_sucio = archivo_html.read().decode('utf-8', errors='ignore')
                    contenido_limpio = limpiar_html_google(contenido_sucio)
                    with open(ruta_guardado_html, 'w', encoding='utf-8') as f:
                        f.write(contenido_limpio)
                    art.nombre_archivo = nombre_final_html
                
                if archivo_css and archivo_css.filename != '':
                    contenido_css = archivo_css.read().decode('utf-8', errors='ignore')
                    css_valido, resultado_css = validar_css_seguro(contenido_css)
                    if not css_valido:
                        return redirect(url_for('admin.admin', mensaje=resultado_css))
                    
                    ruta_guardado_css = os.path.join(carpeta_base, 'static', 'articulos_css', f"{art.slug}.css")
                    with open(ruta_guardado_css, 'w', encoding='utf-8') as f:
                        f.write(resultado_css)
                
                # Single commit at the end for transaction integrity
                db.session.add(LogActividad(tipo_evento=LogEventType.ADMIN, detalle=f"Editado: {art.titulo}"))
                db.session.commit()
                
            except (IOError, OSError) as e:
                db.session.rollback()
                logger.error(f"Error filesystem en edición: {e}", exc_info=True)
                return redirect(url_for('admin.admin', mensaje="Error al actualizar archivos"))
            except IntegrityError as e:
                db.session.rollback()
                logger.error(f"Error de integridad: {e}")
                return redirect(url_for('admin.admin', mensaje="Error: Slug duplicado"))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error inesperado: {e}", exc_info=True)
                return redirect(url_for('admin.admin', mensaje="Error al actualizar artículo"))
            
            return redirect(url_for('admin.admin', mensaje="Artículo actualizado correctamente."))
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error en admin_editar: {e}", exc_info=True)
            return redirect(url_for('admin.admin', mensaje="Error inesperado al editar artículo."))
    
    return render_template('editar_articulo.html', articulo=art)


@admin_bp.route('/eliminar/<int:id>', methods=['POST'])
@admin_required
def admin_eliminar(id):
    """Soft delete de artículos (no eliminación física). Requiere POST para seguridad CSRF."""
    art = Articulo.query.get_or_404(id)
    
    # Soft delete (marcar como eliminado)
    art.soft_delete()
    db.session.commit()  # Commit explícito (Auditoría: separación de responsabilidades)
    
    return redirect(url_for('admin.admin', mensaje="Artículo movido a papelera (puede restaurarse)."))


@admin_bp.route('/restaurar/<int:id>', methods=['POST'])
@admin_required
def admin_restaurar(id):
    """Restaurar artículo soft-deleted. Requiere POST para seguridad CSRF."""
    art = Articulo.query.get_or_404(id)
    
    if art.deleted_at is None:
        return redirect(url_for('admin.admin', mensaje="El artículo ya está activo."))
    
    art.restore()
    db.session.commit()  # Commit explícito (Auditoría: separación de responsabilidades)
    
    return redirect(url_for('admin.admin', mensaje="Artículo restaurado correctamente."))


@admin_bp.route('/sincronizar', methods=['GET', 'POST'])
@admin_required
def admin_sincronizar():
    """
    Sincroniza BD con el sistema de archivos usando soft delete.
    GET: Muestra preview de artículos huérfanos
    POST: Confirma y archiva artículos huérfanos
    """
    if request.method == 'GET':
        # Mostrar preview de artículos huérfanos
        articulos = Articulo.get_active().all()
        huerfanos = []
        for art in articulos:
            ruta_full = os.path.join(carpeta_base, 'templates', 'articulos', art.nombre_archivo)
            if not os.path.exists(ruta_full):
                huerfanos.append(art)
        
        return render_template('admin_sincronizar_preview.html', huerfanos=huerfanos)
    
    # POST: Confirmar sincronización
    articulos = Articulo.get_active().all()
    eliminados = 0
    for art in articulos:
        ruta_full = os.path.join(carpeta_base, 'templates', 'articulos', art.nombre_archivo)
        if not os.path.exists(ruta_full):
            art.soft_delete()  # Soft delete instead of physical deletion
            eliminados += 1
    
    if eliminados > 0:
        db.session.add(LogActividad(tipo_evento=LogEventType.ADMIN, detalle=f"Sincronización: {eliminados} archivados"))
    
    db.session.commit()
    return redirect(url_for('admin.admin', mensaje=f"Sincronización: {eliminados} artículos archivados (pueden restaurarse)"))
