# Script para cerrar BotKathana.exe si está en ejecución
Write-Host "Verificando si BotKathana.exe está en ejecución..." -ForegroundColor Cyan

$processName = "BotKathana"
$processes = Get-Process -Name $processName -ErrorAction SilentlyContinue

if ($processes) {
    Write-Host "BotKathana.exe está en ejecución. Cerrando proceso..." -ForegroundColor Yellow
    $processes | Stop-Process -Force
    Start-Sleep -Seconds 1
    Write-Host "Proceso cerrado correctamente." -ForegroundColor Green
} else {
    Write-Host "BotKathana.exe no está en ejecución." -ForegroundColor Green
}

Write-Host ""
Read-Host "Presiona Enter para continuar"

