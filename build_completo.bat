@echo off
echo ========================================
echo Bot Kathana - Generador de Ejecutable
echo (Version Completa con todas las librerias)
echo ========================================
echo.

REM Detectar Python
set PYTHON_CMD=python
where python >nul 2>&1
if errorlevel 1 (
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
        echo Por favor, especifica la ruta completa de Python.
        pause
        exit /b 1
    )
)

echo Usando Python: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

echo [PASO 1/4] Instalando/Actualizando dependencias...
%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias.
    pause
    exit /b 1
)

echo.
echo [PASO 2/4] Limpiando builds anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "BotKathana.spec" del /q "BotKathana.spec"

echo.
echo [PASO 3/4] Construyendo ejecutable con PyInstaller...
echo Esto puede tardar varios minutos...
echo.

%PYTHON_CMD% -m PyInstaller ^
    --name=BotKathana ^
    --onefile ^
    --windowed ^
    --noconsole ^
    --clean ^
    --noupx ^
    --add-data "config.json;." ^
    --hidden-import=PyQt5.QtCore ^
    --hidden-import=PyQt5.QtGui ^
    --hidden-import=PyQt5.QtWidgets ^
    --hidden-import=config_manager ^
    --hidden-import=bot_controller ^
    --hidden-import=configuracion ^
    --hidden-import=game_window ^
    --hidden-import=estado_objetivo ^
    --hidden-import=hilo_detector_ocr ^
    --hidden-import=hilo_habilidades ^
    --hidden-import=hilo_autocuracion ^
    --hidden-import=hilo_observador_objetivo ^
    --hidden-import=hilo_recoger_drop ^
    --hidden-import=hilo_mob_trabado ^
    --hidden-import=mss ^
    --hidden-import=PIL ^
    --hidden-import=pytesseract ^
    --hidden-import=win32api ^
    --hidden-import=win32con ^
    --hidden-import=win32gui ^
    --collect-all PyQt5 ^
    --collect-all mss ^
    --collect-all PIL ^
    gui_main.py

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo crear el ejecutable.
    echo Revisa los mensajes de error arriba.
    pause
    exit /b 1
)

echo.
echo [PASO 4/4] Verificando resultado...
if exist "dist\BotKathana.exe" (
    echo.
    echo ========================================
    echo EXITO: Ejecutable creado correctamente!
    echo ========================================
    echo.
    echo Ubicacion: %CD%\dist\BotKathana.exe
    echo Tamaño aproximado: 
    dir "dist\BotKathana.exe" | find "BotKathana.exe"
    echo.
    echo El ejecutable incluye todas las librerias necesarias.
    echo Puedes copiarlo a cualquier computadora con Windows.
    echo.
) else (
    echo ERROR: El ejecutable no se creo.
    echo Revisa los errores arriba.
)

echo.
pause



