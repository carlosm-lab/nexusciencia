"""
Flask Extensions Initialization
Extensiones Flask sin vincular a la app (se vinculan en factory)
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from authlib.integrations.flask_client import OAuth
from flask_assets import Environment

# Inicializar extensiones (sin vincular a app)
db = SQLAlchemy()
migrate = Migrate()
oauth = OAuth()
csrf = CSRFProtect()
cache = Cache()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
assets = Environment()

