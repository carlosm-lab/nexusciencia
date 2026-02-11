import os
import random
import unicodedata
import re
from datetime import datetime, timedelta

# Importamos la app, la base de datos y el modelo desde tu archivo principal
from app import app, db, Articulo, LISTA_CATEGORIAS

# --- CONFIGURACIÓN MASIVA ---
ARTICULOS_POR_CATEGORIA = 100  # 100 artículos para CADA una de las 50 categorías
URL_PDF = "https://github.com/C4RL05-M/nexus-archivos/releases/download/v1/Avena.y.Control.de.Peso.Cientifico.pdf"
URL_AUDIO = "https://github.com/C4RL05-M/nexus-archivos/releases/download/v1/El.superpoder.de.la.avena.y.el.peso.mp3"
CARPETA_TEMPLATES = os.path.join(os.getcwd(), 'templates', 'articulos')

# Contenido HTML base
CONTENIDO_HTML_BASE = """
<h2><span>Evidencia Académica y Análisis Clínico</span></h2>
<h3><span>1. Introducción al Estudio</span></h3>
<p><span>Este artículo presenta una revisión exhaustiva sobre los impactos fisiológicos y metabólicos observados en estudios recientes. La metodología aplicada prioriza ensayos controlados aleatorizados para garantizar la validez de los datos presentados en el contexto de <strong>{{CATEGORIA}}</strong>.</span></p>
<p><span>Se examinan mecanismos moleculares clave, incluyendo la interacción con receptores específicos y la modulación de vías de señalización intracelular que afectan directamente al comportamiento y la salud humana.</span></p>

<h3><span>2. Metodología y Resultados</span></h3>
<p><span>Los datos recopilados sugieren una correlación significativa entre las variables analizadas. Específicamente, se observó una mejora del <strong>25%</strong> en los marcadores biológicos asociados al bienestar en el grupo experimental comparado con el grupo control.</span></p>
<h4><span>2.1. Análisis Estadístico</span></h4>
<p><span>Utilizando modelos de regresión lineal, se determinó que la intervención tiene un impacto positivo sostenido a lo largo de 12 semanas.</span></p>

<h3><span>3. Conclusiones</span></h3>
<p><span>En conclusión, la evidencia actual respalda la integración de estas prácticas en protocolos clínicos estándar. Se recomienda, no obstante, continuar con investigaciones longitudinales para evaluar efectos a largo plazo.</span></p>
"""

def slugify(value):
    """Convierte cadenas a formato URL amigable."""
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)

def generar_datos_masivos():
    total_estimado = len(LISTA_CATEGORIAS) * ARTICULOS_POR_CATEGORIA
    print(f"--- 🚀 INICIANDO INYECCIÓN MASIVA: {total_estimado} ARTÍCULOS ---")
    print(f"--- ESTO PUEDE TARDAR UNOS MINUTOS ---")
    
    # Asegurar carpeta
    if not os.path.exists(CARPETA_TEMPLATES):
        os.makedirs(CARPETA_TEMPLATES)

    contador_global = 0
    errores = 0
    
    # Recorrer CADA categoría
    for indice_cat, categoria in enumerate(LISTA_CATEGORIAS, 1):
        
        print(f"📂 Procesando Categoría {indice_cat}/{len(LISTA_CATEGORIAS)}: {categoria}...")
        
        # Generar 100 artículos para esta categoría
        for i in range(1, ARTICULOS_POR_CATEGORIA + 1):
            contador_global += 1
            
            # Datos simulados
            titulo = f"Estudio {i}: Nuevas perspectivas en {categoria.replace('🧠 ', '').replace('🧬 ', '')}"
            
            # Slug único: Categoria + Indice
            slug_base = slugify(f"{categoria}-{i}")
            slug = slug_base[:150] # Limitar longitud por si acaso
            
            nombre_archivo = f"{slug}.html"
            ruta_archivo = os.path.join(CARPETA_TEMPLATES, nombre_archivo)
            
            # Tags variados
            tags_generados = f"{slugify(categoria).replace('-', ', ')}, estudio, investigacion, prueba-{i}"
            
            # Fecha aleatoria (últimos 2 años para variedad)
            dias_atras = random.randint(0, 730)
            fecha_art = datetime.utcnow() - timedelta(days=dias_atras)

            # 1. Crear Archivo Físico
            try:
                with open(ruta_archivo, 'w', encoding='utf-8') as f:
                    contenido_personalizado = CONTENIDO_HTML_BASE.replace("{{CATEGORIA}}", categoria)
                    f.write(contenido_personalizado)
            except Exception as e:
                print(f"❌ Error archivo {nombre_archivo}: {e}")
                errores += 1
                continue

            # 2. Agregar a DB (Sesión en memoria)
            nuevo_articulo = Articulo(
                titulo=titulo,
                slug=slug,
                categoria=categoria,
                tags=tags_generados,
                nombre_archivo=nombre_archivo,
                url_pdf=URL_PDF,
                url_audio=URL_AUDIO,
                fecha=fecha_art
            )
            db.session.add(nuevo_articulo)

        # Hacemos commit por cada categoría (cada 100 items) para no saturar la RAM
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error guardando bloque de categoría {categoria}: {e}")

    print(f"\n🎉 ¡PROCESO TERMINADO!")
    print(f"📊 Total procesados: {contador_global}")
    print(f"⚠️ Errores: {errores}")
    print(f"📂 Archivos en: {CARPETA_TEMPLATES}")

if __name__ == "__main__":
    with app.app_context():
        # Opcional: Limpiar DB previa para evitar duplicados masivos
        # print("🧹 Limpiando base de datos anterior...")
        # db.session.query(Articulo).delete()
        # db.session.commit()
        
        generar_datos_masivos()