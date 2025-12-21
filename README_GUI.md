# Bot Kathana - Interfaz Gráfica

## Descripción

Interfaz gráfica de escritorio para configurar y controlar el Bot Kathana. Permite configurar todos los parámetros del bot mediante una interfaz visual organizada en pestañas.

## Instalación

1. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

### Ejecutar la interfaz gráfica

```bash
python gui_main.py
```

### Configuración

La interfaz está organizada en las siguientes pestañas:

1. **General**: Configuración básica (ventana del juego, Tesseract, región OCR, umbral)
2. **Mobs Objetivo**: Lista de mobs a atacar (agregar/eliminar)
3. **Items Drop**: Lista de items a recoger (agregar/eliminar)
4. **Loot/Drop**: Configuración de loot (repeticiones F, intervalo)
5. **Habilidades**: Configuración de habilidades (activar/desactivar, cooldowns)
6. **Autocuración**: Configuración de vida y maná (posiciones, teclas, intervalos)
7. **Observador**: Configuración del observador de objetivo
8. **Escape**: Configuración de escape cuando el mob está trabado

### Carga Inicial de Configuración

Al iniciar la aplicación:
- Si existe `config.json`, se cargan los valores desde ese archivo y se muestran en la interfaz
- Si no existe `config.json`, se usan los valores por defecto del módulo `configuracion.py`

### Modificar Configuración

1. Puedes modificar cualquier parámetro en las pestañas de la interfaz
2. Los cambios se reflejan inmediatamente en la interfaz
3. **No es necesario guardar** antes de iniciar el bot

### Guardar Configuración (Opcional)

El botón "Guardar Configuración" es opcional y permite:
- Guardar la configuración actual de la interfaz en `config.json`
- Útil para mantener una configuración persistente entre sesiones
- La próxima vez que inicies la aplicación, se cargarán estos valores

### Iniciar/Detener el Bot

1. Configurar todos los parámetros necesarios en las pestañas
2. Hacer clic en "RUN" para iniciar el bot
   - **El bot usará automáticamente los valores actuales de la interfaz** (no necesita guardar primero)
   - Los valores se aplican directamente al módulo de configuración
3. El botón cambiará a "STOP" cuando esté ejecutándose
4. Hacer clic en "STOP" para detener el bot

**Nota importante**: Al presionar "RUN", el bot siempre usa los valores que están actualmente en la interfaz, independientemente de si has guardado o no en `config.json`.

### Estado del Bot

En la parte superior de la ventana se muestra:
- Estado del bot (Detenido/Ejecutando)
- Información del objetivo actual (tipo, nombre, tiempo, similitud)

## Generar Ejecutable

### Opción 1: Usar el script batch (Windows)

```bash
build.bat
```

### Opción 2: Usar PyInstaller directamente

```bash
pyinstaller build_exe.spec
```

El ejecutable se generará en la carpeta `dist/BotKathana.exe`

### Notas sobre el ejecutable

- El ejecutable no requiere Python instalado
- Se incluyen todas las dependencias necesarias
- El archivo `config.json` se creará en el mismo directorio que el ejecutable
- Asegúrate de tener Tesseract OCR instalado en el sistema

## Estructura de Archivos

- `gui_main.py`: Interfaz gráfica principal
- `config_manager.py`: Gestor de configuración (carga/guardado desde/hacia JSON)
- `bot_controller.py`: Controlador del bot
- `configuracion.py`: Módulo de configuración (se actualiza dinámicamente desde la interfaz)
- `build_exe.spec`: Especificación de PyInstaller
- `build.bat`: Script para generar el ejecutable
- `config.json`: Archivo de configuración inicial (opcional, se usa para cargar valores al iniciar la aplicación)

## Solución de Problemas

### Error al iniciar el bot

- Verifica que el juego esté abierto
- Verifica que el título de la ventana sea correcto
- Verifica que Tesseract OCR esté instalado y la ruta sea correcta

### La configuración no se guarda

- Verifica que tengas permisos de escritura en el directorio
- Verifica que no haya errores en los campos (valores inválidos)

### El ejecutable no funciona

- Asegúrate de tener todas las DLLs necesarias
- Verifica que Tesseract OCR esté instalado en el sistema
- Ejecuta desde la línea de comandos para ver errores

