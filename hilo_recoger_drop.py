"""
Hilo: Recoger Drop (loot al morir el mob)
Escucha transiciones MOB -> NULO y ejecuta la secuencia de loot.
"""
import time
import threading

from estado_objetivo import estado, TipoObjetivo
from configuracion import VK_CODES, LOOT_DROP

# Constantes de Windows para teclado
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101


class HiloRecogerDrop:
    """
    Hilo que ejecuta el loot cuando el mob muere (MOB -> NULO).
    """

    def __init__(self, hwnd: int):
        """
        Inicializa el hilo de loot.

        Args:
            hwnd: Handle de la ventana del juego
        """
        self.hwnd = hwnd
        self.user32 = None
        self.ejecutando = False
        self.thread = None
        self.config_loot = LOOT_DROP

    # ---------------------------------------------
    # Helpers de teclado
    # ---------------------------------------------
    def _presionar_tecla(self, tecla: str) -> None:
        if not self.user32:
            self.user32 = __import__("ctypes").windll.user32
        if tecla not in VK_CODES:
            return
        vk_code = VK_CODES[tecla]
        self.user32.PostMessageW(self.hwnd, WM_KEYDOWN, vk_code, 0)
        time.sleep(0.05)
        self.user32.PostMessageW(self.hwnd, WM_KEYUP, vk_code, 0)

    def _presionar_tecla_f(self) -> None:
        """Presiona la tecla F para lootear."""
        self._presionar_tecla("F")

    # ---------------------------------------------
    # Lógica principal de loot
    # ---------------------------------------------
    def _ejecutar_loot(self) -> None:
        """
        Ejecuta la acción de loot:
        - Pausa todos los hilos
        - Presiona F N veces (configurable) con un intervalo configurable
        - Reactiva hilos al finalizar
        """
        print("[LOOT] 🎁 Mob murió - Ejecutando secuencia de loot (hilo_recoger_drop)...")

        # Marcar que estamos en acción de loot
        estado.iniciar_accion_loot()

        # Pausar todos los hilos
        estado.pausar_todos_los_hilos()

        repeticiones = max(0, int(self.config_loot.get('repeticiones_f', 3)))
        intervalo = float(self.config_loot.get('intervalo_f', 0.5))

        # Presionar F repeticiones configuradas
        for i in range(repeticiones):
            self._presionar_tecla_f()
            print(f"[LOOT] Tecla F presionada ({i+1}/{repeticiones})")
            if i < repeticiones - 1:
                time.sleep(intervalo)

        # Esperar hasta ~1.s totales (0.5 + 0.5 + 0.5)
        # time.sleep(0.5)

        # Reactivar todos los hilos
        estado.reactivar_todos_los_hilos()

        # Marcar que terminamos
        estado.finalizar_accion_loot()

        print("[LOOT] ✅ Secuencia de loot completada")

    # ---------------------------------------------
    # Loop principal
    # ---------------------------------------------
    def _ciclo_loot(self) -> None:
        print("[LOOT] Hilo de recoger drop iniciado")
        while self.ejecutando:
            # Verificar si este hilo está activo
            if not estado.hilo_activo("recoger_drop"):
                time.sleep(0.1)
                continue

            info = estado.obtener_info()

            # Detectar transición MOB -> NULO
            if (
                info["tipo"] in [TipoObjetivo.NULO, TipoObjetivo.DROP]
                and info["tipo_anterior"] == TipoObjetivo.MOB
                and not estado.ejecutando_loot
            ):
                estado.pausar_todos_los_hilos_excepto('recoger_drop')
                self._ejecutar_loot()
                # Resetear timestamp para que el contador arranque en 0
                estado.resetear_timestamp()
                estado.pausar_todos_los_hilos_excepto('observador_objetivo')

            time.sleep(0.1)

        print("[LOOT] Hilo de recoger drop detenido")

    def iniciar(self) -> None:
        if self.ejecutando:
            return
        self.ejecutando = True
        self.thread = threading.Thread(target=self._ciclo_loot, daemon=True)
        self.thread.start()

    def detener(self) -> None:
        self.ejecutando = False
        if self.thread:
            self.thread.join(timeout=2)

