import os

# --- CONFIGURACIÓN ---
# Si pones este archivo DENTRO de D:\nexusciencia, puedes dejarlo como '.'
# Si lo ejecutas desde otro lado, usa: r"D:\nexusciencia"
RUTA_OBJETIVO = r"D:\nexusciencia"

# Carpetas que NO queremos ver en el árbol (Ruido)
CARPETAS_IGNORAR = {
    '__pycache__', 
    '.git', 
    'venv', 
    'env', 
    '.idea', 
    '.vscode',
    'instance', # A veces contiene la DB local, opcional ocultarla
    'migrations' # Si usas Flask-Migrate y hay muchos archivos
}

# Archivos específicos a ignorar (Opcional)
ARCHIVOS_IGNORAR = {
    '.DS_Store', 
    'Thumbs.db',
    'generar_arbol.py' # Para que no se liste a sí mismo
}

ARCHIVO_SALIDA = "arbol_proyecto.txt"

def generar_arbol(ruta_inicio):
    arbol = []
    
    # Validar que la ruta existe
    if not os.path.exists(ruta_inicio):
        return [f"❌ Error: La ruta '{ruta_inicio}' no existe."]

    arbol.append(f"📂 PROYECTO: {os.path.basename(os.path.abspath(ruta_inicio))}")
    arbol.append(f"📍 RUTA: {os.path.abspath(ruta_inicio)}")
    arbol.append("="*50)

    # Recorrer el directorio
    for raiz, directorios, archivos in os.walk(ruta_inicio):
        # 1. Filtrar directorios ignorados (modificamos la lista 'directorios' in-place)
        directorios[:] = [d for d in directorios if d not in CARPETAS_IGNORAR]
        
        # 2. Calcular nivel de indentación
        nivel = raiz.replace(ruta_inicio, '').count(os.sep)
        indentacion = '│   ' * (nivel)
        
        # 3. Agregar nombre de la subcarpeta actual (si no es la raíz)
        if raiz != ruta_inicio:
            carpeta = os.path.basename(raiz)
            arbol.append(f"{indentacion[:-4]}├── 📁 {carpeta}/")
            
        # 4. Agregar archivos
        sub_indentacion = '│   ' * (nivel + 1)
        for archivo in archivos:
            if archivo not in ARCHIVOS_IGNORAR:
                arbol.append(f"{sub_indentacion}├── {archivo}")

    return arbol

if __name__ == "__main__":
    print(f"🔍 Generando árbol de: {RUTA_OBJETIVO}...")
    
    contenido = generar_arbol(RUTA_OBJETIVO)
    
    try:
        with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as f:
            f.write("\n".join(contenido))
        print(f"✅ ¡Listo! El árbol se guardó en: {ARCHIVO_SALIDA}")
    except Exception as e:
        print(f"❌ Error al guardar el archivo: {e}")