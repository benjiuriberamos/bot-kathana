@echo off
echo ========================================
echo Bot Kathana - Generador de Ejecutable
echo ========================================
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
%PYTHON_CMD% --version
echo.

echo [1/3] Instalando dependencias...
%PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias.
    pause
    exit /b 1
)

echo.
echo [2/3] Construyendo ejecutable...
%PYTHON_CMD% -m PyInstaller build_exe.spec
if errorlevel 1 (
    echo ERROR: No se pudo crear el ejecutable.
    pause
    exit /b 1
)

echo.
echo [3/3] Verificando resultado...
if exist "dist\BotKathana.exe" (
    echo.
    echo ========================================
    echo EXITO: Ejecutable creado correctamente!
    echo ========================================
    echo.
    echo Ubicacion: %CD%\dist\BotKathana.exe
    echo.
) else (
    echo ERROR: El ejecutable no se creo. Revisa los errores arriba.
)

echo.
pause

