#!/usr/bin/env python3
"""
==========================================================================
NEXUS CIENCIA - SCRIPT DE ACTUALIZACIÓN
==========================================================================
Este script ayuda a aplicar las mejoras implementadas en el proyecto.

Ejecutar con: python upgrade.py
==========================================================================
"""

import os
import sys
import subprocess

def print_header(title):
    """Imprime un encabezado visual."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def run_command(cmd, description):
    """Ejecuta un comando y muestra el resultado."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"   Output: {e.output}")
        return False

def main():
    """Ejecuta el proceso de actualización paso a paso."""
    
    print_header("NEXUS CIENCIA - ACTUALIZACIÓN DEL SISTEMA")
    
    print("Este script instalará las nuevas dependencias y validará la configuración.\n")
    
    # Paso 1: Verificar archivo .env
    print_header("1. Verificando Configuración")
    
    if not os.path.exists('.env'):
        print("⚠️  ADVERTENCIA: Archivo .env no encontrado")
        print("   📄 Se ha creado .env.example como plantilla")
        print("   🔧 Por favor, copia .env.example a .env y configura tus credenciales:")
        print("      cp .env.example .env")
        print("\n   Luego ejecuta este script nuevamente.\n")
        return
    else:
        print("✅ Archivo .env encontrado")
    
    # Paso 2: Instalar nuevas dependencias
    print_header("2. Instalando Nuevas Dependencias")
    
    if not run_command("pip install -r requirements.txt", "Instalando dependencias de producción"):
        print("\n⚠️  Error instalando dependencias. Verifica tu entorno virtual.")
        return
    
    # Paso 3: Verificar instalación
    print_header("3. Verificando Instalación")
    
    packages = ["Flask-Limiter", "gunicorn", "sqlalchemy"]
    for package in packages:
        cmd = f"pip show {package}"
        if run_command(cmd, f"Verificando {package}"):
            continue
        else:
            print(f"\n⚠️  {package} no está instalado correctamente")
            return
    
    # Paso 4: Instrucciones finales
    print_header("4. Siguientes Pasos")
    
    print("🎉 ¡Actualización completada con éxito!\n")
    print("📋 ACCIONES REQUERIDAS:")
    print("\n1. ⚠️  DETENER LA APLICACIÓN ACTUAL (python app.py)")
    print("   - Presiona Ctrl+C en la terminal donde está corriendo")
    print("\n2. 🔧 VERIFICAR CONFIGURACIÓN en .env:")
    print("   - SECRET_KEY configurada")
    print("   - GOOGLE_CLIENT_ID configurada")
    print("   - GOOGLE_CLIENT_SECRET configurada")
    print("   - ADMIN_EMAIL configurado")
    print("\n3. 🚀 REINICIAR LA APLICACIÓN:")
    print("   python app.py")
    print("\n4. ✅ VERIFICAR FUNCIONAMIENTO:")
    print("   - Visita: http://localhost:5000")
    print("   - Health check: http://localhost:5000/health")
    print("\n" + "="*70)
    print("📖 Para más información, consulta README.md")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
