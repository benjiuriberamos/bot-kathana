"""
Hilo: Control de Área
Monitorea las coordenadas del personaje y evita que salga del polígono configurado.
Si el personaje está fuera del área:
- Pausa todos los hilos excepto autocuración y este mismo
- Presiona las teclas necesarias para regresar al área

Controles invertidos (cámara rotada con ruedita del mouse):
- W → Sur
- S → Norte  
- A → Este
- D → Oeste
"""
import ctypes
import time
import threading
import mss
import cv2
import numpy as np
import pytesseract
import re
from shapely.geometry import Point, Polygon

from estado_objetivo import estado
from configuracion import VK_CODES

# Configurar Tesseract (se actualizará dinámicamente)
def _configurar_tesseract():
    """Configura Tesseract con la ruta actual del módulo."""
    import configuracion
    pytesseract.pytesseract.tesseract_cmd = configuracion.TESSERACT_PATH

_configurar_tesseract()

# Constantes para mensajes de teclado
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101

# Constantes para SendInput
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008

user32 = ctypes.windll.user32


class KEYBDINPUT(ctypes.Structure):
    """Estructura para entrada de teclado con SendInput."""
    _fields_ = [
        ('wVk', ctypes.c_ushort),
        ('wScan', ctypes.c_ushort),
        ('dwFlags', ctypes.c_ulong),
        ('time', ctypes.c_ulong),
        ('dwExtraInfo', ctypes.POINTER(ctypes.c_ulong))
    ]


class INPUT(ctypes.Structure):
    """Estructura INPUT para SendInput."""
    _fields_ = [
        ('type', ctypes.c_ulong),
        ('ki', KEYBDINPUT),
        ('padding', ctypes.c_ubyte * 8)
    ]


# Mapeo de teclas a scan codes (más compatible con juegos)
SCAN_CODES = {
    'W': 0x11,
    'A': 0x1E,
    'S': 0x1F,
    'D': 0x20,
}


class RECT(ctypes.Structure):
    """Estructura para representar un rectángulo en Windows."""
    _fields_ = [
        ('left', ctypes.c_long),
        ('top', ctypes.c_long),
        ('right', ctypes.c_long),
        ('bottom', ctypes.c_long)
    ]


def _obtener_altura_barra_titulo() -> int:
    """Obtiene la altura de la barra de título según el DPI del sistema."""
    SM_CYCAPTION = 4
    SM_CYFRAME = 33
    SM_CXPADDEDBORDER = 92
    
    altura_caption = user32.GetSystemMetrics(SM_CYCAPTION)
    altura_frame = user32.GetSystemMetrics(SM_CYFRAME)
    padding = user32.GetSystemMetrics(SM_CXPADDEDBORDER)
    
    return altura_caption + altura_frame + padding


# ============================================================
# CONSTANTES FIJAS DE LA REGIÓN DE COORDENADAS DEL MINIMAPA
# El minimapa siempre tiene el mismo tamaño y posición (anclado arriba-derecha)
# ============================================================
COORDS_RIGHT_OFFSET = 122     # Píxeles desde el borde derecho de la ventana
COORDS_TOP_OFFSET = 163      # Píxeles desde el contenido del juego (sin barra título)
COORDS_WIDTH = 59            # Ancho del área de coordenadas
COORDS_HEIGHT = 13           # Alto del área de coordenadas


class HiloControlArea:
    """
    Hilo que monitorea la posición del personaje y lo mantiene dentro del área configurada.
    
    El minimapa está anclado a la esquina superior derecha de la ventana.
    Las coordenadas aparecen debajo del minimapa en formato "X / Y".
    """
    
    def __init__(self, hwnd: int):
        """
        Args:
            hwnd: Handle de la ventana del juego
        """
        self.hwnd = hwnd
        self.ejecutando = False
        self.thread = None
        self.fuera_de_area = False
        self.altura_barra_titulo = _obtener_altura_barra_titulo()
        
        # Estado para evitar oscilación
        self.objetivo_fijo = None       # Punto objetivo fijado al salir del área
        self.ultima_tecla = None        # Última tecla presionada
        self.contador_misma_tecla = 0   # Contador para mantener dirección
        
        # Validación de lecturas OCR
        self.ultima_pos_valida = None   # (x, y) última posición válida
        self.tecla_movimiento = None    # Última tecla de movimiento presionada
    
    def _obtener_rect_ventana(self) -> RECT:
        """Obtiene las coordenadas de la ventana."""
        rect = RECT()
        user32.GetWindowRect(self.hwnd, ctypes.byref(rect))
        return rect
    
    def _capturar_region_coordenadas(self) -> np.ndarray:
        """
        Captura la región donde aparecen las coordenadas X, Y.
        La posición se calcula desde la esquina superior DERECHA de la ventana
        porque el minimapa está anclado ahí y no cambia de tamaño.
        
        Las constantes son fijas porque el minimapa nunca cambia de tamaño.
        """
        rect = self._obtener_rect_ventana()
        ancho_ventana = rect.right - rect.left
        
        # Calcular left desde la derecha (constantes fijas)
        left = rect.left + ancho_ventana - COORDS_RIGHT_OFFSET - COORDS_WIDTH
        
        region = {
            "left": left,
            "top": rect.top + self.altura_barra_titulo + COORDS_TOP_OFFSET,
            "width": COORDS_WIDTH,
            "height": COORDS_HEIGHT
        }
        
        with mss.mss() as sct:
            screenshot = sct.grab(region)
            return np.array(screenshot)
    
    def _procesar_imagen_ocr(self, imagen: np.ndarray) -> np.ndarray:
        """
        Preprocesa la imagen para OCR - optimizado para texto BLANCO del minimapa.
        Mantiene el texto blanco sobre fondo negro.
        """
        # Convertir BGRA a escala de grises
        gris = cv2.cvtColor(imagen, cv2.COLOR_BGRA2GRAY)
        
        # Escalar 5x para mejor lectura de texto pequeño
        escalada = cv2.resize(gris, None, fx=5, fy=5, interpolation=cv2.INTER_LINEAR)
        
        # Umbral fijo para capturar texto blanco brillante (190 reduce ruido)
        # Texto BLANCO sobre fondo NEGRO
        _, binaria = cv2.threshold(escalada, 190, 255, cv2.THRESH_BINARY)
        
        # Agregar borde negro alrededor para mejor detección
        binaria = cv2.copyMakeBorder(binaria, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=0)
        
        return binaria
    
    def _extraer_coordenadas(self, imagen: np.ndarray) -> tuple:
        """
        Extrae las coordenadas X, Y del texto OCR.
        Formato esperado: "460 / 674" o "460/ 674" o "460/674"
        
        Returns:
            Tupla (x, y) o None si no se pudo extraer
        """
        imagen_procesada = self._procesar_imagen_ocr(imagen)
        
        # [DEBUG] Descomentar para ver qué captura el OCR
        # cv2.imwrite("debug_coordenadas.png", imagen_procesada)
        
        # Configuración óptima: PSM 7 (línea de texto) + whitelist de números
        config_tesseract = '--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789/'
        texto = pytesseract.image_to_string(imagen_procesada, config=config_tesseract)
        texto = texto.strip()
        
        # [DEBUG] Descomentar para ver qué detecta el OCR
        # print(f"[DEBUG OCR] Texto: '{texto}'")
        
        # Extraer números del texto
        numeros = re.findall(r'\d+', texto)
        
        if len(numeros) >= 2:
            try:
                x = int(numeros[0])
                y = int(numeros[1])
                return (x, y)
            except ValueError:
                pass
        
        return None
    
    def _validar_lectura_ocr(self, x: int, y: int) -> bool:
        """
        Valida que la lectura de OCR sea coherente con el movimiento.
        
        Reglas:
        - No puede avanzar más de 50 unidades en ningún eje
        - Ambos ejes no pueden cambiar significativamente al mismo tiempo
        - Si se presionó W o S (movimiento vertical), X no debe cambiar
        - Si se presionó A o D (movimiento horizontal), Y no debe cambiar
        
        Args:
            x, y: Coordenadas leídas
            
        Returns:
            True si la lectura es válida, False si es inválida
        """
        # Si no hay posición anterior, aceptar la lectura
        if self.ultima_pos_valida is None:
            return True
        
        prev_x, prev_y = self.ultima_pos_valida
        delta_x = abs(x - prev_x)
        delta_y = abs(y - prev_y)
        
        # Validar que no avance más de 50 unidades en ningún eje
        MAX_DELTA = 50
        if delta_x > MAX_DELTA or delta_y > MAX_DELTA:
            print(f"[CONTROL ÁREA] OCR inválido: Delta muy grande ({delta_x}, {delta_y}) > {MAX_DELTA}")
            return False
        
        # Validar que no cambien AMBOS ejes significativamente al mismo tiempo
        # (el personaje solo puede moverse en una dirección a la vez)
        TOLERANCIA_DOBLE = 10
        if delta_x > TOLERANCIA_DOBLE and delta_y > TOLERANCIA_DOBLE:
            print(f"[CONTROL ÁREA] OCR inválido: Cambio en ambos ejes ({delta_x}, {delta_y})")
            return False
        
        # Validar coherencia con la tecla presionada (cuando el bot mueve)
        if self.tecla_movimiento:
            TOLERANCIA = 5  # Pequeña tolerancia para errores menores
            
            if self.tecla_movimiento in ['W', 'S']:
                # Movimiento vertical (Y cambia) - X NO debe cambiar significativamente
                if delta_x > TOLERANCIA:
                    print(f"[CONTROL ÁREA] OCR inválido: Tecla {self.tecla_movimiento} pero X cambió {delta_x}")
                    return False
            
            elif self.tecla_movimiento in ['A', 'D']:
                # Movimiento horizontal (X cambia) - Y NO debe cambiar significativamente
                if delta_y > TOLERANCIA:
                    print(f"[CONTROL ÁREA] OCR inválido: Tecla {self.tecla_movimiento} pero Y cambió {delta_y}")
                    return False
        
        return True
    
    def _crear_poligono(self, puntos: list) -> Polygon:
        """Crea un objeto Polygon de shapely desde una lista de puntos."""
        return Polygon([(p[0], p[1]) for p in puntos])
    
    def _punto_en_poligono(self, x: float, y: float, poligono: Polygon) -> bool:
        """
        Verifica si un punto está dentro del polígono usando shapely.
        
        Args:
            x, y: Coordenadas del punto
            poligono: Objeto Polygon de shapely
            
        Returns:
            True si el punto está dentro o en el borde del polígono
        """
        punto = Point(x, y)
        return poligono.contains(punto) or poligono.touches(punto)
    
    def _obtener_punto_mas_cercano(self, x: float, y: float, poligono: Polygon) -> tuple:
        """
        Encuentra el punto más cercano DENTRO del polígono.
        Proyecta al borde y luego un poco hacia el interior.
        
        Args:
            x, y: Posición actual (fuera del polígono)
            poligono: Objeto Polygon de shapely
            
        Returns:
            Tupla (x, y) del punto objetivo dentro del polígono
        """
        punto = Point(x, y)
        
        # Encontrar el punto más cercano en el borde del polígono
        punto_borde = poligono.exterior.interpolate(
            poligono.exterior.project(punto)
        )
        
        # Mover un poco hacia el interior (hacia el centroide) para asegurar que está dentro
        centroide = poligono.centroid
        factor = 0.15  # 15% hacia el centro desde el borde
        objetivo_x = punto_borde.x + (centroide.x - punto_borde.x) * factor
        objetivo_y = punto_borde.y + (centroide.y - punto_borde.y) * factor
        
        return (objetivo_x, objetivo_y)
    
    def _determinar_tecla_regreso(self, x: float, y: float, objetivo_x: float, objetivo_y: float) -> str:
        """
        Determina qué tecla presionar para ir hacia el objetivo.
        Incluye lógica anti-oscilación.
        
        Mapa en cuarto cuadrante con controles INVERTIDOS:
        - W → Sur (Y aumenta)
        - S → Norte (Y disminuye)
        - A → Este (X aumenta)
        - D → Oeste (X disminuye)
        
        Args:
            x, y: Posición actual del personaje
            objetivo_x, objetivo_y: Punto objetivo (centroide del polígono)
            
        Returns:
            Tecla a presionar ('W', 'A', 'S', 'D')
        """
        dx = objetivo_x - x  # Diferencia en X
        dy = objetivo_y - y  # Diferencia en Y
        
        # Umbral mínimo para considerar cambio de dirección (evita oscilación)
        UMBRAL_CAMBIO = 5
        
        # Si ya tenemos una tecla y no hemos llegado al umbral, mantenerla
        if self.ultima_tecla and self.contador_misma_tecla < 3:
            # Verificar si la dirección actual sigue siendo válida
            if self.ultima_tecla == 'A' and dx > -UMBRAL_CAMBIO:
                self.contador_misma_tecla += 1
                return 'A'
            elif self.ultima_tecla == 'D' and dx < UMBRAL_CAMBIO:
                self.contador_misma_tecla += 1
                return 'D'
            elif self.ultima_tecla == 'W' and dy > -UMBRAL_CAMBIO:
                self.contador_misma_tecla += 1
                return 'W'
            elif self.ultima_tecla == 'S' and dy < UMBRAL_CAMBIO:
                self.contador_misma_tecla += 1
                return 'S'
        
        # Reiniciar contador al cambiar de tecla
        self.contador_misma_tecla = 0
        
        # Factor de preferencia: si las diferencias son similares, 
        # preferir la dirección con mayor diferencia absoluta
        FACTOR_PREFERENCIA = 1.5
        
        # Determinar la dirección principal
        if abs(dx) > abs(dy) * FACTOR_PREFERENCIA:
            # Movimiento horizontal es claramente más importante
            if dx > 0:
                self.ultima_tecla = 'A'
                return 'A'  # Este
            else:
                self.ultima_tecla = 'D'
                return 'D'  # Oeste
        elif abs(dy) > abs(dx) * FACTOR_PREFERENCIA:
            # Movimiento vertical es claramente más importante
            if dy > 0:
                self.ultima_tecla = 'W'
                return 'W'  # Sur
            else:
                self.ultima_tecla = 'S'
                return 'S'  # Norte
        else:
            # Diferencias similares - mantener última dirección si existe
            if self.ultima_tecla:
                return self.ultima_tecla
            
            # Sin historial, elegir la mayor diferencia
            if abs(dx) >= abs(dy):
                self.ultima_tecla = 'A' if dx > 0 else 'D'
            else:
                self.ultima_tecla = 'W' if dy > 0 else 'S'
            return self.ultima_tecla
    
    def _presionar_tecla_inicio(self, tecla: str):
        """Presiona una tecla (key down) sin soltarla."""
        if tecla not in SCAN_CODES:
            print(f"[CONTROL ÁREA] Error: Tecla '{tecla}' no encontrada")
            return False
        
        scan_code = SCAN_CODES[tecla]
        
        key_down = INPUT()
        key_down.type = INPUT_KEYBOARD
        key_down.ki.wVk = 0
        key_down.ki.wScan = scan_code
        key_down.ki.dwFlags = KEYEVENTF_SCANCODE
        key_down.ki.time = 0
        key_down.ki.dwExtraInfo = None
        
        user32.SendInput(1, ctypes.byref(key_down), ctypes.sizeof(INPUT))
        return True
    
    def _soltar_tecla(self, tecla: str):
        """Suelta una tecla (key up)."""
        if tecla not in SCAN_CODES:
            return
        
        scan_code = SCAN_CODES[tecla]
        
        key_up = INPUT()
        key_up.type = INPUT_KEYBOARD
        key_up.ki.wVk = 0
        key_up.ki.wScan = scan_code
        key_up.ki.dwFlags = KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP
        key_up.ki.time = 0
        key_up.ki.dwExtraInfo = None
        
        user32.SendInput(1, ctypes.byref(key_up), ctypes.sizeof(INPUT))
    
    def _click_deseleccionar(self):
        """
        Hace click izquierdo en el centro de la pantalla (3% más abajo)
        para deseleccionar el objetivo actual.
        """
        rect = self._obtener_rect_ventana()
        ancho = rect.right - rect.left
        alto = rect.bottom - rect.top
        
        # Centro + 3% más abajo
        centro_x = ancho // 2
        centro_y = (alto // 2) + int(alto * 0.04)
        
        # Constantes para click izquierdo
        WM_LBUTTONDOWN = 0x0201
        WM_LBUTTONUP = 0x0202
        
        lParam = (centro_y << 16) | centro_x
        
        user32.PostMessageW(self.hwnd, WM_LBUTTONDOWN, 0x0001, lParam)
        time.sleep(0.05)
        user32.PostMessageW(self.hwnd, WM_LBUTTONUP, 0, lParam)
        print(f"[CONTROL ÁREA] Click izquierdo ({centro_x}, {centro_y}) - Deseleccionando objetivo")
    
    def _click_centro_arriba(self):
        """
        Hace click izquierdo en el centro de la pantalla (10% más arriba).
        """
        rect = self._obtener_rect_ventana()
        ancho = rect.right - rect.left
        alto = rect.bottom - rect.top
        
        # Centro - 10% más arriba
        centro_x = ancho // 2
        centro_y = (alto // 2) - int(alto * 0.10)
        
        # Constantes para click izquierdo
        WM_LBUTTONDOWN = 0x0201
        WM_LBUTTONUP = 0x0202
        
        lParam = (centro_y << 16) | centro_x
        
        user32.PostMessageW(self.hwnd, WM_LBUTTONDOWN, 0x0001, lParam)
        time.sleep(0.05)
        user32.PostMessageW(self.hwnd, WM_LBUTTONUP, 0, lParam)
        print(f"[CONTROL ÁREA] Click izquierdo ({centro_x}, {centro_y}) - Centro arriba")
    
    def _click_central_fijar_camara(self):
        """
        Hace click con el botón central del mouse para fijar la cámara.
        Esto posiciona la cámara de forma que W=Sur, A=Este, S=Norte, D=Oeste.
        """
        rect = self._obtener_rect_ventana()
        centro_x = (rect.right - rect.left) // 2
        centro_y = (rect.bottom - rect.top) // 2
        
        # Constantes para click central
        WM_MBUTTONDOWN = 0x0207
        WM_MBUTTONUP = 0x0208
        
        lParam = (centro_y << 16) | centro_x
        
        user32.PostMessageW(self.hwnd, WM_MBUTTONDOWN, 0x0010, lParam)
        time.sleep(0.05)
        user32.PostMessageW(self.hwnd, WM_MBUTTONUP, 0, lParam)
        print("[CONTROL ÁREA] Click central - Fijando camara para WASD")
    
    def _ciclo_control_area(self):
        """Ciclo principal del control de área."""
        print("[CONTROL ÁREA] Hilo iniciado - Esperando configuracion...")
        
        while self.ejecutando:
            # Verificar si este hilo está activo
            if not estado.hilo_activo('control_area'):
                time.sleep(0.5)
                continue
            
            try:
                import configuracion
                config = configuracion.CONTROL_AREA
                
                # Verificar si está habilitado
                if not config.get('habilitado', False):
                    time.sleep(2.0)
                    continue
                
                # Obtener polígono configurado
                puntos_poligono = config.get('poligono', [])
                if len(puntos_poligono) < 3:
                    # Necesitamos al menos 3 puntos para formar un polígono
                    time.sleep(1.0)
                    continue
                
                # Crear polígono con shapely
                poligono = self._crear_poligono(puntos_poligono)
                
                # Capturar y leer coordenadas
                imagen = self._capturar_region_coordenadas()
                coordenadas = self._extraer_coordenadas(imagen)
                
                if coordenadas is None:
                    # No se pudieron leer las coordenadas, esperar y reintentar
                    time.sleep(config.get('intervalo_lectura', 0.5))
                    continue
                
                x, y = coordenadas
                
                # Validar coherencia de la lectura OCR
                if not self._validar_lectura_ocr(x, y):
                    # Lectura inválida, usar última posición válida o esperar
                    if self.ultima_pos_valida:
                        x, y = self.ultima_pos_valida
                        print(f"[CONTROL ÁREA] Usando última posición válida: ({x}, {y})")
                    else:
                        time.sleep(config.get('intervalo_lectura', 0.5))
                        continue
                else:
                    # Lectura válida, actualizar última posición
                    self.ultima_pos_valida = (x, y)
                    # Resetear tecla de movimiento después de validar
                    self.tecla_movimiento = None
                
                # Verificar si está dentro del polígono (usando shapely)
                dentro = self._punto_en_poligono(x, y, poligono)
                
                # Actualizar posición en el estado compartido (para la GUI)
                estado.actualizar_posicion(x, y, dentro)
                
                # Log constante de posición (incluye confirmación de actualización GUI)
                estado_texto = "DENTRO" if dentro else "FUERA"
                print(f"[CONTROL ÁREA] Pos ({x}, {y}) - {estado_texto} [GUI actualizada]")
                
                if dentro:
                    # Está dentro del área - todo normal
                    if self.fuera_de_area:
                        print(f"[CONTROL ÁREA] === REGRESO AL AREA === Reactivando hilos")
                        self.fuera_de_area = False
                        # Resetear estado anti-oscilación
                        self.objetivo_fijo = None
                        self.ultima_tecla = None
                        self.contador_misma_tecla = 0
                        self.tecla_movimiento = None
                        estado.reactivar_todos_los_hilos()
                    
                    time.sleep(config.get('intervalo_lectura', 0.5))
                    
                else:
                    # Está FUERA del área - activar corrección
                    if not self.fuera_de_area:
                        print(f"[CONTROL ÁREA] === SALIO DEL AREA === Iniciando correccion")
                        self.fuera_de_area = True
                        
                        # Pausar hilos de combate (habilidades, mob_trabado, observador_objetivo)
                        # Los hilos default (autocuración, detector_ocr, control_area) se mantienen activos
                        estado.pausar_todos_los_hilos()
                        
                        # 1. Click izquierdo para deseleccionar el objetivo (centro +3% abajo)
                        self._click_deseleccionar()
                        time.sleep(0.1)
                        
                        # 2. Click central para fijar la cámara (WASD funcionan correctamente)
                        self._click_central_fijar_camara()
                        time.sleep(0.1)
                        
                        # 3. Click izquierdo arriba (centro -10% arriba)
                        self._click_centro_arriba()
                        time.sleep(0.2)
                        self._click_centro_arriba()
                        time.sleep(0.2)
                    
                    # Calcular punto más cercano del polígono (recalcula cada vez)
                    objetivo_x, objetivo_y = self._obtener_punto_mas_cercano(x, y, poligono)
                    tecla = self._determinar_tecla_regreso(x, y, objetivo_x, objetivo_y)
                    
                    dist = ((x - objetivo_x)**2 + (y - objetivo_y)**2)**0.5
                    duracion = config.get('duracion_movimiento', 3.0)
                    
                    print(f"[CONTROL ÁREA] ({x}, {y}) -> ({objetivo_x:.0f}, {objetivo_y:.0f}) | Dist: {dist:.0f} | Tecla: {tecla} x {duracion}s")
                    
                    # Guardar la tecla de movimiento para validación posterior
                    self.tecla_movimiento = tecla
                    
                    # Mantener tecla presionada durante la duración configurada
                    self._presionar_tecla_inicio(tecla)
                    time.sleep(duracion)
                    self._soltar_tecla(tecla)
                    
                    # Verificar inmediatamente si ya está dentro del polígono
                    time.sleep(0.1)
                    imagen_check = self._capturar_region_coordenadas()
                    coords_check = self._extraer_coordenadas(imagen_check)
                    
                    if coords_check:
                        x_check, y_check = coords_check
                        
                        # Validar la lectura post-movimiento
                        if self._validar_lectura_ocr(x_check, y_check):
                            self.ultima_pos_valida = (x_check, y_check)
                            self.tecla_movimiento = None
                            
                            if self._punto_en_poligono(x_check, y_check, poligono):
                                print(f"[CONTROL ÁREA] Ya dentro ({x_check}, {y_check}) - Activando observador")
                                self.fuera_de_area = False
                                self.objetivo_fijo = None
                                self.ultima_tecla = None
                                self.contador_misma_tecla = 0
                                estado.reactivar_todos_los_hilos()
                        else:
                            print(f"[CONTROL ÁREA] Lectura post-movimiento inválida, reintentando...")
                
            except Exception as e:
                print(f"[CONTROL ÁREA] Error: {e}")
                time.sleep(1.0)
        
        print("[CONTROL ÁREA] Hilo finalizado")
    
    def iniciar(self):
        """Inicia el hilo de control de área."""
        if self.ejecutando:
            return
        
        self.ejecutando = True
        self.thread = threading.Thread(target=self._ciclo_control_area, daemon=True)
        self.thread.start()
    
    def detener(self):
        """Detiene el hilo de control de área."""
        self.ejecutando = False
        if self.thread:
            self.thread.join(timeout=2.0)


# =============================================================================
# PRUEBA INDEPENDIENTE
# =============================================================================
if __name__ == "__main__":
    from game_window import GameWindow
    import configuracion
    
    print("=== Prueba de Control de Área ===")
    print()
    
    # Buscar ventana del juego
    game = GameWindow(configuracion.GAME_WINDOW_TITLE)
    if not game.hwnd:
        print("ERROR: No se encontró la ventana del juego")
        print(f"Buscando: '{configuracion.GAME_WINDOW_TITLE}'")
        exit(1)
    
    print(f"Ventana encontrada: {game.hwnd}")
    print()
    
    # Crear instancia para probar captura
    control = HiloControlArea(game.hwnd)
    
    # Probar captura de coordenadas
    print("Capturando región de coordenadas...")
    imagen = control._capturar_region_coordenadas()
    
    # Guardar imagen para debug
    cv2.imwrite("debug_coordenadas_raw.png", imagen)
    print("Imagen guardada: debug_coordenadas_raw.png")
    
    # Procesar y guardar
    procesada = control._procesar_imagen_ocr(imagen)
    cv2.imwrite("debug_coordenadas_proc.png", procesada)
    print("Imagen procesada: debug_coordenadas_proc.png")
    
    # Extraer coordenadas
    coords = control._extraer_coordenadas(imagen)
    if coords:
        print(f"\n[OK] Coordenadas detectadas: X={coords[0]}, Y={coords[1]}")
    else:
        print("\n[ERROR] No se pudieron detectar las coordenadas")
    
    print()
    print("Revisa las imágenes debug_coordenadas_*.png para ajustar la región si es necesario")

