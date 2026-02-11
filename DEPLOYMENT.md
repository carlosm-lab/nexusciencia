# 🚀 Guía de Deployment - NexusCiencia

## Requisitos Previos

- Python 3.11+
- MySQL/PostgreSQL (producción) o SQLite (desarrollo)
- Git
- Servidor web (Nginx recomendado)
- Certificado SSL (Let's Encrypt)

---

## 1. Preparación del Servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install python3-pip python3-venv nginx mysql-server -y

# Crear usuario para la aplicación
sudo adduser nexusciencia
sudo usermod -aG sudo nexusciencia
```

---

## 2. Clonar el Proyecto

```bash
# Cambiar al usuario de la aplicación
su - nexusciencia

# Clonar repositorio
git clone https://github.com/tu-usuario/nexusciencia.git
cd nexusciencia

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
pip install gunicorn  # Servidor WSGI para producción
```

---

## 3. Configurar Variables de Entorno

```bash
# Crear archivo .env
cp .env.example .env
nano .env
```

**Contenido del .env (PRODUCCIÓN)**:
```env
# Flask
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta-super-segura-aqui-cambiarla  # ⚠️ CAMBIAR

# Base de datos (MySQL/PostgreSQL)
DATABASE_URL=mysql://usuario:password@localhost/nexusciencia

# Google OAuth
GOOGLE_CLIENT_ID=tu-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=tu-client-secret

# Google Gemini AI (Chat)
GEMINI_API_KEY=tu-gemini-api-key  # Obtener en https://aistudio.google.com

# Admin
ADMIN_EMAIL=admin@ejemplo.com

# Opcional: Sentry para monitoreo
SENTRY_DSN=https://...@sentry.io/...
```

---

## 4. Configurar Base de Datos

### MySQL

```bash
# Conectar a MySQL
sudo mysql

# Crear base de datos y usuario
CREATE DATABASE nexusciencia CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'nexusciencia'@'localhost' IDENTIFIED BY 'password-seguro';
GRANT ALL PRIVILEGES ON nexusciencia.* TO 'nexusciencia'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Aplicar Migraciones

```bash
# Activar entorno virtual
source venv/bin/activate

# Aplicar migraciones
flask db upgrade

# Verificar
flask db current
```

---

## 5. Configurar Gunicorn

**Crear archivo de servicio systemd**:

```bash
sudo nano /etc/systemd/system/nexusciencia.service
```

**Contenido**:
```ini
[Unit]
Description=NexusCiencia - Plataforma de Artículos Educativos
After=network.target mysql.service

[Service]
Type=notify
User=nexusciencia
Group=www-data
WorkingDirectory=/home/nexusciencia/nexusciencia
Environment="PATH=/home/nexusciencia/nexusciencia/venv/bin"
ExecStart=/home/nexusciencia/nexusciencia/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind unix:/home/nexusciencia/nexusciencia/nexusciencia.sock \
    --timeout 120 \
    --log-level info \
    --access-logfile /var/log/nexusciencia/access.log \
    --error-logfile /var/log/nexusciencia/error.log \
    app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Crear directorio de logs**:
```bash
sudo mkdir -p /var/log/nexusciencia
sudo chown nexusciencia:www-data /var/log/nexusciencia
```

**Habilitar y arrancar servicio**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable nexusciencia
sudo systemctl start nexusciencia
sudo systemctl status nexusciencia
```

---

## 6. Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/nexusciencia
```

**Contenido**:
```nginx
server {
    listen 80;
    server_name nexusciencia.com www.nexusciencia.com;

    # Redirigir a HTTPS (después de obtener certificado)
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name nexusciencia.com www.nexusciencia.com;

    # SSL (configurar después con Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/nexusciencia.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/nexusciencia.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Logs
    access_log /var/log/nginx/nexusciencia_access.log;
    error_log /var/log/nginx/nexusciencia_error.log;

    # Archivos estáticos
    location /static {
        alias /home/nexusciencia/nexusciencia/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy a Gunicorn
    location / {
        proxy_pass http://unix:/home/nexusciencia/nexusciencia/nexusciencia.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 120;
        proxy_send_timeout 120;
        proxy_read_timeout 120;
        
        # Buffer
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # Límite de tamaño de archivos (debe coincidir con MAX_CONTENT_LENGTH)
    client_max_body_size 16M;
}
```

**Habilitar sitio**:
```bash
sudo ln -s /etc/nginx/sites-available/nexusciencia /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 7. Obtener Certificado SSL

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtener certificado
sudo certbot --nginx -d nexusciencia.com -d www.nexusciencia.com

# Verificar renovación automática
sudo certbot renew --dry-run
```

---

## 8. Configurar Backups Automáticos

**Crear script de backup**:
```bash
nano /home/nexusciencia/scripts/auto_backup.sh
```

**Contenido**:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/nexusciencia/backups"
DB_NAME="nexusciencia"
DB_USER="nexusciencia"
DB_PASS="tu-password"

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

# Backup de MySQL
mysqldump -u $DB_USER -p$DB_PASS $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup de archivos importantes
tar -czf $BACKUP_DIR/files_$DATE.tar.gz \
    /home/nexusciencia/nexusciencia/instance \
    /home/nexusciencia/nexusciencia/templates/articulos

# Limpiar backups antiguos (mantener últimos 30 días)
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completado: $DATE"
```

**Hacer ejecutable**:
```bash
chmod +x /home/nexusciencia/scripts/auto_backup.sh
```

**Agregar a crontab**:
```bash
crontab -e
```

**Añadir línea** (backup diario a las 2 AM):
```cron
0 2 * * * /home/nexusciencia/scripts/auto_backup.sh >> /var/log/nexusciencia/backup.log 2>&1
```

---

## 9. Monitoreo y Logs

### Ver logs en tiempo real

```bash
# Logs de la aplicación
sudo journalctl -u nexusciencia -f

# Logs de Gunicorn
tail -f /var/log/nexusciencia/error.log

# Logs de Nginx
tail -f /var/log/nginx/nexusciencia_error.log
```

### Configurar logrotate

```bash
sudo nano /etc/logrotate.d/nexusciencia
```

**Contenido**:
```
/var/log/nexusciencia/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 nexusciencia www-data
    sharedscripts
    postrotate
        systemctl reload nexusciencia > /dev/null 2>&1 || true
    endscript
}
```

---

## 10. Comandos Útiles de Mantenimiento

```bash
# Reiniciar aplicación
sudo systemctl restart nexusciencia

# Ver estado
sudo systemctl status nexusciencia

# Ver logs recientes
sudo journalctl -u nexusciencia --since "1 hour ago"

# Actualizar código
cd /home/nexusciencia/nexusciencia
git pull
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
sudo systemctl restart nexusciencia

# Ejecutar backup manual
/home/nexusciencia/scripts/auto_backup.sh

# Verificar uso de recursos
htop
df -h
```

---

## 11. Checklist Pre-Deployment

- [ ] Variables de entorno configuradas (.env)
- [ ] SECRET_KEY cambiado a uno único
- [ ] Base de datos creada y migrada
- [ ] Google OAuth configurado (redirect URI: https://tu-dominio.com/callback)
- [ ] ADMIN_EMAIL configurado
- [ ] Certificado SSL instalado
- [ ] Nginx configurado y probado
- [ ] Gunicorn service arrancado
- [ ] Backups automáticos configurados
- [ ] Logs rotados configurados
- [ ] Firewall configurado (UFW)
- [ ] Tests pasando (pytest)

---

## 12. Firewall (UFW)

```bash
# Habilitar firewall
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

---

## 13. Optimizaciones Opcionales

### Redis para cache (opcional)

```bash
sudo apt install redis-server -y
pip install redis
```

**Actualizar config.py**:
```python
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = 'redis://localhost:6379/0'
```

### Sentry para monitoreo de errores

```bash
pip install sentry-sdk[flask]
```

**En app.py**:
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

if app.config.get('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=app.config['SENTRY_DSN'],
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0
    )
```

---

## 14. Troubleshooting

### Error: "Address already in use"
```bash
sudo lsof -i :5000
sudo kill <PID>
```

### Error: "Permission denied" en socket
```bash
sudo chown nexusciencia:www-data /home/nexusciencia/nexusciencia/nexusciencia.sock
sudo chmod 660 /home/nexusciencia/nexusciencia/nexusciencia.sock
```

### Aplicación no responde
```bash
sudo systemctl restart nexusciencia
sudo systemctl restart nginx
```

### Logs de errores
```bash
sudo journalctl -u nexusciencia -n 100 --no-pager
```

---

## 📊 Verificación Post-Deployment

```bash
# 1. Verificar servicios
sudo systemctl status nexusciencia
sudo systemctl status nginx

# 2. Probar endpoints
curl https://tu-dominio.com/health
# Debe retornar: {"status": "healthy", ...}

# 3. Verificar SSL
curl -I https://tu-dominio.com
# Debe retornar: HTTP/2 200

# 4. Verificar logs
tail -f /var/log/nexusciencia/error.log
# No debe haber errores críticos
```

---

## 🎉 Proyecto Deployado

Una vez completados todos los pasos, tu aplicación NexusCiencia estará:

- ✅ Corriendo en HTTPS
- ✅ Con certificado SSL válido
- ✅ Respaldada automáticamente
- ✅ Monitoreada con logs
- ✅ Optimizada con Nginx
- ✅ Segura (CSRF, rate limiting, etc.)
- ✅ Enterprise-ready

**URL**: https://tu-dominio.com  
**Panel Admin**: https://tu-dominio.com/admin  
**Health Check**: https://tu-dominio.com/health

¡Felicidades! 🚀
