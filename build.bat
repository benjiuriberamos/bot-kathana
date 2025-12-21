@echo off
echo Construyendo ejecutable del Bot Kathana...
echo.

REM Intentar encontrar Python
set PYTHON_CMD=python
where python >nul 2>&1
if errorlevel 1 (
    REM Si no está en PATH, intentar con la ruta común
    if exist "C:\python3.10\python.exe" (
        set PYTHON_CMD=C:\python3.10\python.exe
    ) else if exist "C:\Python310\python.exe" (
        set PYTHON_CMD=C:\Python310\python.exe
    ) else if exist "C:\Python39\python.exe" (
        set PYTHON_CMD=C:\Python39\python.exe
    ) else if exist "C:\Python311\python.exe" (
        set PYTHON_CMD=C:\Python311\python.exe
    ) else (
        echo ERROR: No se encontro Python.
        echo Por favor, ejecuta el comando manualmente con la ruta completa:
        echo C:\python3.10\python.exe -m PyInstaller build_exe.spec
        pause
        exit /b 1
    )
)

echo Usando Python: %PYTHON_CMD%
echo.

REM Instalar dependencias si es necesario
echo Verificando dependencias...
%PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias.
    pause
    exit /b 1
)

echo.
echo Construyendo ejecutable con PyInstaller...
%PYTHON_CMD% -m PyInstaller build_exe.spec
if errorlevel 1 (
    echo ERROR: No se pudo crear el ejecutable. Revisa los mensajes de error arriba.
    pause
    exit /b 1
)

echo.
if exist "dist\BotKathana.exe" (
    echo Ejecutable creado exitosamente en: dist\BotKathana.exe
) else (
    echo ERROR: No se pudo crear el ejecutable. Revisa los mensajes de error arriba.
)
echo.
pause

