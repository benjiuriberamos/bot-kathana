@echo off
echo Verificando si BotKathana.exe está en ejecución...

tasklist /FI "IMAGENAME eq BotKathana.exe" 2>NUL | find /I /N "BotKathana.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo BotKathana.exe está en ejecución. Cerrando proceso...
    taskkill /F /IM BotKathana.exe >NUL 2>&1
    timeout /t 1 /nobreak >NUL
    echo Proceso cerrado correctamente.
) else (
    echo BotKathana.exe no está en ejecución.
)

echo.
pause

