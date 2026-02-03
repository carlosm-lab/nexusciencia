# NexusCiencia - Repositorio de Artículos Científicos

[![Tests](https://img.shields.io/badge/tests-11%2F11%20passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()
[![Flask](https://img.shields.io/badge/flask-3.1.2-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Quality](https://img.shields.io/badge/quality-10%2B%2F10-gold)]()

Plataforma web para gestión y visualización de artículos científicos de psicología con sistema de autenticación OAuth, biblioteca personal y panel de administración.

---

## 🌟 Características

- 💎 **Premium Academic UI** - Diseño "Seamless" con Mesh Gradients y Glassmorphism
- 📚 **Repositorio de Fuentes** - Acceso a papers crudos (PubMed, Scopus, etc.)
- 🩺 **Casos Clínicos** - Expedientes médicos interactivos para práctica diagnóstica
- 🎯 **Landing SEO-Optimizada** - Página de inicio diseñada para máxima visibilidad
- 🔒 **Autenticación Google OAuth** - Login seguro con Google
- 🎨 **UI Moderna** - Diseño responsive con animaciones suaves y tipografía Inter
- 🛡️ **Seguridad Enterprise** - CSRF, rate limiting, sanitización HTML
- 📊 **Panel Admin** - Gestión completa de artículos
- ✅ **Tests Automatizados** - Suite de tests con 100% passing (11 tests)
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

---

## 🚀 Inicio Rápido

### Requisitos
- Python 3.11+
- MySQL/PostgreSQL (producción) o SQLite (desarrollo)
- Google OAuth credentials

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/carlosm-lab/nexusciencia.git
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
├── app/
│   ├── routes/            # Blueprint routes (main, admin, auth, etc.)
│   ├── models/            # Modelos SQLAlchemy
│   ├── services/          # Lógica de negocio
│   └── utils/             # Helpers y decoradores
│
├── static/                # Archivos estáticos
│   ├── css/               # Tailwind + Custom CSS
│   ├── js/                # Scripts de interacción
│   └── img/               # Assets gráficos
│
├── templates/             # Templates Jinja2
│   ├── base.html          # Layout principal
│   ├── fuentes.html       # Nueva vista de repositorio
│   ├── casos.html         # Nueva vista de casos clínicos
│   └── ...
│
├── tests/                 # Tests automatizados
├── scripts/               # Scripts de utilidad
├── migrations/            # Migraciones de BD
└── instance/              # SQLite DB
```

---

## 🛡️ Seguridad

### Implementado
- ✅ **CSRF Protection** - Token en todos los formularios y APIs
- ✅ **Rate Limiting** - Por usuario autenticado (60 req/min búsqueda, 30/min APIs)
- ✅ **HTML Sanitization** - nh3 + BeautifulSoup (doble sanitización)
- ✅ **URL Validation** - Solo http/https permitidos
- ✅ **HTTPS Redirect** - Forzado en producción (Flask-Talisman)
- ✅ **Secure Headers** - HSTS, X-Frame-Options, etc.

---

## � Changelog

### v6.0.0 (2026-02-03) - Premium Academic Platform
- ✅ **UI Redesign**: Mesh Gradients, Glassmorphism, Animated Underlines
- ✅ **Repositorio de Fuentes**: Nueva sección `/fuentes` con listado de papers
- ✅ **Casos Clínicos**: Nueva sección `/casos-clinicos` para práctica
- ✅ **Full Bleed Layout**: Eliminación de contenedores boxed para look moderno
- ✅ **Trust Signals**: Badges institucionales (APA, PubMed, etc.)

### v5.0.0 (2026-02-02) - SEO Landing Page
- ✅ Landing SEO-Optimizada
- ✅ Estructura semántica JSON-LD
- ✅ Eliminado chat con IA

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
