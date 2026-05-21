"""
Tracker de posición del cursor relativo a una ventana específica.
Muestra en consola las coordenadas del cursor dentro de la ventana indicada.

Dependencias:
    pip install pyautogui pygetwindow

Uso:
    python cursor_tracker.py

Configuración:
    Cambia la variable WINDOW_TITLE con el nombre (parcial) de tu ventana.
"""

import time
import pyautogui
import pygetwindow as gw

# ─────────────────────────────────────────────
#  CONFIGURACIÓN — cambia este valor
WINDOW_TITLE = "Kathana - The Coming of the Dark Ages"   # Nombre parcial o completo de la ventana
REFRESH_RATE  = 0.1        # Segundos entre actualizaciones (0.1 = 10 veces/seg)
# ─────────────────────────────────────────────


def find_window(title: str):
    """Busca la ventana por título (búsqueda parcial, sin importar mayúsculas)."""
    matches = [w for w in gw.getAllWindows() if title.lower() in w.title.lower()]
    if not matches:
        return None
    return matches[0]


def list_open_windows():
    """Muestra todas las ventanas abiertas para ayudar al usuario."""
    windows = [w for w in gw.getAllWindows() if w.title.strip()]
    print("\nVentanas abiertas detectadas:")
    for i, w in enumerate(windows, 1):
        print(f"  [{i:02d}] '{w.title}'  —  pos=({w.left},{w.top})  tamaño={w.width}x{w.height}")
    print()


def track_cursor(window_title: str):
    print(f"\n{'='*55}")
    print(f"  Cursor Tracker — ventana: '{window_title}'")
    print(f"  Presiona Ctrl+C para salir")
    print(f"{'='*55}\n")

    last_pos = (-1, -1)

    while True:
        win = find_window(window_title)

        if win is None:
            print(f"\r  ⚠  Ventana '{window_title}' no encontrada. Esperando...  ", end="", flush=True)
            time.sleep(1)
            continue

        # Coordenadas absolutas del cursor en pantalla
        abs_x, abs_y = pyautogui.position()

        # Posición relativa a la ventana
        rel_x = abs_x - win.left
        rel_y = abs_y - win.top

        # Solo imprimir si el cursor se movió
        if (rel_x, rel_y) != last_pos:
            last_pos = (rel_x, rel_y)

            # Indicar si el cursor está dentro o fuera de la ventana
            inside = (0 <= rel_x <= win.width) and (0 <= rel_y <= win.height)
            status = "✅ DENTRO " if inside else "❌ FUERA  "

            print(
                f"\r  {status} | "
                f"Ventana: ({win.left},{win.top}) {win.width}x{win.height} | "
                f"Cursor absoluto: ({abs_x:4d},{abs_y:4d}) | "
                f"Relativo a ventana: ({rel_x:4d},{rel_y:4d})    ",
                end="",
                flush=True
            )

        time.sleep(REFRESH_RATE)


if __name__ == "__main__":
    list_open_windows()
    track_cursor(WINDOW_TITLE)
