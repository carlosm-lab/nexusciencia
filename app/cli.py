"""
Comandos CLI para NexusCiencia
Integración Flask CLI para tareas de administración
"""

import os
import click
from flask import current_app
from flask.cli import with_appcontext


def init_app(app):
    """Registra los comandos CLI con la aplicación Flask."""
    app.cli.add_command(logs_cli)


@click.group('logs')
def logs_cli():
    """Comandos para gestión de logs"""
    pass


@logs_cli.command('clear')
@with_appcontext
def clear_logs():
    """Limpia el archivo app.log principal"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_file = os.path.join(base_dir, 'app.log')
    
    if os.path.exists(log_file):
        try:
            # Truncar en lugar de eliminar para evitar problemas con handlers activos
            with open(log_file, 'w') as f:
                f.truncate(0)
            click.echo(click.style('✅ app.log vaciado correctamente', fg='green'))
        except PermissionError:
            click.echo(click.style('⚠️ app.log está siendo usado por otro proceso', fg='yellow'))
            click.echo('   Detén el servidor primero')
        except Exception as e:
            click.echo(click.style(f'❌ Error: {e}', fg='red'))
    else:
        click.echo(click.style('ℹ️ app.log no existe', fg='blue'))


@logs_cli.command('rotate')
@with_appcontext
def rotate_logs():
    """Fuerza rotación de logs (elimina backups antiguos)"""
    import glob
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    backup_pattern = os.path.join(base_dir, 'app.log.*')
    
    backups = glob.glob(backup_pattern)
    
    if backups:
        removed = 0
        for backup in backups:
            try:
                os.remove(backup)
                removed += 1
            except Exception:
                pass
        click.echo(click.style(f'✅ {removed} archivos de backup eliminados', fg='green'))
    else:
        click.echo(click.style('ℹ️ No hay backups de logs para eliminar', fg='blue'))


@logs_cli.command('stats')
@with_appcontext
def log_stats():
    """Muestra estadísticas del archivo de log"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_file = os.path.join(base_dir, 'app.log')
    
    if os.path.exists(log_file):
        size = os.path.getsize(log_file)
        size_kb = size / 1024
        size_mb = size_kb / 1024
        
        # Contar líneas
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = sum(1 for _ in f)
        
        click.echo(f'📊 Estadísticas de app.log:')
        click.echo(f'   Tamaño: {size_mb:.2f} MB ({size_kb:.0f} KB)')
        click.echo(f'   Líneas: {lines:,}')
        
        if size_mb > 5:
            click.echo(click.style('   ⚠️ El log es grande, considera ejecutar: flask logs clear', fg='yellow'))
    else:
        click.echo(click.style('ℹ️ app.log no existe', fg='blue'))
