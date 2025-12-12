"""
Módulo para enviar comandos de teclado a la ventana del juego.
Responsabilidad: Simulación de entrada de teclado (Single Responsibility Principle)
"""
import ctypes
import time
from game_window import GameWindow


class KeyboardController:
    """
    Clase para enviar comandos de teclado a la ventana del juego.
    Usa PostMessage para enviar teclas a una ventana específica.
    """
    
    # Constantes de Windows para mensajes de teclado
    WM_KEYDOWN = 0x0100
    WM_KEYUP = 0x0101
    
    # Códigos virtuales de teclas
    VK_CODES = {
        '0': 0x30,
        '1': 0x31,
        '2': 0x32,
        '3': 0x33,
        '4': 0x34,
        '5': 0x35,
        '6': 0x36,
        '7': 0x37,
        '8': 0x38,
        '9': 0x39,
    }
    
    def __init__(self, game_window: GameWindow):
        """
        Inicializa el controlador de teclado.
        
        Args:
            game_window: Instancia de GameWindow
        """
        self.game_window = game_window
        self.user32 = ctypes.windll.user32
    
    def press_key(self, key: str, delay: float = 0.05) -> None:
        """
        Envía la pulsación de una tecla a la ventana del juego.
        
        Args:
            key: Tecla a presionar (string)
            delay: Tiempo de espera entre presionar y soltar (segundos)
            
        Raises:
            ValueError: Si la tecla no está soportada
        """
        if key not in self.VK_CODES:
            raise ValueError(f"Tecla '{key}' no soportada. Teclas válidas: {list(self.VK_CODES.keys())}")
        
        vk_code = self.VK_CODES[key]
        hwnd = self.game_window.hwnd
        
        # Enviar tecla presionada
        self.user32.PostMessageW(hwnd, self.WM_KEYDOWN, vk_code, 0)
        time.sleep(delay)
        # Enviar tecla liberada
        self.user32.PostMessageW(hwnd, self.WM_KEYUP, vk_code, 0)
