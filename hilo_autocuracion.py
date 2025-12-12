"""
Hilo 3: Autocuración
Monitorea la vida y el maná del personaje.
Presiona las teclas de curación cuando están bajos.
Se pausa cuando el estado indica que los hilos deben detenerse.
"""
import ctypes
import time
import threading
from typing import Tuple, List

from estado_objetivo import estado, TipoObjetivo
from configuracion import AUTOCURACION, VK_CODES

# Cargar DLL de Windows
user32 = ctypes.windll.user32


class RECT(ctypes.Structure):
    """Estructura para representar un rectángulo en Windows."""
    _fields_ = [
        ('left', ctypes.c_long),
        ('top', ctypes.c_long),
        ('right', ctypes.c_long),
        ('bottom', ctypes.c_long)
    ]


# Constantes para mensajes de teclado
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101


# Colores válidos para vida (rojos)
COLORES_VIDA = [
    (255, 0, 0), (254, 0, 0), (253, 0, 0), (252, 0, 0), (251, 0, 0), (250, 0, 0),
    (255, 1, 0), (255, 2, 0), (254, 1, 0), (253, 1, 0), (252, 1, 0),
    (200, 0, 0), (180, 0, 0), (160, 0, 0), (140, 0, 0), (120, 0, 0), (100, 0, 0),
    (255, 50, 0), (255, 40, 0), (255, 30, 0), (255, 20, 0), (255, 10, 0),
    (80, 0, 0), (60, 0, 0),
]

# Colores válidos para maná (azules de la barra del juego)
COLORES_MANA = [
    # Azules brillantes puros (parte clara de la barra)
    (0, 0, 255), (0, 0, 254), (0, 0, 253), (0, 0, 252), (0, 0, 251), (0, 0, 250),
    (10, 10, 255), (20, 20, 255), (30, 30, 255), (40, 40, 255), (50, 50, 255),
    (60, 60, 255), (70, 70, 255), (80, 80, 255), (90, 90, 255), (100, 100, 255),
    
    # Azules medios (gradiente de la barra)
    (0, 0, 240), (0, 0, 230), (0, 0, 220), (0, 0, 210), (0, 0, 200),
    (10, 10, 240), (20, 20, 230), (30, 30, 220), (40, 40, 210), (50, 50, 200),
    (0, 0, 190), (0, 0, 180), (0, 0, 170), (0, 0, 160), (0, 0, 150),
    
    # Azules oscuros (parte oscura de la barra)
    (0, 0, 140), (0, 0, 130), (0, 0, 120), (0, 0, 110), (0, 0, 100),
    (10, 10, 140), (20, 20, 130), (30, 30, 120), (40, 40, 110), (50, 50, 100),
    (0, 0, 90), (0, 0, 80), (0, 0, 70), (0, 0, 60), (0, 0, 50),
    
    # Azules muy oscuros (borde de la barra)
    (0, 0, 40), (0, 0, 30), (0, 0, 20), (10, 10, 40), (20, 20, 30),
    
    # Azules con algo de verde (variaciones de la barra)
    (0, 20, 255), (0, 40, 255), (0, 60, 255), (0, 80, 255), (0, 100, 255),
    (0, 20, 200), (0, 40, 200), (0, 60, 200), (0, 80, 200),
    (0, 20, 150), (0, 40, 150), (0, 60, 150),
    
    # Azules con algo de rojo (posibles reflejos)
    (20, 0, 255), (40, 0, 255), (60, 0, 255), (80, 0, 255),
    (20, 0, 200), (40, 0, 200), (60, 0, 200),
    (20, 0, 150), (40, 0, 150),
    
    # Azules mixtos (R, G bajos, B alto)
    (30, 40, 255), (40, 50, 240), (50, 60, 220), (60, 70, 200),
    (30, 40, 180), (40, 50, 160), (50, 60, 140),
]


class HiloAutocuracion:
    """
    Hilo que monitorea vida y maná.
    Presiona teclas de curación cuando están bajos.
    """
    
    def __init__(self, hwnd: int):
        """
        Inicializa el monitor de autocuración.
        
        Args:
            hwnd: Handle de la ventana del juego
        """
        self.hwnd = hwnd
        self.ejecutando = False
        self.thread_vida = None
        self.thread_mana = None
        self.gdi32 = ctypes.windll.gdi32
    
    def _obtener_rect_ventana(self) -> RECT:
        """Obtiene las coordenadas de la ventana."""
        rect = RECT()
        user32.GetWindowRect(self.hwnd, ctypes.byref(rect))
        return rect
    
    def _obtener_color_pixel(self, x_relativo: int, y_relativo: int) -> Tuple[int, int, int]:
        """
        Obtiene el color RGB de un píxel en coordenadas relativas a la ventana.
        
        Args:
            x_relativo: Coordenada X relativa a la ventana
            y_relativo: Coordenada Y relativa a la ventana
            
        Returns:
            Tupla (R, G, B)
        """
        rect = self._obtener_rect_ventana()
        x_absoluto = rect.left + x_relativo
        y_absoluto = rect.top + y_relativo
        
        hdc = user32.GetDC(0)
        color = self.gdi32.GetPixel(hdc, x_absoluto, y_absoluto)
        user32.ReleaseDC(0, hdc)
        
        r = color & 0xFF
        g = (color >> 8) & 0xFF
        b = (color >> 16) & 0xFF
        
        return r, g, b
    
    def _colores_similares(self, color1: Tuple[int, int, int], 
                          color2: Tuple[int, int, int], 
                          tolerancia: int = 15) -> bool:
        """Verifica si dos colores son similares."""
        r1, g1, b1 = color1
        r2, g2, b2 = color2
        return (abs(r1 - r2) <= tolerancia and 
                abs(g1 - g2) <= tolerancia and 
                abs(b1 - b2) <= tolerancia)
    
    def _presionar_tecla(self, tecla: str) -> None:
        """Presiona una tecla en la ventana del juego."""
        if tecla not in VK_CODES:
            return
        
        vk_code = VK_CODES[tecla]
        user32.PostMessageW(self.hwnd, WM_KEYDOWN, vk_code, 0)
        time.sleep(0.05)
        user32.PostMessageW(self.hwnd, WM_KEYUP, vk_code, 0)
    
    def _tiene_vida(self, x: int, y: int) -> Tuple[bool, Tuple[int, int, int]]:
        """
        Verifica si hay vida en la posición indicada.
        
        Returns:
            Tupla (tiene_vida, color_detectado)
        """
        color = self._obtener_color_pixel(x, y)
        r, g, b = color
        
        # Verificar contra colores conocidos
        for color_vida in COLORES_VIDA:
            if self._colores_similares(color, color_vida):
                return True, color
        
        # Verificar si el rojo es dominante
        if r > 50 and r > (g + 30) and r > (b + 30):
            return True, color
        
        return False, color
    
    def _tiene_mana(self, x: int, y: int) -> Tuple[bool, Tuple[int, int, int]]:
        """
        Verifica si hay maná en la posición indicada.
        Detecta azules de la barra de maná del juego.
        
        Returns:
            Tupla (tiene_mana, color_detectado)
        """
        color = self._obtener_color_pixel(x, y)
        r, g, b = color
        
        # Verificar contra colores conocidos
        for color_mana in COLORES_MANA:
            if self._colores_similares(color, color_mana):
                return True, color
        
        # REGLA PRINCIPAL: El azul es el componente dominante
        # La barra de maná tiene B mucho mayor que R y G
        if b > 50:
            # Si el azul es significativamente mayor que rojo y verde
            if b > r and b > g:
                # Y la diferencia es notable (al menos 20 puntos más que el mayor de R,G)
                max_rg = max(r, g)
                if b > (max_rg + 20):
                    return True, color
        
        # REGLA SECUNDARIA: Azul alto aunque R y G también tengan algo
        # Para azules como (50, 50, 200) o (80, 80, 255)
        if b >= 100 and b >= r and b >= g:
            # El azul debe ser al menos 1.5 veces el promedio de R y G
            promedio_rg = (r + g) / 2
            if promedio_rg == 0 or b >= (promedio_rg * 1.5):
                return True, color
        
        return False, color
    
    def _ciclo_vida(self) -> None:
        """Ciclo de monitoreo de vida."""
        print("[AUTOCURACIÓN] Hilo de vida iniciado")
        config = AUTOCURACION['vida']
        contador = 0
        
        while self.ejecutando:
            # Verificar si este hilo está activo
            if not estado.hilo_activo('autocuracion'):
                time.sleep(0.1)
                continue
            
            tiene_vida, color = self._tiene_vida(config['x'], config['y'])
            contador += 1
            
            if tiene_vida:
                time.sleep(config['intervalo_con'])
            else:
                print(f"[VIDA] Sin vida | Color: RGB{color} | Presionando '{config['tecla']}'")
                for tecla in config['tecla']:
                    if estado.tipo != TipoObjetivo.MOB and tecla != '0':
                        continue
                    self._presionar_tecla(tecla)
                time.sleep(config['intervalo_sin'])
        
        print("[AUTOCURACIÓN] Hilo de vida detenido")
    
    def _ciclo_mana(self) -> None:
        """Ciclo de monitoreo de maná."""
        print("[AUTOCURACIÓN] Hilo de maná iniciado")
        config = AUTOCURACION['mana']
        contador = 0
        
        while self.ejecutando:
            # Verificar si este hilo está activo
            if not estado.hilo_activo('autocuracion'):
                time.sleep(0.1)
                continue
            
            tiene_mana, color = self._tiene_mana(config['x'], config['y'])
            contador += 1
            
            if tiene_mana:
                time.sleep(config['intervalo_con'])
            else:
                print(f"[MANÁ] Sin maná | Color: RGB{color} | Presionando '{config['tecla']}'")
                self._presionar_tecla(config['tecla'])
                time.sleep(config['intervalo_sin'])
        
        print("[AUTOCURACIÓN] Hilo de maná detenido")
    
    def iniciar(self) -> None:
        """Inicia los hilos de autocuración."""
        if self.ejecutando:
            return
        
        self.ejecutando = True
        
        # Hilo para vida
        self.thread_vida = threading.Thread(target=self._ciclo_vida, daemon=True)
        self.thread_vida.start()
        
        # Hilo para maná
        self.thread_mana = threading.Thread(target=self._ciclo_mana, daemon=True)
        self.thread_mana.start()
    
    def detener(self) -> None:
        """Detiene los hilos de autocuración."""
        self.ejecutando = False
        if self.thread_vida:
            self.thread_vida.join(timeout=2)
        if self.thread_mana:
            self.thread_mana.join(timeout=2)
    
    def mostrar_configuracion(self) -> None:
        """Muestra la configuración actual de autocuración."""
        print("\n[CONFIGURACIÓN DE AUTOCURACIÓN]")
        print("-" * 50)
        for recurso, config in AUTOCURACION.items():
            print(f"  {recurso.upper()}:")
            print(f"    Posición: ({config['x']}, {config['y']})")
            print(f"    Tecla: '{config['tecla']}'")
            print(f"    Intervalo con recurso: {config['intervalo_con']}s")
            print(f"    Intervalo sin recurso: {config['intervalo_sin']}s")
        print("-" * 50)


# ============================================================
# PRUEBA INDEPENDIENTE
# ============================================================
if __name__ == "__main__":
    from game_window import GameWindow
    from configuracion import GAME_WINDOW_TITLE
    
    try:
        print("=" * 60)
        print("PRUEBA DEL HILO DE AUTOCURACIÓN")
        print("=" * 60)
        
        # Buscar ventana
        print("\n[INFO] Buscando ventana del juego...")
        game_window = GameWindow(GAME_WINDOW_TITLE)
        print(f"[OK] Ventana encontrada (Handle: {game_window.hwnd})")
        
        # Crear e iniciar hilo
        hilo = HiloAutocuracion(game_window.hwnd)
        hilo.mostrar_configuracion()
        
        print("\n[INFO] Iniciando hilos de autocuración...")
        print("[INFO] Presiona Ctrl+C para detener")
        print("-" * 60)
        
        hilo.iniciar()
        
        # Mantener corriendo
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n[INFO] Hilos detenidos por el usuario")
        hilo.detener()
        print("[OK] Script finalizado")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
