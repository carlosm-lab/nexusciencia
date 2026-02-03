"""
Punto de entrada de la aplicación (reemplaza app.py monolítico)
"""

from app import create_app
from app.extensions import db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # El modo debug se controla por FLASK_ENV en config
    debug_mode = app.config.get('DEBUG', False)
    
    # host='0.0.0.0' permite acceso desde cualquier dispositivo en la red local
    print(f"🌐 Servidor iniciando en puerto 5000 (Debug: {debug_mode})")
    print(f"📱 Accesible en red local: http://0.0.0.0:5000")
    print(f"💡 Usa la IP de tu computadora para acceder desde otros dispositivos")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
