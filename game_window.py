"""
Módulo para gestionar la ventana del juego.
Responsabilidad: Encontrar y gestionar la ventana del juego (Single Responsibility Principle)
"""
import ctypes
from ctypes import wintypes


class RECT(ctypes.Structure):
    """Estructura para representar un rectángulo en Windows."""
    _fields_ = [
        ('left', ctypes.c_long),
        ('top', ctypes.c_long),
        ('right', ctypes.c_long),
        ('bottom', ctypes.c_long)
    ]


class GameWindow:
    """
    Clase para gestionar la ventana del juego.
    Encapsula toda la lógica relacionada con la ventana.
    """
    
    def __init__(self, window_title: str):
        """
        Inicializa el gestor de ventana.
        
        Args:
            window_title: Título de la ventana del juego
        """
        self.window_title = window_title
        self.user32 = ctypes.windll.user32
        self._hwnd = None
    
    @property
    def hwnd(self) -> int:
        """Obtiene el handle de la ventana."""
        if self._hwnd is None:
            self._hwnd = self._find_window()
        return self._hwnd
    
    def _find_window(self) -> int:
        """
        Busca la ventana del juego por su título.
        
        Returns:
            Handle de la ventana
            
        Raises:
            Exception: Si no se encuentra la ventana
        """
        hwnd = self.user32.FindWindowW(None, self.window_title)
        if hwnd == 0:
            raise Exception(f"No se encontró la ventana con título: {self.window_title}")
        return hwnd
    
    def get_window_rect(self) -> RECT:
        """
        Obtiene las coordenadas de la ventana.
        
        Returns:
            Estructura RECT con las coordenadas
        """
        rect = RECT()
        self.user32.GetWindowRect(self.hwnd, ctypes.byref(rect))
        return rect
    
    def is_valid(self) -> bool:
        """
        Verifica si la ventana sigue siendo válida.
        
        Returns:
            True si la ventana existe, False en caso contrario
        """
        return self.user32.IsWindow(self.hwnd) != 0
