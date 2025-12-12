"""
Hilo: Mob Trabado
Detecta cuando un mob lleva mucho tiempo y ejecuta la secuencia de escape (clics alternados).
"""
import time
import threading

from estado_objetivo import estado, TipoObjetivo
from configuracion import ESCAPE_MOB, ESCAPE_BY_MOB
import ctypes


class RECT(ctypes.Structure):
    """Estructura para representar un rectángulo en Windows."""
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


class HiloMobTrabado:
    """
    Hilo que detecta mobs trabados y ejecuta escape mediante clics alternados.
    """

    def __init__(self, hwnd: int):
        self.hwnd = hwnd
        self.user32 = ctypes.windll.user32
        self.ejecutando = False
        self.thread = None
        self._escape_ejecutado_para_mob = None
        self._escape_punto_actual = 0

    # ------------------------------
    # Helpers de ventana y clic
    # ------------------------------
    def _obtener_rect_ventana(self) -> RECT:
        rect = RECT()
        self.user32.GetWindowRect(self.hwnd, ctypes.byref(rect))
        return rect

    def _hacer_clic(self, x_relativo: int, y_relativo: int) -> None:
        rect = self._obtener_rect_ventana()
        x_abs = rect.left + x_relativo
        y_abs = rect.top + y_relativo

        # Mover cursor
        self.user32.SetCursorPos(x_abs, y_abs)
        time.sleep(0.05)

        # Clic izquierdo
        self.user32.mouse_event(0x0002, 0, 0, 0, 0)  # Down
        time.sleep(0.05)
        self.user32.mouse_event(0x0004, 0, 0, 0, 0)  # Up

    # ------------------------------
    # Lógica de escape
    # ------------------------------
    def _ejecutar_escape(self) -> None:
        nombre_mob = estado.nombre_coincidente
        puntos = ESCAPE_MOB["puntos_clic"]
        punto = puntos[self._escape_punto_actual]
        click_x = punto["x"]
        click_y = punto["y"]

        print(
            f"[ESCAPE] 🏃 Mob trabado ({nombre_mob}) - Punto {self._escape_punto_actual + 1}/{len(puntos)}"
        )
        print(f"[ESCAPE] Haciendo clic en ({click_x}, {click_y})")

        # Marcar acción en progreso
        estado.iniciar_accion_loot()

        # Pausar hilos
        estado.pausar_todos_los_hilos()

        # Clics
        veces = ESCAPE_MOB["veces"]
        duracion = ESCAPE_MOB["duracion_total"]
        intervalo = duracion / veces
        for i in range(veces):
            self._hacer_clic(click_x, click_y)
            print(f"[ESCAPE] Clic en ({click_x}, {click_y}) - ({i+1}/{veces})")
            if i < veces - 1:
                time.sleep(intervalo)

        time.sleep(0.2)

        # Reactivar hilos
        estado.reactivar_todos_los_hilos()
        estado.finalizar_accion_loot()

        # Resetear contador y alternar punto
        estado.resetear_timestamp()
        self._escape_punto_actual = (self._escape_punto_actual + 1) % len(puntos)
        self._escape_ejecutado_para_mob = None

        print(
            f"[ESCAPE] ✅ Completado - Próxima vez usará Punto {self._escape_punto_actual + 1}"
        )

    def _verificar_mob_trabado(self) -> bool:
        if estado.tipo != TipoObjetivo.MOB:
            return False

        nombre_actual = estado.nombre_coincidente
        tiempo_en_estado = estado.tiempo_en_estado_actual

        if self._escape_ejecutado_para_mob == nombre_actual:
            return False

        #El escape depende de con qué mob estes peleando
        #si es fuerte demora más, si es debil demora menos
        tiempo_escape = ESCAPE_BY_MOB.get(nombre_actual, ESCAPE_MOB["timeout_mob"])
        
        if tiempo_en_estado >= tiempo_escape:
            self._escape_ejecutado_para_mob = nombre_actual
            return True

        # Si cambia de mob, limpiar flag
        if self._escape_ejecutado_para_mob and self._escape_ejecutado_para_mob != nombre_actual:
            self._escape_ejecutado_para_mob = None

        return False

    # ------------------------------
    # Loop
    # ------------------------------
    def _ciclo(self) -> None:
        print("[ESCAPE] Hilo de mob trabado iniciado")
        while self.ejecutando:
            if not estado.hilo_activo("mob_trabado"):
                time.sleep(0.1)
                continue

            try:
                if self._verificar_mob_trabado() and not estado.ejecutando_loot:
                    estado.pausar_todos_los_hilos_excepto('mob_trabado')
                    self._ejecutar_escape()
                    estado.pausar_todos_los_hilos_excepto('observador_objetivo')
                
                nombre_actual = estado.nombre_coincidente
                tiempo_escape = ESCAPE_BY_MOB.get(nombre_actual, ESCAPE_MOB["timeout_mob"])
                if estado.tiempo_en_estado_actual >= tiempo_escape + ESCAPE_MOB["duracion_total"] + 1:
                    estado.resetear_timestamp()
                    print(f"hilo de mob trabado activo por {estado.tiempo_en_estado_actual} segundos    ")
                
            except Exception as e:
                print(f"[ESCAPE] Error: {e}")

            time.sleep(0.1)

        print("[ESCAPE] Hilo de mob trabado detenido")

    def iniciar(self) -> None:
        if self.ejecutando:
            return
        self.ejecutando = True
        self.thread = threading.Thread(target=self._ciclo, daemon=True)
        self.thread.start()

    def detener(self) -> None:
        self.ejecutando = False
        if self.thread:
            self.thread.join(timeout=2)

