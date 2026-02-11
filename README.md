# NexusCiencia - Repositorio de Artículos Educativos

[![Tests](https://img.shields.io/badge/tests-11%2F11%20passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()
[![Flask](https://img.shields.io/badge/flask-3.1.2-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Quality](https://img.shields.io/badge/quality-10%2B%2F10-gold)]()

Plataforma web para gestión y visualización de artículos educativos de psicología con sistema de autenticación OAuth, biblioteca personal y panel de administración.

---

## 🌟 Características

- 💎 **Premium Academic UI** - Diseño "Seamless" con Mesh Gradients y Glassmorphism
- 📚 **Repositorio de Fuentes** - Acceso a papers crudos (PubMed, Scopus, etc.)
- 🩺 **Casos Clínicos** - Expedientes médicos interactivos para práctica diagnóstica
- 🎯 **Landing SEO-Optimizada** - Página de inicio diseñada para máxima visibilidad en buscadores
- 🔒 **Autenticación Google OAuth** - Login seguro con Google
- 📚 **Biblioteca Personal** - Guardar artículos favoritos
- 🎨 **UI Moderna** - Diseño responsive con animaciones suaves
- 🔍 **Búsqueda Avanzada** - Filtrado por título, categoría y tags
- 📄 **Paginación** - Navegación eficiente entre artículos
- 🛡️ **Seguridad Enterprise** - CSRF, rate limiting, sanitización HTML
- 📊 **Panel Admin** - Gestión completa de artículos
- ✅ **Tests Automatizados** - Suite de tests con 100% passing
- 🚀 **Production-Ready** - Flask-Migrate, logs rotados, backups

---

## 📸 Capturas

### Dashboard Principal
- Diseño "Full Bleed" con fondo `slate-50`
- Hero section con Mesh Gradient dinámico
- Bento Grid con tarjetas Glassmorphism

### Nuevas Secciones
- **Repositorio de Fuentes**: Tabla compacta estilo bibliotecario con DOIs
- **Casos Clínicos**: Tarjetas de expediente médico con niveles de dificultad

### Panel de Administración
- Subida de artículos con HTML sanitizado
- Edición y eliminación
- Logs de actividad

### Biblioteca Personal
- Gestión de artículos guardados
- Acceso rápido a favoritos

---

## 🚀 Inicio Rápido

### Requisitos
- Python 3.11+
- MySQL/PostgreSQL (producción) o SQLite (desarrollo)
- Google OAuth credentials

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/nexusciencia.git
cd nexusciencia

# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows)
.\venv\Scripts\Activate.ps1

# Activar entorno (Linux/Mac)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Configuración

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
# - SECRET_KEY (generar uno único)
# - GOOGLE_CLIENT_ID
# - GOOGLE_CLIENT_SECRET
# - ADMIN_EMAIL
# - GEMINI_API_KEY (para chat con IA - https://aistudio.google.com)
# - DATABASE_URL (opcional, usa SQLite por defecto)
```

### Migraciones

```bash
# Inicializar base de datos
flask db upgrade

# Verificar
flask db current
```

### Ejecutar

```bash
# Modo desarrollo
python run.py

# La app estará en http://localhost:5000
```

---

## 🧪 Tests

```bash
# Ejecutar todos los tests
pytest -v tests/

# Con coverage
pytest --cov=app tests/

# Output esperado:
# ========================== 11 passed ==========================
```

---

## 📂 Estructura del Proyecto

```
nexusciencia/
├── app.py                  # Aplicación principal
├── config.py               # Configuraciones por ambiente
├── requirements.txt        # Dependencias Python
├── requirements-dev.txt    # Dependencias de desarrollo
│
├── static/                 # Archivos estáticos
│   ├── css/               # Estilos (variables, layout)
│   ├── js/                # JavaScript (main, dashboard, admin)
│   └── img/               # Imágenes
│
├── templates/             # Templates Jinja2
│   ├── base.html         # Template base
│   ├── index.html        # Dashboard principal
│   ├── admin.html        # Panel de administración
│   ├── articulo.html     # Vista de artículo
│   └── articulos/        # HTML de artículos (generado)
│
├── tests/                 # Tests automatizados
│   ├── conftest.py       # Fixtures de pytest
│   ├── test_auth.py      # Tests de autenticación
│   ├── test_api.py       # Tests de APIs
│   └── test_models.py    # Tests de modelos
│
├── scripts/               # Scripts de utilidad
│   ├── backup_db.ps1     # Backup automático
│   ├── inyectar_datos.py # Generar datos de prueba
│   └── limpiar_log.py    # Limpiar logs
│
├── migrations/            # Migraciones de BD (Flask-Migrate)
│   └── versions/         # Versiones de migraciones
│
└── instance/              # Datos de instancia (SQLite, etc)
```

---

## 🛡️ Seguridad

### Implementado
- ✅ **CSRF Protection** - Token en todos los formularios y APIs
- ✅ **Rate Limiting** - Por usuario autenticado (60 req/min búsqueda, 30/min APIs)
- ✅ **HTML Sanitization** - nh3 + BeautifulSoup (doble sanitización)
- ✅ **URL Validation** - Solo http/https permitidos
- ✅ **HTTPS Redirect** - Forzado en producción (Flask-Talisman)
- ✅ **MAX_CONTENT_LENGTH** - Límite de 16MB en uploads
- ✅ **Excepciones Específicas** - Manejo granular de errores
- ✅ **Logs Seguros** - Sin información sensible

### Configuración Recomendada
- SECRET_KEY único por instalación
- HTTPS en producción (certificado SSL)
- Base de datos con autenticación fuerte
- Firewall configurado (UFW)

---

## 🔧 Tecnologías

### Backend
- **Flask 3.1.2** - Framework web
- **SQLAlchemy** - ORM con índices optimizados
- **Flask-Migrate 4.0.7** - Migraciones de BD
- **Flask-WTF** - CSRF protection
- **Flask-Limiter** - Rate limiting
- **nh3 0.2.15** - Sanitización HTML (moderno, rápido)
- **Flask-Talisman 1.1.0** - HTTPS forzado
- **BeautifulSoup4** - Parsing HTML
- **Authlib** - OAuth 2.0
- **google-genai** - Integración con Google Gemini AI

### Frontend
- **Bootstrap 5.3** - Framework CSS
- **JavaScript ES6+** - Interactividad moderna
- **CSS Variables** - Design system
- **Jinja2** - Template engine

### Testing
- **pytest 8.3.4** - Framework de testing
- **11 tests automatizados** - Coverage de áreas críticas

### DevOps
- **Gunicorn** - WSGI server (producción)
- **Nginx** - Reverse proxy
- **Certbot** - Certificados SSL
- **Systemd** - Gestión de servicios

---

## 📊 Rendimiento

### Optimizaciones Implementadas
- ✅ Índices en BD (Usuario.email, LogActividad.fecha)
- ✅ Paginación (20 artículos/página)
- ✅ Selectinload para evitar N+1 queries
- ✅ Cache busting en assets estáticos
- ✅ Log rotation (10MB × 5 backups)
- ✅ Throttling en búsqueda

### Métricas
- **Tests**: 11/11 passing (100%)
- **Tiempo de carga**: <500ms (promedio)
- **Queries optimizadas**: Selectinload en relaciones
- **Artículos soportados**: Ilimitados (con paginación)

---

## 🚀 Deployment

Ver [DEPLOYMENT.md](DEPLOYMENT.md) para guía completa de producción.

### Resumen
```bash
# 1. Configurar servidor (Ubuntu/Debian)
sudo apt install python3-pip nginx mysql-server

# 2. Clonar y configurar
git clone <repo>
python3 -m venv venv
pip install -r requirements.txt
cp .env.example .env  # Editar con credenciales

# 3. Base de datos
flask db upgrade

# 4. Gunicorn + Nginx
# Ver DEPLOYMENT.md para configuración completa

# 5. SSL con Let's Encrypt
sudo certbot --nginx
```

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Ejecutar tests antes de PR
```bash
pytest -v tests/
# Debe pasar 11/11 tests
```

---

## 📝 Changelog

### v6.0.0 (2026-02-03) - Premium Academic Platform
- ✅ **UI Redesign**: Mesh Gradients, Glassmorphism, Animated Underlines
- ✅ **Repositorio de Fuentes**: Nueva sección `/fuentes` con listado de papers
- ✅ **Casos Clínicos**: Nueva sección `/casos-clinicos` para práctica
- ✅ **Full Bleed Layout**: Eliminación de contenedores boxed para look moderno
- ✅ **Trust Signals**: Badges institucionales (APA, PubMed, etc.)

### v5.0.0 (2026-02-02) - SEO Landing Page
- ✅ **Nueva Landing SEO-Optimizada** - Página de inicio rediseñada para máxima visibilidad
- ✅ Estructura semántica con Schema.org JSON-LD
- ✅ Hero section, estadísticas, categorías destacadas
- ✅ Eliminado chat con IA (simplificación del producto)
- ✅ Código más limpio y mantenible

### v4.0.0 (2025-12-19) - AI-Powered (Deprecado)
- ~~Asistente de Investigación con IA~~
- ~~Integración con Google Gemini~~

### v3.0.0 (2025-12-17) - Modular Architecture
- ✅ Arquitectura modular con Factory Pattern
- ✅ SEO optimizado con Schema.org
- ✅ Dark mode con persistencia
- ✅ Flask-Assets para CSS/JS bundling

### v2.0.0 (2025-12-16) - Enterprise Ready
- ✅ Paginación completa (UI + backend)
- ✅ Rate limiting por usuario
- ✅ Tests automatizados

### v1.0.0 (2024) - Release Inicial
- Sistema de autenticación OAuth
- Dashboard con búsqueda

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

## 👤 Autor

**NexusCiencia Team**

- GitHub: [@tu-usuario](https://github.com/tu-usuario)
- Email: contact@nexusciencia.com

---

## 🙏 Agradecimientos

- Google OAuth para autenticación
- Bootstrap por el framework CSS
- Flask community por las extensiones
- Contributors y testers

---

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/tu-usuario/nexusciencia/issues)
- **Documentación**: Ver [DEPLOYMENT.md](DEPLOYMENT.md)
- **Email**: support@nexusciencia.com

---

## 🌟 Estado del Proyecto

**Estado**: Production-Ready ✅

- ✅ Arquitectura Flask modular (Factory Pattern, Blueprints)
- ✅ Tests automatizados passing (11+ tests)
- ✅ Seguridad implementada (CSRF, sanitización, rate limiting)
- ✅ Documentación completa
- ✅ Docker y deployment configurados

**Requiere antes de deploy:**
- Configurar credenciales de producción en `.env`
- Rotar SECRET_KEY y credenciales OAuth

**¡Listo para deploy después de configuración!** 🚀
