"""
Hilo 1: Detector OCR
Captura la pantalla, procesa con OCR y clasifica el objetivo.
Actualiza el singleton EstadoObjetivo con el tipo detectado.
También ejecuta:
- Secuencia de loot cuando un mob muere
- Secuencia de escape cuando un mob está trabado (> 15 segundos)
"""
import ctypes
import time
import threading
from PIL import Image
import mss
import pytesseract
from difflib import SequenceMatcher

from estado_objetivo import estado, TipoObjetivo
from configuracion import (
    TESSERACT_PATH, OCR_REGION, UMBRAL_SIMILITUD,
    MOBS_OBJETIVO, DROP_ITEMS_OBJETIVO, VK_CODES
)

# Configurar Tesseract
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Constantes para mensajes de teclado
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101


class RECT(ctypes.Structure):
    """Estructura para representar un rectángulo en Windows."""
    _fields_ = [
        ('left', ctypes.c_long),
        ('top', ctypes.c_long),
        ('right', ctypes.c_long),
        ('bottom', ctypes.c_long)
    ]


class HiloDetectorOCR:
    """
    Hilo que captura la pantalla, procesa con OCR y clasifica objetivos.
    Actualiza el estado global constantemente.
    """
    
    def __init__(self, hwnd: int):
        """
        Inicializa el detector OCR.
        
        Args:
            hwnd: Handle de la ventana del juego
        """
        self.hwnd = hwnd
        self.ejecutando = False
        self.thread = None
        self.user32 = ctypes.windll.user32
        self.intervalo = 0.01  # 1000ms entre capturas
        
    def _obtener_rect_ventana(self) -> RECT:
        """Obtiene las coordenadas de la ventana."""
        rect = RECT()
        self.user32.GetWindowRect(self.hwnd, ctypes.byref(rect))
        return rect
    
    def _capturar_region_objetivo(self) -> Image.Image:
        """
        Captura la región de la ventana donde aparece la información del objetivo.
        Usa mss para compatibilidad con juegos DirectX/OpenGL.
        """
        rect = self._obtener_rect_ventana()
        
        region = {
            "left": rect.left + OCR_REGION["left_offset"],
            "top": rect.top + OCR_REGION["top_offset"],
            "width": OCR_REGION["width"],
            "height": OCR_REGION["height"]
        }
        
        with mss.mss() as sct:
            screenshot = sct.grab(region)
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        
        return img
    
    def _procesar_imagen_para_ocr(self, imagen: Image.Image) -> Image.Image:
        """Preprocesa la imagen para mejorar la detección OCR."""
        # Convertir a escala de grises
        imagen_gris = imagen.convert('L')
        # Binarización para mejor OCR
        imagen_binaria = imagen_gris.point(lambda x: 255 if x > 100 else 0)
        return imagen_binaria
    
    def _extraer_texto(self, imagen: Image.Image) -> str:
        """Usa OCR para extraer el texto de la imagen."""
        imagen_procesada = self._procesar_imagen_para_ocr(imagen)
        config_tesseract = '--psm 6 --oem 3'
        texto = pytesseract.image_to_string(imagen_procesada, config=config_tesseract)
        return texto.strip()
    
    def _calcular_similitud(self, texto1: str, texto2: str) -> float:
        """Calcula la similitud entre dos cadenas de texto."""
        if not texto1 or not texto2:
            return 0
        return SequenceMatcher(None, texto1.lower(), texto2.lower()).ratio()
    
    def _buscar_en_lista(self, nombre_detectado: str, lista: list) -> tuple:
        """
        Busca el mejor match en una lista.
        
        Args:
            nombre_detectado: Nombre capturado por OCR
            lista: Lista de nombres a comparar
            
        Returns:
            tuple: (nombre_encontrado, similitud) o (None, 0)
        """
        if not nombre_detectado:
            return None, 0
        
        mejor_match = None
        mejor_similitud = 0
        nombre_limpio = nombre_detectado.strip()
        
        for item in lista:
            similitud = self._calcular_similitud(nombre_limpio, item)
            if similitud > mejor_similitud:
                mejor_similitud = similitud
                mejor_match = item
        
        if mejor_similitud >= UMBRAL_SIMILITUD:
            return mejor_match, mejor_similitud
        
        return None, mejor_similitud
    
    def _presionar_tecla(self, tecla: str) -> None:
        """Presiona una tecla genérica."""
        if tecla not in VK_CODES:
            return
        vk_code = VK_CODES[tecla]
        self.user32.PostMessageW(self.hwnd, WM_KEYDOWN, vk_code, 0)
        time.sleep(0.05)
        self.user32.PostMessageW(self.hwnd, WM_KEYUP, vk_code, 0)
    
    # ============================================================
    # Clasificación de objetivo
    # ============================================================
    
    def _clasificar_objetivo(self, texto_detectado: str) -> None:
        """
        Clasifica el objetivo y actualiza el estado global.
        
        Args:
            texto_detectado: Texto extraído por OCR
        """
        # Si el texto está vacío -> NULO
        if not texto_detectado or texto_detectado.strip() == "":
            estado.establecer_nulo()
            return
        
        # Buscar en la lista de mobs
        mob_encontrado, similitud_mob = self._buscar_en_lista(texto_detectado, MOBS_OBJETIVO)
        if mob_encontrado:
            estado.establecer_mob(texto_detectado, mob_encontrado, similitud_mob)
            return
        
        # Buscar en la lista de drops
        drop_encontrado, similitud_drop = self._buscar_en_lista(texto_detectado, DROP_ITEMS_OBJETIVO)
        if drop_encontrado:
            estado.establecer_drop(texto_detectado, drop_encontrado, similitud_drop)
            return
        
        # No coincide con nada -> NULO (objetivo desconocido)
        estado.establecer_nulo()
    
    def _ciclo_deteccion(self) -> None:
        """Ciclo principal del hilo detector."""
        print("[DETECTOR OCR] Hilo iniciado")
        
        while self.ejecutando:
            # Verificar si este hilo está activo
            if not estado.hilo_activo('detector_ocr'):
                time.sleep(0.1)
                continue
            
            try:
                
                
                # 2. Capturar la región del objetivo
                captura = self._capturar_region_objetivo()
                
                # 3. Extraer texto con OCR
                texto = self._extraer_texto(captura)
                
                # 4. Obtener primera línea (nombre del objetivo)
                lineas = texto.split('\n')
                nombre = lineas[0].strip() if lineas else ""
                
                # 5. Clasificar y actualizar estado
                self._clasificar_objetivo(nombre)

                
            except Exception as e:
                print(f"[DETECTOR OCR] Error: {e}")
            
            time.sleep(self.intervalo)
        
        print("[DETECTOR OCR] Hilo detenido")
    
    def iniciar(self) -> None:
        """Inicia el hilo detector."""
        if self.ejecutando:
            return
        
        self.ejecutando = True
        self.thread = threading.Thread(target=self._ciclo_deteccion, daemon=True)
        self.thread.start()
    
    def detener(self) -> None:
        """Detiene el hilo detector."""
        self.ejecutando = False
        if self.thread:
            self.thread.join(timeout=2)


# ============================================================
# PRUEBA INDEPENDIENTE
# ============================================================
if __name__ == "__main__":
    from game_window import GameWindow
    from configuracion import GAME_WINDOW_TITLE
    
    try:
        print("=" * 60)
        print("PRUEBA DEL DETECTOR OCR")
        print("=" * 60)
        
        # Buscar ventana
        print("\n[INFO] Buscando ventana del juego...")
        game_window = GameWindow(GAME_WINDOW_TITLE)
        print(f"[OK] Ventana encontrada (Handle: {game_window.hwnd})")
        
        # Mostrar configuración
        print(f"\n[INFO] Mobs configurados: {len(MOBS_OBJETIVO)}")
        for mob in MOBS_OBJETIVO:
            print(f"  - {mob}")
        print(f"\n[INFO] Items drop configurados: {len(DROP_ITEMS_OBJETIVO)}")
        for item in DROP_ITEMS_OBJETIVO:
            print(f"  - {item}")
        print(f"\n[INFO] Umbral de similitud: {UMBRAL_SIMILITUD*100:.0f}%")
        
        # Iniciar detector
        print("\n[INFO] Iniciando detector OCR...")
        print("[INFO] Presiona Ctrl+C para detener")
        print("-" * 60)
        
        detector = HiloDetectorOCR(game_window.hwnd)
        detector.iniciar()
        
        # Mantener corriendo
        while True:
            info = estado.obtener_info()
            print(f"[STATUS] Tipo: {info['tipo'].value} | "
                  f"Nombre: {info['nombre_coincidente'] or 'N/A'} | "
                  f"Tiempo: {info['tiempo_en_estado']:.1f}s", end='\r')
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\n[INFO] Detector detenido por el usuario")
        detector.detener()
        print("[OK] Script finalizado")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
