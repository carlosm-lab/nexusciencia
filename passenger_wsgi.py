"""
Punto de entrada WSGI para Passenger (cPanel, shared hosting).
"""
import sys
import os

# Agregar el directorio actual al path de Python
sys.path.append(os.getcwd())

# Importar la app desde run.py (no desde el paquete app/)
from run import app as application