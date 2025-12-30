"""
Hilo 4: Observador de Objetivo
Observa constantemente el estado del objetivo y presiona E según las reglas:
- NULO: Presiona E para seleccionar nuevo objetivo
- MOB: No presiona E (ya tenemos objetivo)
- DROP: Si lleva más de 3 segundos, presiona E
Se pausa cuando el estado indica que los hilos deben detenerse.
"""
import ctypes
import time
import threading

from estado_objetivo import estado, TipoObjetivo
from configuracion import VK_CODES, OBSERVADOR_OBJETIVO

# Cargar DLL de Windows
user32 = ctypes.windll.user32

# Constantes para mensajes de teclado
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101


class HiloObservadorObjetivo:
    """
    Hilo que observa el estado del objetivo y presiona E según las reglas.
    """
    
    def __init__(self, hwnd: int):
        """
        Inicializa el observador de objetivo.
        
        Args:
            hwnd: Handle de la ventana del juego
        """
        self.hwnd = hwnd
        self.ejecutando = False
        self.thread = None
        # No copiar valores, leer dinámicamente desde el módulo
    
    def _presionar_tecla_para_seleccionar(self) -> None:
        """Presiona la tecla configurada para seleccionar objetivo."""
        # Leer configuración dinámicamente desde el módulo
        import configuracion
        tecla = configuracion.OBSERVADOR_OBJETIVO.get('tecla_seleccionar', 'E')
        vk_codes = configuracion.VK_CODES
        
        if tecla not in vk_codes:
            print(f"[OBSERVADOR] Error: Tecla '{tecla}' no encontrada en VK_CODES")
            return
        
        vk_code = vk_codes[tecla]
        user32.PostMessageW(self.hwnd, WM_KEYDOWN, vk_code, 0)
        time.sleep(0.05)
        user32.PostMessageW(self.hwnd, WM_KEYUP, vk_code, 0)
        print(f"[OBSERVADOR] Tecla {tecla} presionada - Seleccionando objetivo...")
    
    def _ciclo_observador(self) -> None:
        """Ciclo principal del observador."""
        print("[OBSERVADOR] Hilo iniciado")
        
        while self.ejecutando:
            # Leer configuración dinámicamente desde el módulo
            timeout_drop = OBSERVADOR_OBJETIVO['timeout_drop']
            intervalo = OBSERVADOR_OBJETIVO['intervalo_revision']
            
            # Verificar si este hilo está activo
            if not estado.hilo_activo('observador_objetivo'):
                time.sleep(0.1)
                continue
            
            # Obtener toda la información una vez por ciclo
            info = estado.obtener_info()
            tipo_actual = info['tipo']
            tiempo_en_estado = info['tiempo_en_estado']
            
            if tipo_actual == TipoObjetivo.NULO:
                # Sin objetivo -> presionar E
                self._presionar_tecla_para_seleccionar()
                time.sleep(1.5)  # Esperar un poco antes de volver a intentar
                
            elif tipo_actual in [TipoObjetivo.MOB, TipoObjetivo.DROP]:
                estado.pausar_todos_los_hilos_excepto('habilidades')
                estado.activar_hilo('recoger_drop')
                estado.activar_hilo('mob_trabado')
                # Tenemos un mob -> no hacer nada
                pass
                
                # Tenemos un drop
                # if tiempo_en_estado >= timeout_drop:
                #     # Lleva más de X segundos en DROP -> presionar E
                #     print(f"[OBSERVADOR] DROP por {tiempo_en_estado:.1f}s (> {timeout_drop}s) -> Presionando E")
                #     self._presionar_tecla_para_seleccionar()
                #     time.sleep(1.5)
            
            time.sleep(intervalo)
        
        print("[OBSERVADOR] Hilo detenido")
    
    def iniciar(self) -> None:
        """Inicia el hilo observador."""
        if self.ejecutando:
            return
        
        self.ejecutando = True
        self.thread = threading.Thread(target=self._ciclo_observador, daemon=True)
        self.thread.start()
    
    def detener(self) -> None:
        """Detiene el hilo observador."""
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
        print("PRUEBA DEL OBSERVADOR DE OBJETIVO")
        print("=" * 60)
        
        # Buscar ventana
        print("\n[INFO] Buscando ventana del juego...")
        game_window = GameWindow(GAME_WINDOW_TITLE)
        print(f"[OK] Ventana encontrada (Handle: {game_window.hwnd})")
        
        # Mostrar configuración
        print(f"\n[INFO] Timeout para DROP: {OBSERVADOR_OBJETIVO['timeout_drop']}s")
        print(f"[INFO] Intervalo de revisión: {OBSERVADOR_OBJETIVO['intervalo_revision']}s")
        
        print("\n[INFO] Reglas:")
        print("  - NULO: Presionar E")
        print("  - MOB: No presionar E")
        print(f"  - DROP: Presionar E después de {OBSERVADOR_OBJETIVO['timeout_drop']}s")
        
        # Iniciar observador
        print("\n[INFO] Iniciando observador...")
        print("[INFO] Presiona Ctrl+C para detener")
        print("-" * 60)
        
        observador = HiloObservadorObjetivo(game_window.hwnd)
        observador.iniciar()
        
        # Mantener corriendo
        while True:
            info = estado.obtener_info()
            print(f"[STATUS] Tipo: {info['tipo'].value} | "
                  f"Tiempo: {info['tiempo_en_estado']:.1f}s | "
                  f"Nombre: {info['nombre_coincidente'] or 'N/A'}", end='\r')
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\n[INFO] Observador detenido por el usuario")
        observador.detener()
        print("[OK] Script finalizado")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
