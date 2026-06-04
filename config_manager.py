"""
Gestor de configuración para el bot.
Maneja la carga y guardado de configuración desde/hacia JSON.
"""
import json
import os
from typing import Dict, Any, List


CONFIG_JSON_PATH = "config.json"


def cargar_configuracion() -> Dict[str, Any]:
    """
    Carga la configuración desde config.json si existe.
    Si no existe, retorna None.
    
    Returns:
        Diccionario con la configuración o None
    """
    if not os.path.exists(CONFIG_JSON_PATH):
        return None
    
    try:
        with open(CONFIG_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error al cargar configuración: {e}")
        return None


def guardar_configuracion(config: Dict[str, Any]) -> bool:
    """
    Guarda la configuración en config.json.
    
    Args:
        config: Diccionario con la configuración completa
        
    Returns:
        True si se guardó correctamente, False en caso contrario
    """
    try:
        with open(CONFIG_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error al guardar configuración: {e}")
        return False


def obtener_configuracion_completa() -> Dict[str, Any]:
    """
    Obtiene la configuración completa del bot.
    Intenta cargar desde JSON, si no existe usa valores por defecto.
    
    Returns:
        Diccionario con toda la configuración
    """
    # Intentar cargar desde JSON
    config_json = cargar_configuracion()
    if config_json:
        if 'ENV' not in config_json:
            config_json['ENV'] = 'prod'
        if 'MOBS_LOOT' not in config_json:
            config_json['MOBS_LOOT'] = []
        if 'MOBS_TODOS' not in config_json:
            config_json['MOBS_TODOS'] = config_json.get('MOBS_OBJETIVO', [])
        return config_json
    
    # Si no existe, importar valores por defecto desde configuracion.py
    try:
        import configuracion as cfg
        
        return {
            'GAME_WINDOW_TITLE': cfg.GAME_WINDOW_TITLE,
            'ENV': getattr(cfg, 'ENV', 'prod'),
            'EASYOCR_GPU': getattr(cfg, 'EASYOCR_GPU', True),
            'UMBRAL_SIMILITUD': cfg.UMBRAL_SIMILITUD,
            'MOBS_OBJETIVO': cfg.MOBS_OBJETIVO,
            'MOBS_LOOT': getattr(cfg, 'MOBS_LOOT', []),
            'MOBS_TODOS': getattr(cfg, 'MOBS_TODOS', []),
            'LOOT_DROP': cfg.LOOT_DROP,
            'HABILIDADES': cfg.HABILIDADES,
            'AUTOCURACION': cfg.AUTOCURACION,
            'OBSERVADOR_OBJETIVO': cfg.OBSERVADOR_OBJETIVO,
            'ESCAPE_MOB': cfg.ESCAPE_MOB,
            'ESCAPE_BY_MOB': cfg.ESCAPE_BY_MOB,
        }
    except Exception as e:
        print(f"Error al cargar configuración por defecto: {e}")
        return {}


def aplicar_configuracion_a_modulo(config: Dict[str, Any]) -> None:
    """
    Aplica la configuración al módulo configuracion.py.
    Esto permite que el código existente siga funcionando.
    
    Args:
        config: Diccionario con la configuración
    """
    import configuracion as cfg
    
    if 'GAME_WINDOW_TITLE' in config:
        cfg.GAME_WINDOW_TITLE = config['GAME_WINDOW_TITLE']
    if 'ENV' in config:
        cfg.ENV = config['ENV']
    if 'EASYOCR_GPU' in config:
        cfg.EASYOCR_GPU = config['EASYOCR_GPU']
    if 'UMBRAL_SIMILITUD' in config:
        cfg.UMBRAL_SIMILITUD = config['UMBRAL_SIMILITUD']
    if 'MOBS_OBJETIVO' in config:
        cfg.MOBS_OBJETIVO = config['MOBS_OBJETIVO']
    if 'MOBS_LOOT' in config:
        cfg.MOBS_LOOT = config['MOBS_LOOT']
    if 'MOBS_TODOS' in config:
        cfg.MOBS_TODOS = config['MOBS_TODOS']
    if 'LOOT_DROP' in config:
        cfg.LOOT_DROP = config['LOOT_DROP']
    if 'HABILIDADES' in config:
        cfg.HABILIDADES = config['HABILIDADES']
    if 'AUTOCURACION' in config:
        cfg.AUTOCURACION = config['AUTOCURACION']
    if 'OBSERVADOR_OBJETIVO' in config:
        cfg.OBSERVADOR_OBJETIVO = config['OBSERVADOR_OBJETIVO']
    if 'ESCAPE_MOB' in config:
        cfg.ESCAPE_MOB = config['ESCAPE_MOB']
    if 'ESCAPE_BY_MOB' in config:
        cfg.ESCAPE_BY_MOB = config['ESCAPE_BY_MOB']

