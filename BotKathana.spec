# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['gui_main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json', '.'),  # Incluir config.json en la raíz del ejecutable
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'cv2',
        'numpy',
        'pytesseract',
        'mss',
        'win32api',
        'win32con',
        'win32gui',
        'win32process',
        'config_manager',
        'bot_controller',
        'game_window',
        'configuracion',
        'estado_objetivo',
        'hilo_detector_ocr',
        'hilo_habilidades',
        'hilo_autocuracion',
        'hilo_observador_objetivo',
        'hilo_recoger_drop',
        'hilo_mob_trabado',
        'pixel_detector',
        'keyboard_controller',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BotKathana',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin consola (aplicación GUI)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Puedes agregar un icono aquí si tienes uno: 'icono.ico'
)

