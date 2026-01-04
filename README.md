# Bot Kathana - Sistema de Hilos

Bot automatizado para el juego **Kathana - The Coming of the Dark Ages**.
Utiliza múltiples hilos de ejecución trabajando en paralelo.

## 🎯 Características

- **Detección OCR**: Captura pantalla y reconoce objetivos
- **Clasificación automática**: Distingue entre Mobs, Drops y objetivos nulos
- **Habilidades automáticas**: Dispara teclas según configuración
- **Autocuración**: Monitorea vida y maná constantemente
- **Selección inteligente**: Presiona E según el tipo de objetivo

## 📁 Estructura del Proyecto

```
bot/
├── bot.py                      # Script principal - Inicia todos los hilos
├── configuracion.py            # Configuración central del bot
├── estado_objetivo.py          # Singleton del estado del objetivo
├── hilo_detector_ocr.py        # Hilo 1: Detector OCR
├── hilo_habilidades.py         # Hilo 2: Disparador de habilidades
├── hilo_autocuracion.py        # Hilo 3: Monitor de vida y maná
├── hilo_observador_objetivo.py # Hilo 4: Observador de objetivo
├── game_window.py              # Gestor de ventana del juego
├── pixel_detector.py           # Detector de colores de píxeles
├── keyboard_controller.py      # Controlador de teclado
└── README.md                   # Este archivo
```

## 🚀 Uso

### Ejecutar el bot completo:
```bash
python bot.py
```

### Probar hilos individuales:
```bash
python hilo_detector_ocr.py        # Probar solo detector OCR
python hilo_habilidades.py         # Probar solo habilidades
python hilo_autocuracion.py        # Probar solo autocuración
python hilo_observador_objetivo.py # Probar solo observador
```

## ⚙️ Configuración

Toda la configuración está en `configuracion.py`:

### Mobs objetivo
```python
MOBS_OBJETIVO = [
    "Zinmon (51)",
    "Zinmon Gosu (55)",
    "Mangrian (50)",
    "Kyojin (48)",
]
```

### Items drop
```python
DROP_ITEMS_OBJETIVO = [
    "Poison String",
    "Pinna",
    "Spara Panaka",
    "Rupiah",
]
```

### Habilidades
```python
HABILIDADES = {
    '1': {'active': False, 'time': 1.0},
    '2': {'active': True,  'time': 1.0},
    # ...
}
```

### Autocuración
```python
AUTOCURACION = {
    'vida': {
        'x': 128, 'y': 62,
        'tecla': '0',
        'intervalo_con': 1.0,
        'intervalo_sin': 0.5,
    },
    'mana': {
        'x': 75, 'y': 84,
        'tecla': '9',
        'intervalo_con': 1.0,
        'intervalo_sin': 0.5,
    }
}
```

## 🔄 Hilos de Ejecución

### Hilo 1: Detector OCR (`hilo_detector_ocr.py`)
- Captura la región del objetivo en pantalla
- Procesa la imagen con Tesseract OCR
- Clasifica el objetivo:
  - **NULO**: Texto vacío o no reconocido
  - **MOB**: Coincide con la lista de mobs
  - **DROP**: Coincide con la lista de items
- Actualiza el estado global constantemente
- **NUEVO**: Ejecuta secuencia de loot cuando MOB → NULO (mob muere)

### Hilo 2: Habilidades (`hilo_habilidades.py`)
- Observa el estado del objetivo
- Si es **MOB** o **DROP**:
  - Presiona R para atacar (solo MOB)
  - Dispara las habilidades según cooldown
- Respeta los tiempos de cooldown configurados

### Hilo 3: Autocuración (`hilo_autocuracion.py`)
- Monitorea el color de la barra de vida
- Monitorea el color de la barra de maná
- Presiona teclas de curación cuando están bajos
- Dos sub-hilos: uno para vida, otro para maná

### Hilo 4: Observador de Objetivo (`hilo_observador_objetivo.py`)
- Observa constantemente el estado del objetivo
- **NULO** → Presiona E para seleccionar nuevo objetivo
- **MOB** → No hace nada (ya tenemos objetivo)
- **DROP** → Si lleva más de 3 segundos, presiona E

## 🎁 Secuencia de Loot

Cuando un mob muere (transición MOB → NULO), se ejecuta automáticamente:

```
MOB detectado → Combate normal
       │
       ▼ (mob muere, OCR detecta texto vacío)
MOB → NULO detectado
       │
       ▼
┌──────────────────────────────┐
│  PAUSAR TODOS LOS HILOS      │
│  (autocuración, habilidades, │
│   observador pausados)       │
└──────────────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  PRESIONAR F × 3             │
│  (cada 0.33s = 1 segundo)    │
│  Para recoger loot           │
└──────────────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  REACTIVAR TODOS LOS HILOS   │
└──────────────────────────────┘
       │
       ▼
Continuar ciclo normal...
```

## 🏃 Secuencia de Escape (Mob Trabado)

Cuando un mob lleva más de 15 segundos (configurable), se considera "trabado" y se ejecuta:

```
MOB detectado → Combate normal
       │
       ▼ (pasan 15+ segundos con el mismo mob)
MOB TRABADO detectado
       │
       ▼
┌──────────────────────────────┐
│  PAUSAR TODOS LOS HILOS      │
└──────────────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  PRESIONAR S × 3             │
│  (durante 3 segundos)        │
│  Para escapar del mob        │
└──────────────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  REACTIVAR TODOS LOS HILOS   │
└──────────────────────────────┘
       │
       ▼
Continuar ciclo normal...
```

**Nota**: El escape solo se ejecuta una vez por mob. Si el mismo mob sigue apareciendo, no se vuelve a ejecutar hasta que cambie el objetivo.

## 📊 Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────┐
│                     ESTADO OBJETIVO                          │
│                    (Singleton Global)                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  tipo: NULO | MOB | DROP                            │    │
│  │  nombre: str                                        │    │
│  │  timestamp: float                                   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
           ▲                ▲                ▲
           │                │                │
     ┌─────┴─────┐    ┌─────┴─────┐    ┌─────┴─────┐
     │  HILO 1   │    │  HILO 2   │    │  HILO 4   │
     │  OCR      │    │ HABILIDAD │    │ OBSERVADOR│
     │           │    │           │    │           │
     │ Escribe   │    │   Lee     │    │   Lee     │
     └───────────┘    └───────────┘    └───────────┘
                            
           ┌───────────────────────────────┐
           │           HILO 3              │
           │        AUTOCURACIÓN           │
           │  (Independiente del estado)   │
           └───────────────────────────────┘
```

## 📋 Requisitos

- Python 3.7+
- Tesseract OCR instalado
- Bibliotecas Python:
  ```
  pip install pillow mss pytesseract
  ```

### Instalar Tesseract OCR (Windows)
1. Descargar de: https://github.com/UB-Mannheim/tesseract/wiki
2. Instalar en: `C:\Program Files\Tesseract-OCR\`
3. Verificar la ruta en `configuracion.py`

## ⚠️ Notas Importantes

1. El juego debe estar abierto antes de ejecutar el bot
2. El título de la ventana debe coincidir exactamente
3. Ajusta las coordenadas según tu resolución de pantalla
4. Usa Ctrl+C para detener el bot de forma segura

## 📦 Generar Ejecutable (.exe)

Puedes generar un ejecutable standalone para distribuir el bot sin necesidad de tener Python instalado.

### Requisitos previos

1. **Python 3.7+** instalado
2. **Entorno virtual** configurado con todas las dependencias:
   ```bash
   # Crear entorno virtual (si no existe)
   python -m venv venv
   
   # Activar entorno virtual
   # Windows CMD:
   venv\Scripts\activate.bat
   # Windows PowerShell:
   venv\Scripts\Activate.ps1
   
   # Instalar dependencias
   pip install -r requirements.txt
   ```

3. **PyInstaller** instalado (ya incluido en requirements.txt):
   ```bash
   pip install pyinstaller
   ```

### Opción 1: Usar los scripts automáticos (Recomendado)

#### Windows CMD (Símbolo del sistema)
```batch
build_exe.bat
```

#### Windows PowerShell
```powershell
.\build_exe.ps1
```

> **Nota:** Si PowerShell bloquea la ejecución, primero ejecuta:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

Los scripts automáticamente:
- Activan el entorno virtual
- Cierran cualquier instancia de BotKathana.exe en ejecución
- Limpian builds anteriores
- Generan el nuevo ejecutable

### Opción 2: Generar manualmente con PyInstaller

```bash
# Activar entorno virtual primero
venv\Scripts\activate

# Generar ejecutable usando el archivo .spec
pyinstaller BotKathana.spec --clean
```

O sin archivo .spec (genera uno nuevo):
```bash
pyinstaller gui_main.py --onefile --noconsole --name BotKathana --clean
```

### Ubicación del ejecutable

El ejecutable se genera en:
```
dist\BotKathana.exe
```

### Archivos incluidos en el ejecutable

El archivo `BotKathana.spec` configura PyInstaller para incluir:
- `config.json` - Configuración del bot
- Todos los módulos Python del proyecto
- Dependencias de PyQt5, OpenCV, Tesseract, etc.

### Distribución

Para distribuir el bot, necesitas:

1. **BotKathana.exe** - El ejecutable generado
2. **Tesseract OCR** - Debe estar instalado en el sistema destino
   - Descarga: https://github.com/UB-Mannheim/tesseract/wiki
   - Ruta por defecto: `C:\Program Files\Tesseract-OCR\tesseract.exe`

### Personalización del ejecutable

Puedes modificar `BotKathana.spec` para:

- **Agregar un icono:**
  ```python
  icon='ruta/a/tu/icono.ico',
  ```

- **Mostrar consola** (útil para debug):
  ```python
  console=True,
  ```

- **Incluir archivos adicionales:**
  ```python
  datas=[
      ('config.json', '.'),
      ('otro_archivo.txt', '.'),
  ],
  ```

### Solución de problemas al generar

| Problema | Solución |
|----------|----------|
| "El archivo está en uso" | Cierra BotKathana.exe y vuelve a intentar |
| "ModuleNotFoundError" | Agrega el módulo a `hiddenimports` en el .spec |
| "No se encuentra pyinstaller" | Ejecuta `pip install pyinstaller` |
| Ejecutable muy grande | Normal (~50-100MB por incluir PyQt5 y OpenCV) |
| Antivirus bloquea | Agrega excepción o firma el ejecutable |

---

## 🛠️ Solución de Problemas

### "No se encontró la ventana"
- Verifica que el juego esté abierto
- Verifica el título exacto de la ventana en `configuracion.py`

### OCR no reconoce texto
- Ajusta la región de captura en `configuracion.py`
- Ajusta el umbral de similitud (`UMBRAL_SIMILITUD`)

### Habilidades no se disparan
- Verifica que las habilidades estén en `active: True`
- Verifica los tiempos de cooldown

### Autocuración no funciona
- Ajusta las coordenadas de las barras de vida/maná
- Verifica los colores en las listas de colores válidos

