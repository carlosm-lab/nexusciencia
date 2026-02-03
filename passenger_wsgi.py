import sys, os

# Agregar el directorio actual al path de Python
sys.path.append(os.getcwd())

# Importar la variable 'app' desde tu archivo 'app.py'
from app import app as application