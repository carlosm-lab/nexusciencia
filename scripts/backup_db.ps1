# Script de Backup para NexusCiencia
# Ejecutar: .\scripts\backup_db.ps1

$date = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "backups"

# Crear directorio de backups si no existe
if (!(Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
    Write-Host "✅ Directorio de backups creado" -ForegroundColor Green
}

# Para SQLite (desarrollo)
if (Test-Path "instance/nexusciencia.db") {
    $sqliteBackup = "$backupDir/sqlite_backup_$date.db"
    Copy-Item "instance/nexusciencia.db" $sqliteBackup
    Write-Host "✅ Backup SQLite creado: $sqliteBackup" -ForegroundColor Green
}

# Para MySQL (producción)
# Descomentar y configurar credenciales
# $mysqlUser = "root"
# $mysqlPassword = "tu_password"
# $database = "nexusciencia"
# $mysqlBackup = "$backupDir/mysql_backup_$date.sql"
# 
# mysqldump -u $mysqlUser -p$mysqlPassword $database > $mysqlBackup
# Write-Host "✅ Backup MySQL creado: $mysqlBackup" -ForegroundColor Green

# Limpiar backups antiguos (mantener solo los últimos 10)
Get-ChildItem $backupDir | Sort-Object LastWriteTime -Descending | Select-Object -Skip 10 | Remove-Item
Write-Host "✅ Backups antiguos limpiados (manteniendo últimos 10)" -ForegroundColor Green

Write-Host "`n🎉 Backup completado exitosamente" -ForegroundColor Cyan
