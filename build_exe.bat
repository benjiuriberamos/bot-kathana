@echo off
echo ========================================
echo Generando ejecutable BotKathana.exe
echo ========================================
echo.

REM Activar el entorno virtual si existe
if exist venv\Scripts\activate.bat (
    echo Activando entorno virtual...
    call venv\Scripts\activate.bat
)

REM Verificar y cerrar BotKathana.exe si está en ejecución
tasklist /FI "IMAGENAME eq BotKathana.exe" 2>NUL | find /I /N "BotKathana.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo BotKathana.exe está en ejecución. Cerrando proceso...
    taskkill /F /IM BotKathana.exe >NUL 2>&1
    timeout /t 2 /nobreak >NUL
)

REM Limpiar builds anteriores (opcional)
if exist build (
    echo Limpiando builds anteriores...
    rmdir /s /q build 2>NUL
)

REM Intentar eliminar el ejecutable anterior si existe
if exist dist\BotKathana.exe (
    echo Eliminando ejecutable anterior...
    del /F /Q dist\BotKathana.exe >NUL 2>&1
    if exist dist\BotKathana.exe (
        echo ADVERTENCIA: No se pudo eliminar el ejecutable anterior.
        echo Cierra BotKathana.exe manualmente y vuelve a intentar.
    ) else (
        echo Ejecutable anterior eliminado correctamente.
    )
)

REM Ejecutar PyInstaller
echo.
echo Ejecutando PyInstaller...
pyinstaller BotKathana.spec --clean

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ¡Ejecutable generado exitosamente!
    echo ========================================
    echo El ejecutable se encuentra en: dist\BotKathana.exe
    echo.
    echo NOTA: Asegúrate de que Tesseract OCR esté instalado
    echo en el sistema donde se ejecute el programa.
    echo.
) else (
    echo.
    echo ========================================
    echo Error al generar el ejecutable
    echo ========================================
    echo.
    echo Posibles causas:
    echo 1. BotKathana.exe está en ejecución - Cierra el programa y vuelve a intentar
    echo 2. El archivo está bloqueado por otro programa
    echo 3. Permisos insuficientes
    echo.
    echo Solución: Cierra BotKathana.exe completamente y ejecuta este script nuevamente.
    echo.
)

pause

