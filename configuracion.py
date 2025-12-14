"""
Configuración central del bot.
Aquí se definen todos los parámetros configurables.
"""

# ============================================================
# CONFIGURACIÓN DE LA VENTANA DEL JUEGO
# ============================================================
GAME_WINDOW_TITLE = "Kathana - The Coming of the Dark Ages"

# Ruta de Tesseract OCR
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ============================================================
# REGIÓN DE CAPTURA PARA OCR (relativa a la ventana del juego)
# ============================================================
OCR_REGION = {
    "left_offset": 5,     # Margen izquierdo desde la ventana
    "top_offset": 90,     # Margen superior desde la ventana
    "width": 150,         # Ancho de la región a capturar
    "height": 15          # Alto de la región a capturar
}

# Umbral de similitud mínimo para considerar una coincidencia
UMBRAL_SIMILITUD = 0.70

# ============================================================
# LISTA DE MOBS QUE QUIERO MATAR
# Agrega aquí los nombres de los mobs que deseas atacar
# ============================================================
MOBS_OBJETIVO = [
    # "Shamukito",
    # "Sobariung (54)",
    # "Sobariung Gosu (56)",
    # "Balastha Drbhika (62)",
    "Aganna Tara (39)",
    "Pizza Aganna (39)",
    "Kaulitara (41)",
    # "Borangi (54)",
    # "Byokbo (56)",
    # # "Ban Gosu (52)",
    # # "Ban (50)",
    "Zinkiu Gosu (58)",
    "Zinkiu (53)",
    
    # # "Zinmon (51)",
    # # "Zinmon Gosu (55)",

    "Mangrian (50)",
    "Kyoin (48)",
    "Ananga (35)",
    # "Ananga Dvanta (37)",

    "Zaku (45)",
    "Zaku Gosu (47)",
    # "Varaha (15)",
    # "Tarantula (30)",
    # "Heruka (31)",
    # "Aprah Varaha Raja (15)",
    # "Srbinda (21)",
    # "Srbinda Satvan (23)",
    # "Saraa Vrca (17)",
    "Ulkamukha (21)",
    "Ulkamukha Caura (23)",
    "Ulkamukha Satvan (25)",
    "Ananga (25)",
    "Visa Curni (27)",
    # "Ugra Ulkamukha Satvan (32)",
    # "Ugra Ulkamukha Caura (30)",
    # "Ugra Ulkamukha (28)",

    # "Zarku (46)",
    # "Zarku Rudhira (48)",

    # Agrega más mobs aquí...
]

# ============================================================
# LISTA DE ITEMS DROP QUE QUIERO RECOGER
# Agrega aquí los nombres de los items que deseas recoger
# ============================================================
DROP_ITEMS_OBJETIVO = [
    # "Poison String",
    # "Pinna",
    # "Spara Panaka",
    # "Spara Amrita",
    # "Rupiah",
    # "Toronja"

    # Agrega más items aquí...
]

# ============================================================
# CONFIGURACIÓN DE LOOT/DROP
# ============================================================
LOOT_DROP = {
    'repeticiones_f': 0,    # Veces que se presionará la tecla F
    'intervalo_f': 0.5,     # Segundos de espera entre cada pulsación
}

# ============================================================
# CONFIGURACIÓN DE HABILIDADES
# - active: True = usar esta habilidad, False = ignorar
# - time: Cooldown en segundos entre cada uso
# ============================================================
HABILIDADES = {
    '1': {'active': False, 'time': 0.2},   # Habilidad 1
    '2': {'active': True,  'time': 0.2},   # Habilidad 2
    '3': {'active': False,  'time': 0.2},   # Habilidad 3
    '4': {'active': True,  'time': 0.2},   # Habilidad 4
    '5': {'active': False,  'time': 2.2},  # Habilidad 5
    '6': {'active': True,  'time': 60.0},  # Habilidad 6
    '7': {'active': True,  'time': 15.0},   # Habilidad 7
    '8': {'active': True, 'time': 40.0},   # Habilidad 8
    'F': {'active': False,  'time': 1.0},   # Tecla F
    'R': {'active': False,  'time': 0.5},   # Tecla F
    # 'S': {'active': True,  'time': 10.0},  # Tecla S
}

# ============================================================
# CONFIGURACIÓN DE AUTOCURACIÓN
# ============================================================
AUTOCURACION = {
    'vida': {
        'x': 128,                # Posición X de la barra de vida
        'y': 62,                 # Posición Y de la barra de vida
        'tecla': ['0','7', '4'],            # Tecla para curar vida
        'intervalo_con': 1.0,    # Intervalo cuando hay vida (segundos)
        'intervalo_sin': 0.5,    # Intervalo cuando no hay vida (segundos)
    },
    'mana': {
        'x': 45,                 # Posición X de la barra de maná
        'y': 80,                 # Posición Y de la barra de maná
        'tecla': '9',            # Tecla para restaurar maná
        'intervalo_con': 1.0,    # Intervalo cuando hay maná (segundos)
        'intervalo_sin': 0.5,    # Intervalo cuando no hay maná (segundos)
    }
}

# ============================================================
# CONFIGURACIÓN DEL OBSERVADOR DE OBJETIVO
# ============================================================
OBSERVADOR_OBJETIVO = {
    'timeout_drop': 3.0,         # Segundos antes de presionar E en estado DROP
    'intervalo_revision': 0.1,   # Intervalo de revisión del estado (segundos)
}

# ============================================================
# CONFIGURACIÓN DE ESCAPE (MOB TRABADO)
# Si un mob lleva más de X segundos, hacer clic para escapar
# Alterna entre los puntos cada vez que se ejecuta
# ============================================================
ESCAPE_MOB = {
    'pjname': "Toronja",
    'timeout_mob': 20.0,         # Segundos antes de considerar que el mob está trabado
    'punto_click_primero': {'x': 405, 'y': 360},
    'puntos_clic': [
        {'x': 790, 'y': 60},     # Punto 1 - Primera vez que se trabe
        {'x': 790, 'y': 500},    # Punto 4 - Segunda vez que se trabe (cambia estas coordenadas)
        {'x': 220, 'y': 40},    # Punto 2 - Segunda vez que se trabe (cambia estas coordenadas)
        {'x': 40, 'y': 450},     # Punto 3 - Segunda vez que se trabe (cambia estas coordenadas)
    ],
    'veces': 3,                  # Veces que se hace clic en el punto
    'duracion_total': 3.0,       # Duración total de la secuencia de escape (segundos)
}

ESCAPE_BY_MOB = {
    # "Zinkiu Gosu (58)": 25.0,
    # "Zinkiu (53)": 20.0,
    # "Mangrian (50)": 15.0,
    # "Kyoin (48)": 10.0,
    # "Borangi (54)": 10.0,
    # "Byokbo (56)": 10.0,
    # "Ananga (35)": 10.0,
    # "Ananga Dvanta (37)": 15.0,
    # "Aganna Tara (39)": 13.0,
    # "Pizza Aganna (39)": 13.0,
    # "Kaulitara (41)": 13.0,
}


# ============================================================
# CÓDIGOS DE TECLAS VIRTUALES (Windows)
# ============================================================
VK_CODES = {
    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
    '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
    'E': 0x45, 'R': 0x52, 'F': 0x46, 'S': 0x53,
}

