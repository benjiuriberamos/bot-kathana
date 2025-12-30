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
        # Leer configuración dinámicamente desde el módulo
        import configuracion
        escape_mob = configuracion.ESCAPE_MOB
        
        # Obtener nombre una vez al inicio
        info = estado.obtener_info()
        nombre_mob = info['nombre_coincidente']
        puntos = escape_mob["puntos_clic"]
        
        # Asegurar que el índice esté dentro del rango válido
        if len(puntos) == 0:
            print("[ESCAPE] Error: No hay puntos de clic configurados")
            return
            
        self._escape_punto_actual = self._escape_punto_actual % len(puntos)
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
        veces = escape_mob["veces"]
        duracion = escape_mob["duracion_total"]
        intervalo = duracion / veces

        punto_click_primero = escape_mob["punto_click_primero"]

        

        print(f"[ESCAPE] Clic en ({punto_click_primero["x"]}, {punto_click_primero["y"]})")
        for i in range(veces):
            self._hacer_clic(click_x, click_y)
            print(f"[ESCAPE] Clic en ({click_x}, {click_y}) - ({i+1}/{veces})")
            if i < veces - 1:
                time.sleep(intervalo)

        time.sleep(0.2)

        self._hacer_clic(punto_click_primero["x"], punto_click_primero["y"])
        print("click en la cabeza del personaje")
        time.sleep(0.3)
        self._hacer_clic(punto_click_primero["x"], punto_click_primero["y"])
        print("click en la cabeza del personaje")
        time.sleep(0.3)
        self._hacer_clic(punto_click_primero["x"], punto_click_primero["y"])
        print("click en la cabeza del personaje")

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
        # Leer configuración dinámicamente desde el módulo
        import configuracion
        escape_mob = configuracion.ESCAPE_MOB
        escape_by_mob = configuracion.ESCAPE_BY_MOB
        
        # Obtener información una vez
        info = estado.obtener_info()
        if info['tipo'] != TipoObjetivo.MOB:
            return False

        nombre_actual = info['nombre_coincidente']
        tiempo_en_estado = info['tiempo_en_estado']

        if self._escape_ejecutado_para_mob == nombre_actual:
            return False

        #El escape depende de con qué mob estes peleando
        #si es fuerte demora más, si es debil demora menos
        tiempo_escape = escape_by_mob.get(nombre_actual, escape_mob["timeout_mob"])
        
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
                # Leer configuración dinámicamente desde el módulo
                import configuracion
                escape_mob = configuracion.ESCAPE_MOB
                escape_by_mob = configuracion.ESCAPE_BY_MOB
                
                # Obtener información una vez por ciclo
                info = estado.obtener_info()
                
                if self._verificar_mob_trabado() and not info['ejecutando_loot']:
                    estado.pausar_todos_los_hilos_excepto('mob_trabado')
                    self._ejecutar_escape()
                    estado.pausar_todos_los_hilos_excepto('observador_objetivo')
                
                nombre_actual = info['nombre_coincidente']
                tiempo_escape = escape_by_mob.get(nombre_actual, escape_mob["timeout_mob"])
                if info['tiempo_en_estado'] >= tiempo_escape + escape_mob["duracion_total"] + 1:
                    estado.resetear_timestamp()
                    print(f"hilo de mob trabado activo por {info['tiempo_en_estado']:.1f} segundos    ")
                
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
    
    def mostrar_configuracion(self) -> None:
        """Muestra la configuración actual de escape."""
        print("\n[CONFIGURACIÓN DE ESCAPE (MOB TRABADO)]")
        print("-" * 50)
        print(f"  Timeout por defecto: {ESCAPE_MOB['timeout_mob']}s")
        print(f"  Veces de clic: {ESCAPE_MOB['veces']}")
        print(f"  Duración total: {ESCAPE_MOB['duracion_total']}s")
        print(f"  Puntos de clic: {len(ESCAPE_MOB['puntos_clic'])}")
        for i, punto in enumerate(ESCAPE_MOB['puntos_clic'], 1):
            print(f"    Punto {i}: ({punto['x']}, {punto['y']})")
        if ESCAPE_BY_MOB:
            print(f"\n  Timeouts personalizados por mob:")
            for mob, timeout in ESCAPE_BY_MOB.items():
                print(f"    {mob}: {timeout}s")
        print("-" * 50)


# ============================================================
# PRUEBA INDEPENDIENTE
# ============================================================
if __name__ == "__main__":
    from game_window import GameWindow
    from configuracion import GAME_WINDOW_TITLE
    
    try:
        print("=" * 60)
        print("PRUEBA DEL HILO DE MOB TRABADO")
        print("=" * 60)
        
        # Buscar ventana
        print("\n[INFO] Buscando ventana del juego...")
        game_window = GameWindow(GAME_WINDOW_TITLE)
        print(f"[OK] Ventana encontrada (Handle: {game_window.hwnd})")
        
        # Crear e iniciar hilo
        hilo = HiloMobTrabado(game_window.hwnd)
        hilo.mostrar_configuracion()
        
        print("\n[INFO] Iniciando hilo de mob trabado...")
        print("[INFO] Presiona Ctrl+C para detener")
        print("-" * 60)
        
        hilo.iniciar()
        
        # Mantener corriendo
        while True:
            info = estado.obtener_info()
            if info['tipo'] == TipoObjetivo.MOB:
                tiempo_escape = ESCAPE_BY_MOB.get(info['nombre_coincidente'], ESCAPE_MOB["timeout_mob"])
                print(f"[STATUS] Mob: {info['nombre_coincidente']} | "
                      f"Tiempo: {info['tiempo_en_estado']:.1f}s / {tiempo_escape}s | "
                      f"Punto actual: {hilo._escape_punto_actual + 1}", end='\r')
            else:
                print(f"[STATUS] Tipo: {info['tipo'].value} | "
                      f"Tiempo: {info['tiempo_en_estado']:.1f}s", end='\r')
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\n[INFO] Hilo detenido por el usuario")
        hilo.detener()
        print("[OK] Script finalizado")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")

