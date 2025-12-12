"""
Módulo para detectar colores en píxeles de la pantalla.
Responsabilidad: Captura y análisis de colores (Single Responsibility Principle)
"""
import ctypes
from typing import Tuple
from game_window import GameWindow


class PixelDetector:
    """
    Clase para detectar colores de píxeles en la ventana del juego.
    """
    
    def __init__(self, game_window: GameWindow):
        """
        Inicializa el detector de píxeles.
        
        Args:
            game_window: Instancia de GameWindow
        """
        self.game_window = game_window
        self.user32 = ctypes.windll.user32
        self.gdi32 = ctypes.windll.gdi32
    
    def get_pixel_color(self, x_relative: int, y_relative: int) -> Tuple[int, int, int]:
        """
        Obtiene el color RGB de un píxel en coordenadas relativas a la ventana.
        
        Args:
            x_relative: Coordenada X relativa a la ventana
            y_relative: Coordenada Y relativa a la ventana
            
        Returns:
            Tupla (R, G, B) con los valores de color
        """
        # Obtener posición de la ventana
        rect = self.game_window.get_window_rect()
        
        # Calcular coordenadas absolutas
        x_absolute = rect.left + x_relative
        y_absolute = rect.top + y_relative
        
        # Obtener contexto de dispositivo
        hdc = self.user32.GetDC(0)
        
        # Obtener color del píxel (formato BGR en Windows)
        color = self.gdi32.GetPixel(hdc, x_absolute, y_absolute)
        
        # Liberar contexto
        self.user32.ReleaseDC(0, hdc)
        
        # Convertir de BGR a RGB
        r = color & 0xFF
        g = (color >> 8) & 0xFF
        b = (color >> 16) & 0xFF
        
        return r, g, b
    
    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int) -> str:
        """
        Convierte valores RGB a formato hexadecimal.
        
        Args:
            r: Componente rojo (0-255)
            g: Componente verde (0-255)
            b: Componente azul (0-255)
            
        Returns:
            String en formato hexadecimal (#RRGGBB)
        """
        return f"#{r:02X}{g:02X}{b:02X}"
    
    @staticmethod
    def colors_similar(color1: Tuple[int, int, int], 
                       color2: Tuple[int, int, int], 
                       tolerance: int = 10) -> bool:
        """
        Verifica si dos colores RGB son similares dentro de una tolerancia.
        
        Args:
            color1: Primera tupla RGB
            color2: Segunda tupla RGB
            tolerance: Tolerancia permitida por componente
            
        Returns:
            True si los colores son similares, False en caso contrario
        """
        r1, g1, b1 = color1
        r2, g2, b2 = color2
        
        return (abs(r1 - r2) <= tolerance and 
                abs(g1 - g2) <= tolerance and 
                abs(b1 - b2) <= tolerance)
