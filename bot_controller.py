"""
Controlador del bot para la interfaz gráfica.
Maneja el inicio y detención de los hilos del bot.
"""
import threading
import time
from typing import Optional, List, Callable

from game_window import GameWindow
from estado_objetivo import estado
import configuracion

from hilo_detector_ocr import HiloDetectorOCR
from hilo_habilidades import HiloHabilidades
from hilo_autocuracion import HiloAutocuracion
from hilo_observador_objetivo import HiloObservadorObjetivo
from hilo_recoger_drop import HiloRecogerDrop
from hilo_mob_trabado import HiloMobTrabado


class BotController:
    """
    Controlador principal del bot.
    Gestiona todos los hilos y el estado de ejecución.
    """
    
    def __init__(self, status_callback: Optional[Callable] = None):
        """
        Inicializa el controlador del bot.
        
        Args:
            status_callback: Función callback para actualizar el estado en la GUI
        """
        self.status_callback = status_callback
        self.ejecutando = False
        self.game_window: Optional[GameWindow] = None
        self.hilos: List = []
        self.thread_monitor: Optional[threading.Thread] = None
        self.error_message: Optional[str] = None
    
    def iniciar(self):
        """
        Inicia el bot y todos sus hilos.
        
        Returns:
            Tupla (éxito, mensaje)
        """
        if self.ejecutando:
            return False, "El bot ya está en ejecución"
        
        try:
            # Buscar ventana del juego (usar configuración actualizada)
            self.game_window = GameWindow(configuracion.GAME_WINDOW_TITLE)
            
            # Crear e iniciar todos los hilos
            detector_ocr = HiloDetectorOCR(self.game_window.hwnd)
            detector_ocr.iniciar()
            self.hilos.append(detector_ocr)
            
            habilidades = HiloHabilidades(self.game_window.hwnd)
            habilidades.iniciar()
            self.hilos.append(habilidades)
            
            autocuracion = HiloAutocuracion(self.game_window.hwnd)
            autocuracion.iniciar()
            self.hilos.append(autocuracion)
            
            observador = HiloObservadorObjetivo(self.game_window.hwnd)
            observador.iniciar()
            self.hilos.append(observador)
            
            hilo_loot = HiloRecogerDrop(self.game_window.hwnd)
            hilo_loot.iniciar()
            self.hilos.append(hilo_loot)
            
            hilo_esc = HiloMobTrabado(self.game_window.hwnd)
            hilo_esc.iniciar()
            self.hilos.append(hilo_esc)
            
            self.ejecutando = True
            self.error_message = None
            
            # Iniciar hilo de monitoreo
            self.thread_monitor = threading.Thread(target=self._monitorear_estado, daemon=True)
            self.thread_monitor.start()
            
            return True, "Bot iniciado correctamente"
            
        except Exception as e:
            self.error_message = str(e)
            self.detener()
            return False, f"Error al iniciar bot: {e}"
    
    def detener(self):
        """
        Detiene el bot y todos sus hilos.
        
        Returns:
            Tupla (éxito, mensaje)
        """
        if not self.ejecutando:
            return False, "El bot no está en ejecución"
        
        self.ejecutando = False
        
        # Detener todos los hilos
        for hilo in self.hilos:
            try:
                hilo.detener()
            except Exception as e:
                print(f"Error al detener hilo: {e}")
        
        self.hilos.clear()
        self.game_window = None
        
        return True, "Bot detenido correctamente"
    
    def _monitorear_estado(self) -> None:
        """Monitorea el estado del bot y actualiza la GUI."""
        while self.ejecutando:
            try:
                info = estado.obtener_info()
                
                if self.status_callback:
                    self.status_callback(info)
                
                time.sleep(0.5)
            except Exception as e:
                print(f"Error en monitoreo: {e}")
                time.sleep(1)
    
    def esta_ejecutando(self) -> bool:
        """Retorna True si el bot está en ejecución."""
        return self.ejecutando
    
    def obtener_estado(self) -> dict:
        """
        Obtiene el estado actual del objetivo.
        
        Returns:
            Diccionario con información del estado
        """
        if not self.ejecutando:
            return {
                'tipo': 'nulo',
                'nombre': 'N/A',
                'tiempo': 0.0,
                'similitud': 0.0
            }
        
        try:
            info = estado.obtener_info()
            return {
                'tipo': info['tipo'].value,
                'nombre': info['nombre_coincidente'] or 'N/A',
                'tiempo': info['tiempo_en_estado'],
                'similitud': info['similitud'] * 100
            }
        except:
            return {
                'tipo': 'nulo',
                'nombre': 'N/A',
                'tiempo': 0.0,
                'similitud': 0.0
            }

