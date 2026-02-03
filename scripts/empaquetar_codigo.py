import os

# --- CONFIGURACIÓN ---
# Nombre del archivo final
ARCHIVO_SALIDA = "CODIGO_SISTEMA_COMPLETO.txt"

# Extensiones que queremos copiar (El código fuente)
EXTENSIONES_VALIDAS = {'.py', '.html', '.css', '.js'}

# Carpetas que NO queremos tocar (Por seguridad o porque pesan mucho)
CARPETAS_IGNORAR = {
    '__pycache__', 
    '.git', 
    'venv', 
    'env', 
    'uploads',  # Ignora las fotos subidas
    'fotos', 
    'firmas', 
    'img'       # Ignora iconos o imágenes estáticas
}

# Archivos específicos a ignorar
ARCHIVOS_IGNORAR = {
    ARCHIVO_SALIDA,          # No copiarse a sí mismo
    'sistema.db',            # No copiar la base de datos (es binario)
    'data_civil.db',
    'empaquetar_codigo.py'   # No copiar este script
}

def empaquetar_proyecto():
    ruta_raiz = os.getcwd() # Toma la carpeta donde estás ejecutando el script
    
    print(f"--- 📦 EMPAQUETANDO CÓDIGO DEL SISTEMA ---")
    print(f"Ruta raíz: {ruta_raiz}\n")
    
    archivos_procesados = 0
    
    try:
        with open(ARCHIVO_SALIDA, 'w', encoding='utf-8') as salida:
            # Escribir encabezado
            salida.write("=========================================================\n")
            salida.write(f" REPORTE DE CÓDIGO FUENTE - SISTEMA DATA FUSION\n")
            salida.write("=========================================================\n\n")

            # Recorrer carpetas
            for raiz, directorios, ficheros in os.walk(ruta_raiz):
                
                # Filtrar carpetas ignoradas para que no entre en ellas
                directorios[:] = [d for d in directorios if d not in CARPETAS_IGNORAR]
                
                for fichero in ficheros:
                    nombre, extension = os.path.splitext(fichero)
                    
                    # Verificar si es un archivo de código válido y no está ignorado
                    if extension.lower() in EXTENSIONES_VALIDAS and fichero not in ARCHIVOS_IGNORAR:
                        ruta_completa = os.path.join(raiz, fichero)
                        ruta_relativa = os.path.relpath(ruta_completa, ruta_raiz)
                        
                        print(f"📄 Procesando: {ruta_relativa}")
                        
                        try:
                            # Leer contenido del archivo
                            with open(ruta_completa, 'r', encoding='utf-8', errors='ignore') as f_lectura:
                                contenido = f_lectura.read()
                                
                                # Escribir separador y contenido en el archivo final
                                salida.write(f"\n{'='*60}\n")
                                salida.write(f" ARCHIVO: {ruta_relativa}\n")
                                salida.write(f"{'='*60}\n")
                                salida.write(contenido)
                                salida.write("\n\n")
                                
                            archivos_procesados += 1
                            
                        except Exception as e:
                            print(f"⚠️ Error leyendo {fichero}: {e}")

        print(f"\n✅ ¡LISTO! Se guardaron {archivos_procesados} archivos en '{ARCHIVO_SALIDA}'.")
        print("👉 Ahora puedes subir ese único archivo al chat.")

    except Exception as e:
        print(f"❌ Error crítico al crear el archivo de salida: {e}")

if __name__ == '__main__':
    empaquetar_proyecto()
    # Pausa para que veas el resultado si lo ejecutas con doble clic
    input("\nPresiona ENTER para salir...")