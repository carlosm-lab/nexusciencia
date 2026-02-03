# NexusCiencia - Architecture Documentation

## System Overview

NexusCiencia is a scientific article repository built with Flask, following a modular architecture with factory pattern, blueprints, and separation of concerns.

## High-Level Architecture

```mermaid
graph TB
    User[Usuario] --> Nginx[Nginx Reverse Proxy]
    Nginx --> Gunicorn[Gunicorn WSGI Server]
    Gunicorn --> Flask[Flask Application]
    Flask --> DB[(MySQL/SQLite Database)]
    Flask --> OAuth[Google OAuth]
    Flask --> Cache[Flask-Caching]
    Flask --> Limiter[Rate Limiter]
    Flask --> Sentry[Sentry Monitoring]
```

## Application Structure

```
nexusciencia/
├── app/                        # Application package
│   ├── __init__.py            # Factory pattern entrypoint
│   ├── extensions.py          # Flask extensions
│   ├── config.py              # Configuration classes
│   ├── models/                # SQLAlchemy ORM models
│   │   ├── articulo.py        # Article model (soft delete)
│   │   ├── usuario.py         # User model (OAuth)
│   │   ├── notificacion.py    # Notification model
│   │   ├── log.py             # Activity log model
│   │   ├── categoria.py       # Category model (dynamic)
│   │   └── biblioteca.py      # M2M association table
│   ├── routes/                # Flask blueprints (views)
│   │   ├── main.py            # Homepage, article view
│   │   ├── auth.py            # OAuth login/logout
│   │   ├── admin.py           # Admin panel CRUD
│   │   ├── api.py             # REST API endpoints
│   │   ├── perfil.py          # User profile
│   │   └── static_pages.py    # Static informational pages
│   └── utils/                 # Utility functions
│       ├── sanitizers.py      # HTML sanitization
│       ├── validators.py      # Input validation
│       └── helpers.py         # Helper functions
├── templates/                 # Jinja2 templates
├── static/                    # CSS, JS, images
├── tests/                     # Automated tests
├── migrations/                # Flask-Migrate DB migrations
├── run.py                     # Application entry point
└── requirements.txt           # Python dependencies
```

## Request Flow

```mermaid
sequenceDiagram
    participant U as Usuario
    participant N as Nginx
    participant G as Gunicorn
    participant F as Flask App
    participant DB as Database
    
    U->>N: HTTP Request
    N->>G: Proxy Pass
    G->>F: WSGI Call
    
    F->>F: CSRF Validation
    F->>F: Rate Limiting Check
    F->>F: Route Matching
    
    alt Requires Auth
        F->>F: OAuth Verification
    end
    
    F->>DB: Query Data
    DB-->>F: Return Results
    
    F->>F: Template Rendering
    F-->>G: WSGI Response
    G-->>N: HTTP Response
    N-->>U: Final Response
```

## Database Schema

```mermaid
erDiagram
    Usuario ||--o{ Notificacion : tiene
    Usuario }o--o{ Articulo : guarda
    Articulo }o--|| Categoria : pertenece
    
    Usuario {
        int id PK
        string email UK
        string nombre
        datetime fecha_registro
        datetime fecha_ultimo_login
    }
    
    Articulo {
        int id PK
        string titulo
        string slug UK
        string categoria
        string tags
        string nombre_archivo
        string url_pdf
        string url_audio
        datetime fecha
        datetime deleted_at
    }
    
    Categoria {
        int id PK
        string nombre UK
        string icono
        int orden
        bool activa
        datetime fecha_creacion
    }
    
    Notificacion {
        int id PK
        int user_id FK
        string titulo
        string mensaje
        datetime fecha
        bool leido
    }
    
    LogActividad {
        int id PK
        string tipo_evento
        string detalle
        datetime fecha
    }
```

## Component Architecture

### Factory Pattern

```python
# app/__init__.py
def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(get_config())
    
    configure_logging(app)
    register_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_context_processors(app)
    
    return app
```

### Blueprints (MTV Pattern)

```mermaid
graph LR
    R[Routes/Blueprints] --> C[Controllers/Views]
    C --> M[Models/ORM]
    C --> T[Templates/Jinja2]
    M --> DB[(Database)]
    T --> HTML[HTML Response]
```

Each blueprint handles a specific domain:
- **main_bp**: Public pages (homepage, article view)
- **auth_bp**: Authentication flow
- **admin_bp**: Admin panel and CRUD operations
- **api_bp**: REST API for AJAX interactions
- **chat_bp**: AI chat with Google Gemini integration
- **perfil_bp**: User profile management
- **pages_bp**: Static informational pages

## Security Architecture

### Defense in Depth

```mermaid
graph TD
    A[User Input] --> B[CSRF Token Validation]
    B --> C[Rate Limiting]
    C --> D[Input Validation]
    D --> E[HTML Sanitization]
    E --> F[SQL Injection Prevention ORM]
    F --> G[XSS Prevention]
    G --> H[HTTPS Enforcement]
    H --> I[Secure Session Cookies]
```

### Security Layers

1. **Network**: HTTPS only (Talisman)
2. **Application**: CSRF, Rate Limiting, Input Validation
3. **Data**: HTML Sanitization, Parameterized Queries
4. **Session**: Secure cookies (HTTPONLY, SECURE, SAMESITE)
5. **Monitoring**: Sentry error tracking

## Performance Optimizations

### Database Optimization

```python
# N+1 Query Prevention
usuario = Usuario.query.options(
    selectinload(Usuario.articulos_guardados)
).filter_by(email=email).first()

# Indexing Strategy
class Articulo(db.Model):
    slug = db.Column(db.String(200), index=True)  # Lookup
    categoria = db.Column(db.String(100), index=True)  # Filter
    tags = db.Column(db.String(200), index=True)  # Search
    fecha = db.Column(db.DateTime, index=True)  # Sort
```

### Caching Strategy

```python
# Flask-Assets: Bundle & Minify
{% assets "css_all" %}
    <link rel="stylesheet" href="{{ ASSET_URL }}">
{% endassets %}

# View Caching (future)
@cache.cached(timeout=300, key_prefix='homepage')
def inicio():
    ...
```

### Frontend Performance

- **Lazy Loading**: All images have `loading="lazy"`
- **Preconnect**: DNS prefetch for CDNs
- **SRI**: Subresource integrity for external resources
- **Asset Bundling**: Combined and minified CSS/JS

## Data Flow - Article Creation

```mermaid
flowchart TD
    A[Admin Upload HTML] --> B[CSRF Validation]
    B --> C[Input Validation]
    C --> D{Valid?}
    D -->|No| E[Return Error]
    D -->|Yes| F[Sanitize HTML]
    F --> G[Save to Filesystem]
    G --> H{Success?}
    H -->|No| I[Rollback & Log Error]
    H -->|Yes| J[Create DB Record]
    J --> K{DB Success?}
    K -->|No| L[Delete File & Rollback]
    K -->|Yes| M[Commit Transaction]
    M --> N[Log Activity]
    N --> O[Redirect to Admin]
```

## Configuration Management

### Environments

```python
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
```

### Environment Variables

```bash
# Security
SECRET_KEY=...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

# Database
DATABASE_URL=mysql+pymysql://user:pass@host/db

# Monitoring
SENTRY_DSN=...

# Environment
FLASK_ENV=production
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Production Server"
        N[Nginx :80/443]
        G[Gunicorn :8000]
        F[Flask App]
        N --> G
        G --> F
    end
    
    subgraph "Data Layer"
        DB[(MySQL Database)]
        FS[Filesystem Storage]
        F --> DB
        F --> FS
    end
    
    subgraph "External Services"
        OAuth[Google OAuth]
        Gemini[Google Gemini AI]
        S[Sentry Monitoring]
        F --> OAuth
        F --> Gemini
        F --> S
    end
```

### Docker Container

```dockerfile
# Multi-stage build potential
FROM python:3.11-slim

# Non-root user for security
RUN useradd -m nexus

# Application code
COPY --chown=nexus:nexus . /app
WORKDIR /app

# Dependencies
RUN pip install -r requirements.txt

# Health check
HEALTHCHECK CMD python -c "import requests; ..."

# Run as non-root
USER nexus
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "run:app"]
```

## Monitoring & Logging

### Structured Logging

```python
logger.info("Article created", extra={
    'slug': slug,
    'user': email,
    'event': 'article_created'
})
```

### Log Rotation

- Max file size: 10MB
- Backup count: 5
- Format: `%(asctime)s [%(levelname)s] %(name)s: %(message)s`

### Error Monitoring

- **Sentry**: Real-time error tracking in production
- **Health Check**: `/health` endpoint for uptime monitoring

## Testing Strategy

### Test Pyramid

```
        /\
       /  \      E2E Tests (Future)
      /____\
     /      \    Integration Tests
    /________\
   /          \  Unit Tests (Current)
  /____________\
```

### Current Coverage

- **Unit Tests**: Sanitizers, Validators, Models
- **Integration Tests**: API endpoints, Auth flow
- **Target Coverage**: >70%

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html tests/

# Specific module
pytest tests/test_sanitization.py -v
```

## Scalability Considerations

### Horizontal Scaling

- **Stateless Application**: Session data in secure cookies
- **Load Balancer**: Multiple Gunicorn workers
- **Database**: Connection pooling configured

### Vertical Scaling

- **Gunicorn Workers**: `workers = (2 * CPU_cores) + 1`
- **Database Pool**: Pre-ping enabled, 1h recycle
- **Caching**: Simple cache (upgrade to Redis for scale)

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, Flask 3.1.2 |
| **Database** | MySQL/SQLite, SQLAlchemy ORM |
| **Frontend** | Bootstrap 5.3, Vanilla JS |
| **Auth** | Google OAuth (Authlib) |
| **AI** | Google Gemini (google-genai SDK) |
| **Security** | Flask-WTF (CSRF), Talisman (HTTPS), nh3 (XSS) |
| **API** | RESTful, Swagger/Flasgger |
| **Testing** | pytest, coverage |
| **Deployment** | Gunicorn, Nginx, Docker |
| **Monitoring** | Sentry, Structured Logging |

---

## Design Principles

1. **Separation of Concerns**: Models, Views, Controllers in separate modules
2. **DRY**: Reusable utilities and helpers
3. **Security First**: Multiple layers of validation and sanitization
4. **Performance**: Indexed queries, lazy loading, bundling
5. **Testability**: Factory pattern enables easy testing
6. **Maintainability**: Clear structure, comprehensive documentation

---

**Last Updated**: December 2025  
**Version**: 4.0.0
