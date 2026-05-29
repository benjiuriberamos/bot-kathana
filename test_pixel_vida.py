import time
import sys
from game_window import GameWindow
from configuracion import GAME_WINDOW_TITLE, ESCAPE_MOB
from hilo_autocuracion import HiloAutocuracion

def test_pixel():
    try:
        print("=" * 60)
        print("PROBADOR DE PIXEL DE VIDA DEL MOB")
        print("=" * 60)
        
        # Buscar ventana del juego
        print(f"\n[INFO] Buscando ventana: '{GAME_WINDOW_TITLE}'...")
        game_window = GameWindow(GAME_WINDOW_TITLE)
        hwnd = game_window.hwnd
        print(f"[OK] Ventana encontrada! HWND: {hwnd}")
        
        # Obtener coordenadas del pixel de vida del mob configurado
        pixel_config = ESCAPE_MOB.get("pixel_vida_mob", {"x": 1, "y": 1})
        print(f"\n[INFO] Coordenadas del pixel configuradas: X={pixel_config['x']}, Y={pixel_config['y']}")
        if pixel_config['x'] == 1 and pixel_config['y'] == 1:
            print("[WARN] El pixel está configurado como (1, 1). Recuerda calibrarlo en la GUI o en config.json")
            
        # Instanciar el lector de vida
        autocuracion = HiloAutocuracion(hwnd)
         
        print("\n[INFO] Leyendo pixel en tiempo real. Presiona Ctrl+C para salir.")
        print("-" * 60)
        
        while True:
            # Obtener el color y el resultado de la función
            tiene_vida, color = autocuracion._tiene_vida(pixel_config['x'], pixel_config['y'])
            
            status = "✅ CON VIDA (Rojo)" if tiene_vida else "❌ SIN VIDA / VACÍO"
            print(f"\rPixel ({pixel_config['x']},{pixel_config['y']}) | Color RGB: {color} | Estado: {status}      ", end="", flush=True)
            
            time.sleep(0.2)
            
    except KeyboardInterrupt:
        print("\n\n[OK] Script detenido por el usuario.")
    except Exception as e:
        print(f"\n[ERROR] {e}")

if __name__ == "__main__":
    test_pixel()
