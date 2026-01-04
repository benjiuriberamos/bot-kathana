# Script PowerShell para generar el ejecutable
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Generando ejecutable BotKathana.exe" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activar el entorno virtual si existe
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# Verificar y cerrar BotKathana.exe si está en ejecución
$processName = "BotKathana"
$processes = Get-Process -Name $processName -ErrorAction SilentlyContinue
if ($processes) {
    Write-Host "BotKathana.exe está en ejecución. Cerrando proceso..." -ForegroundColor Yellow
    $processes | Stop-Process -Force
    Start-Sleep -Seconds 2
}

# Limpiar builds anteriores (opcional)
if (Test-Path "build") {
    Write-Host "Limpiando builds anteriores..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue
}

# Intentar eliminar el ejecutable anterior si existe
$exePath = "dist\BotKathana.exe"
if (Test-Path $exePath) {
    Write-Host "Eliminando ejecutable anterior..." -ForegroundColor Yellow
    try {
        Remove-Item -Path $exePath -Force -ErrorAction Stop
        Write-Host "Ejecutable anterior eliminado correctamente." -ForegroundColor Green
    } catch {
        Write-Host "No se pudo eliminar el ejecutable anterior. Intentando continuar..." -ForegroundColor Yellow
        Write-Host "Si falla, cierra manualmente BotKathana.exe y vuelve a intentar." -ForegroundColor Yellow
    }
}

# Ejecutar PyInstaller
Write-Host ""
Write-Host "Ejecutando PyInstaller..." -ForegroundColor Yellow
pyinstaller BotKathana.spec --clean

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "¡Ejecutable generado exitosamente!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "El ejecutable se encuentra en: dist\BotKathana.exe" -ForegroundColor Green
    Write-Host ""
    Write-Host "NOTA: Asegúrate de que Tesseract OCR esté instalado" -ForegroundColor Yellow
    Write-Host "en el sistema donde se ejecute el programa." -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Error al generar el ejecutable" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Posibles causas:" -ForegroundColor Yellow
    Write-Host "1. BotKathana.exe está en ejecución - Cierra el programa y vuelve a intentar" -ForegroundColor Yellow
    Write-Host "2. El archivo está bloqueado por otro programa" -ForegroundColor Yellow
    Write-Host "3. Permisos insuficientes" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Solución: Cierra BotKathana.exe completamente y ejecuta este script nuevamente." -ForegroundColor Cyan
    Write-Host ""
}

Read-Host "Presiona Enter para continuar"

