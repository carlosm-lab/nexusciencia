# Changelog

All notable changes to NexusCiencia will be documented in this file.

## [4.0.0] - 2025-12-19

### Added ✨
- **Asistente de Investigación con IA** como funcionalidad central del sitio
- **Integración con Google Gemini** (modelo `gemini-2.5-flash`) con Grounding
- **Chat interactivo** en página de inicio con diseño glassmorphism
- **Búsquedas académicas** con citas de fuentes verificables
- **Contexto del sitio** integrado (artículos, categorías, tags)
- **API REST `/api/chat`** con rate limiting y validación
- **Sistema de prompts** para comportamiento académico formal

### New Files 📁
- `app/routes/chat.py` - Blueprint de API para chat con IA
- `static/css/chat.css` - Estilos del componente chat
- `static/js/chat.js` - Lógica de interacción del chat
- `templates/index.html` - UI del chat como elemento central

### Changed 🔄
- **Página de inicio** rediseñada con chat como elemento principal
- **Flask-Assets** actualizado con bundle `css_chat`
- **Configuración** ampliada con `GEMINI_API_KEY`

### Dependencies 📦
- Added `google-genai>=1.0.0` para integración con Gemini API

### Security 🔐
- Rate limiting en endpoint de chat (30 req/min)
- Validación de longitud de mensajes (máx. 2000 caracteres)
- CSRF exempt en API con validación alternativa

---

## [3.0.0] - 2025-12-17

### Added ✨
- **Modular architecture** with factory pattern and blueprints
- **Dynamic categories system** (model ready for migration)
- **Dark mode toggle** with localStorage persistence
- **Keyboard shortcuts**: Ctrl+K (search), Esc (close modals)
- **Breadcrumb navigation** support
- **Flask-Assets** bundles for CSS/JS minification
- **Lazy loading** for images (performance improvement)
- **Comprehensive testing suite** (sanitization, validators, soft delete)
- **Documentation**: CONTRIBUTING, ARCHITECTURE, CHANGELOG
- **Sitemap.xml** and **robots.txt** for SEO
- **Structured data** (Schema.org) support
- **SRI** (Subresource Integrity) for CDN resources
- **Preconnect** hints for performance
- **Admin log pagination** (50 logs per page configurable)
- **Synchronization preview** before archiving orphaned articles

### Changed 🔄
- **Refactored 978-line app.py** into modular structure (24 files)
- **Timezone-aware datetimes** in all models
- **Case-insensitive search** (`.contains()` → `.ilike()`)
- **Validation enhanced** in admin: URLs, tags, categories
- **Filesystem operations** with try-except and rollback
- **Soft delete** in synchronization instead of physical deletion
- **SESSION_COOKIE** security: SECURE, HTTPONLY, SAMESITE
- **Database connection pooling** optimized (1h recycle, pre_ping)
- **Logging** consistent (only `logger.*`, no `print()`)
- **Blueprint URL references** updated throughout templates
- **Gunicorn** updated to 23.0.0

### Fixed 🐛
- **CRITICAL**: Admin edit now validates URLs to prevent malicious links
- **CRITICAL**: Admin edit validates tag length (prevent DB overflow)
- **CRITICAL**:  Filesystem errors with rollback (no partial updates)
- **CRITICAL**: Synchronization uses soft delete with confirmation UI
- **CRITICAL**: Magic numbers replaced with Config constants
- Search now works correctly with accents and case variations
- Multiple commits per operation → single transactional commit
- Timezone-naive datetime issues resolved

### Security 🔐
- Enhanced URL validation prevents XSS via javascript: URLs
- Session cookies secured (SECURE, HTTPONLY, SAMESITE policies)
- CSP (Content Security Policy) headers configured
- SRI hashes on Bootstrap CDN
- Improved HTML sanitization with lazy loading

### Performance ⚡
- Preconnect hints for CDN resources
- Lazy loading on all images (#️⃣)
- Flask-Assets CSS/JS bundling and minification
- Optimized N+1 queries with `selectinload()`
- DB connection pool tuning (1h recycle vs 4.6min)

### Documentation 📚
- Comprehensive CONTRIBUTING.md
- ARCHITECTURE.md with system diagrams
- Separate CHANGELOG.md (this file)
- scripts/README.md documenting utility scripts
- Improved code comments and docstrings

---

## [2.0.0] - 2025-12-16

### Added
- **Google OAuth authentication**
- **Soft delete functionality** for articles
- **Personal library** for users
- **Advanced search** with filtering
- **Paginación** in article listings
- **CSRF protection** on all forms/APIs
- **Rate limiting** on critical endpoints
- **Flask-Assets** for asset management
- **Swagger/Flasgger** API documentation
- **Talisman** for HTTPS enforcement
- **Sentry** integration for error monitoring
- **Automated tests** with pytest
- **Docker** containerization
- **Flask-Migrate** for database migrations

### Changed
- Enhanced UI with modern design
- Improved security headers
- Better error handling
- Performance optimizations with caching
- Responsive design improvements

---

## [1.0.0] - Initial Release

### Added
- Basic article repository
- Static content management
- Simple categorization
- PDF/audio links support

---

## Upgrade Guide

### v3.0 → v4.0

**Dependencies:**
```bash
pip install google-genai>=1.0.0
```

**Environment:**
```bash
# Add to .env:
GEMINI_API_KEY=your-gemini-api-key  # Get free key at https://aistudio.google.com
```

**New Features:**
- AI Research Assistant on homepage
- `/api/chat` endpoint for AI queries
- Academic search with Google Grounding

**Note:** No database migrations required for v4.0.

---

### v2.0 → v3.0

**Database:**
```bash
flask db upgrade  # Run new migrations
```

**Environment:**
```bash
# Add to .env:
ASSET_VERSION=v3.0.0
```

**Code:**
- Update imports if customized templates
- Run tests: `pytest --cov=app tests/`

**Deployment:**
- Update Gunicorn: `pip install --upgrade gunicorn`
- Restart application server
