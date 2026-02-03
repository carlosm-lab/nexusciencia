# Scripts Utilities - Documentation

This directory contains utility scripts for database management, data injection, and maintenance tasks.

---

## 📁 Available Scripts

### `backup_db.ps1`
**Purpose**: Automated database backup for Windows environments

**Usage**:
```powershell
.\scripts\backup_db.ps1
```

**What it does**:
- Creates timestamped backup of the database
- Stores backup in `backups/` directory
- Useful for pre-deployment backups

**Environment**: Windows (PowerShell)

---

### `inyectar_datos.py`
**Purpose**: Generate test data for development and testing

**Usage**:
```bash
python scripts/inyectar_datos.py
```

**What it does**:
- Creates sample users
- Generates test articles with various categories
- Populates database with realistic data

**⚠️ Warning**: Only use in development/staging environments, NOT in production

**Requirements**:
- Active database connection
- Flask app context

---

### `generar_arbol.py`
**Purpose**: Generate project structure tree

**Usage**:
```bash
python scripts/generar_arbol.py
```

**Output**: Creates `arbol_proyecto.txt` with directory structure

**Useful for**:
- Documentation
- Onboarding new developers
- Understanding project layout

---

### `limpiar_log.py`
**Purpose**: Clean and rotate old log files

**Usage**:
```bash
python scripts/limpiar_log.py
```

**What it does**:
- Removes logs older than configured threshold
- Compresses archived logs
- Frees up disk space

**Configuration**: Edit `MAX_LOG_AGE_DAYS` in script

---

### `upgrade.py`
**Purpose**: Run database migrations

**Usage**:
```bash
python scripts/upgrade.py
```

**What it does**:
- Applies pending Flask-Migrate migrations
- Updates database schema
- Logs migration status

**Alternative**: You can also use `flask db upgrade` directly

---

## 🚀 Quick Reference

### Pre-Deployment Checklist
```bash
# 1. Backup database
.\scripts\backup_db.ps1

# 2. Run migrations
python scripts/upgrade.py

# 3. Test in staging
python run.py

# 4. Deploy to production
```

### Development Setup
```bash
# 1. Generate test data
python scripts/inyectar_datos.py

# 2. View project structure
python scripts/generar_arbol.py
```

### Maintenance
```bash
# Clean old logs
python scripts/limpiar_log.py

# Backup before major changes
.\scripts\backup_db.ps1
```

---

## ⚙️ Adding New Scripts

When creating new utility scripts:

1. **Add docstring** with purpose and usage
2. **Add entry** to this README.md
3. **Use proper error handling**
4. **Log actions** for audit trail
5. **Make it idempotent** (safe to run multiple times)

**Template**:
```python
"""
Script description

Usage: python scripts/my_script.py
"""

import logging

logger = logging.getLogger(__name__)

def main():
    logger.info("Starting my_script...")
    # Your code here
    logger.info("Completed successfully")

if __name__ == '__main__':
    main()
```

---

## 📝 Notes

- All scripts assume they're run from the **project root** directory
- Scripts requiring database access need proper `.env` configuration
- Backup scripts should be run regularly (consider cron jobs)
- Test scripts in staging before production use

---

**Last Updated**: December 2025
