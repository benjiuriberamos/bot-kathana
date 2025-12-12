"""
Hilo 2: Disparador de Habilidades
Presiona las teclas de habilidades cuando el objetivo es MOB o DROP.
Trabaja en paralelo observando el estado global.
Se pausa cuando el estado indica que los hilos deben detenerse.
"""
import ctypes
import time
import threading

from estado_objetivo import estado, TipoObjetivo
from configuracion import HABILIDADES, VK_CODES

# Cargar DLL de Windows
user32 = ctypes.windll.user32

# Constantes para mensajes de teclado
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101


class HiloHabilidades:
    """
    Hilo que presiona habilidades según la configuración.
    Solo actúa cuando el objetivo es MOB o DROP.
    """
    
    def __init__(self, hwnd: int):
        """
        Inicializa el disparador de habilidades.
        
        Args:
            hwnd: Handle de la ventana del juego
        """
        self.hwnd = hwnd
        self.ejecutando = False
        self.thread = None
        # Tiempo del último uso de cada habilidad
        self.ultimo_uso = {tecla: 0 for tecla in HABILIDADES.keys()}
    
    def _presionar_tecla(self, tecla: str) -> None:
        """Presiona una tecla en la ventana del juego."""
        if tecla not in VK_CODES:
            return
        
        vk_code = VK_CODES[tecla]
        user32.PostMessageW(self.hwnd, WM_KEYDOWN, vk_code, 0)
        time.sleep(0.05)
        user32.PostMessageW(self.hwnd, WM_KEYUP, vk_code, 0)
    
    def _habilidad_lista(self, tecla: str) -> bool:
        """
        Verifica si una habilidad está lista para usar.
        
        Args:
            tecla: Tecla de la habilidad
            
        Returns:
            True si pasó suficiente tiempo desde el último uso
        """
        config = HABILIDADES.get(tecla)
        if not config or not config['active']:
            return False
        
        tiempo_actual = time.time()
        tiempo_desde_uso = tiempo_actual - self.ultimo_uso[tecla]
        
        return tiempo_desde_uso >= config['time']
    
    def _usar_habilidad(self, tecla: str) -> None:
        """Usa una habilidad y registra el tiempo."""
        self._presionar_tecla(tecla)
        self.ultimo_uso[tecla] = time.time()
        print(f"[HABILIDAD] Tecla {tecla} presionada")
    
    def _presionar_r_atacar(self) -> None:
        """Presiona R para atacar al mob."""
        self._presionar_tecla('R')
    
    def _ciclo_habilidades(self) -> None:
        """Ciclo principal del hilo de habilidades."""
        print("[HABILIDADES] Hilo iniciado")
        
        while self.ejecutando:
            # Verificar si este hilo está activo
            if not estado.hilo_activo('habilidades'):
                time.sleep(0.1)
                continue
            
            tipo_actual = estado.tipo
            nombre_coincidente = estado.nombre_coincidente
            
            # Solo actuar si el objetivo es MOB o DROP Y tiene nombre coincidente válido
            # Esto evita atacar mobs que no están en la lista
            if tipo_actual in (TipoObjetivo.MOB, TipoObjetivo.DROP) and nombre_coincidente:
                # Si es MOB, también atacar con R
                if tipo_actual == TipoObjetivo.MOB:
                    self._presionar_r_atacar()
                
                # Revisar cada habilidad activa
                for tecla, config in HABILIDADES.items():
                    if config['active'] and self._habilidad_lista(tecla):
                        self._usar_habilidad(tecla)
                        time.sleep(0.1)  # Pausa entre habilidades
                
                time.sleep(0.5)  # Revisar cada 0.5 segundos en combate
            else:
                # No hay objetivo válido o no está en la lista, esperar
                time.sleep(0.3)
        
        print("[HABILIDADES] Hilo detenido")
    
    def iniciar(self) -> None:
        """Inicia el hilo de habilidades."""
        if self.ejecutando:
            return
        
        self.ejecutando = True
        self.thread = threading.Thread(target=self._ciclo_habilidades, daemon=True)
        self.thread.start()
    
    def detener(self) -> None:
        """Detiene el hilo de habilidades."""
        self.ejecutando = False
        if self.thread:
            self.thread.join(timeout=2)
    
    def mostrar_configuracion(self) -> None:
        """Muestra la configuración actual de habilidades."""
        print("\n[CONFIGURACIÓN DE HABILIDADES]")
        print("-" * 40)
        for tecla, config in HABILIDADES.items():
            estado_txt = "✅ ACTIVA" if config['active'] else "❌ INACTIVA"
            print(f"  Tecla {tecla}: {estado_txt} | Cooldown: {config['time']}s")
        print("-" * 40)


# ============================================================
# PRUEBA INDEPENDIENTE
# ============================================================
if __name__ == "__main__":
    from game_window import GameWindow
    from configuracion import GAME_WINDOW_TITLE
    
    try:
        print("=" * 60)
        print("PRUEBA DEL HILO DE HABILIDADES")
        print("=" * 60)
        
        # Buscar ventana
        print("\n[INFO] Buscando ventana del juego...")
        game_window = GameWindow(GAME_WINDOW_TITLE)
        print(f"[OK] Ventana encontrada (Handle: {game_window.hwnd})")
        
        # Crear e iniciar hilo
        hilo = HiloHabilidades(game_window.hwnd)
        hilo.mostrar_configuracion()
        
        print("\n[INFO] Iniciando hilo de habilidades...")
        print("[INFO] El hilo solo actuará cuando estado.tipo sea MOB o DROP")
        print("[INFO] Presiona Ctrl+C para detener")
        print("-" * 60)
        
        hilo.iniciar()
        
        # Mantener corriendo
        while True:
            tipo = estado.tipo.value
            print(f"[STATUS] Estado actual: {tipo}", end='\r')
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n[INFO] Hilo detenido por el usuario")
        hilo.detener()
        print("[OK] Script finalizado")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
