"""
Bot Principal - Kathana
Inicia y coordina todos los hilos de ejecución:
1. Detector OCR: Captura pantalla, procesa OCR, clasifica objetivo
2. Habilidades: Dispara teclas según el objetivo
3. Autocuración: Monitorea vida y maná
4. Observador: Observa el objetivo y presiona E

Uso:
    python bot.py
    
    Presiona Ctrl+C para detener todos los hilos.
"""
import time
import sys

from game_window import GameWindow
from configuracion import (
    GAME_WINDOW_TITLE, 
    MOBS_OBJETIVO, 
    HABILIDADES,
    AUTOCURACION,
    OBSERVADOR_OBJETIVO,
    UMBRAL_SIMILITUD,
    ESCAPE_MOB
)
from estado_objetivo import estado

from hilo_detector_ocr import HiloDetectorOCR
from hilo_habilidades import HiloHabilidades
from hilo_autocuracion import HiloAutocuracion
from hilo_observador_objetivo import HiloObservadorObjetivo
from hilo_recoger_drop import HiloRecogerDrop
from hilo_mob_trabado import HiloMobTrabado


def mostrar_banner():
    """Muestra el banner inicial del bot."""
    print("=" * 70)
    print("                    BOT KATHANA - SISTEMA DE HILOS")
    print("=" * 70)


def mostrar_configuracion():
    """Muestra la configuración actual del bot."""
    print("\n[CONFIGURACIÓN]")
    print("-" * 70)
    
    # Mobs objetivo
    print(f"\n  📋 MOBS OBJETIVO ({len(MOBS_OBJETIVO)}):")
    for mob in MOBS_OBJETIVO:
        print(f"      - {mob}")
    
    # Umbral de similitud
    print(f"\n  🎯 Umbral de similitud: {UMBRAL_SIMILITUD*100:.0f}%")
    
    # Habilidades activas
    activas = [k for k, v in HABILIDADES.items() if v['active']]
    print(f"\n  ⚔️  HABILIDADES ACTIVAS: {', '.join(activas)}")
    
    # Autocuración
    print(f"\n  💚 AUTOCURACIÓN:")
    print(f"      - Vida: Posición ({AUTOCURACION['vida']['x']}, {AUTOCURACION['vida']['y']}) → Tecla '{AUTOCURACION['vida']['tecla']}'")
    print(f"      - Maná: Posición ({AUTOCURACION['mana']['x']}, {AUTOCURACION['mana']['y']}) → Tecla '{AUTOCURACION['mana']['tecla']}'")
    
    # Observador
    print(f"\n  👁️  OBSERVADOR DE OBJETIVO:")
    print(f"      - Timeout DROP: {OBSERVADOR_OBJETIVO['timeout_drop']}s")
    
    print("\n" + "-" * 70)


def mostrar_hilos():
    """Muestra información sobre los hilos."""
    print("\n[HILOS DE EJECUCIÓN]")
    print("-" * 70)
    print("  1️⃣  DETECTOR OCR     - Captura pantalla y clasifica objetivos")
    print("  2️⃣  HABILIDADES      - Dispara teclas de habilidades")
    print("  3️⃣  AUTOCURACIÓN     - Monitorea vida y maná")
    print("  4️⃣  OBSERVADOR       - Observa objetivo y presiona E")
    print("  5️⃣  LOOT             - Recoge drop al morir el mob")
    print("  6️⃣  MOB TRABADO      - Ejecuta escape por clics alternados")
    print("-" * 70)


def mostrar_reglas():
    """Muestra las reglas del observador de objetivo."""
    print("\n[REGLAS DEL OBSERVADOR]")
    print("-" * 70)
    print("  • NULO (sin objetivo)  → Presionar E para seleccionar")
    print("  • MOB (mob detectado)  → No presionar E, atacar normalmente")
    print(f"  • DROP (item drop)     → Si > {OBSERVADOR_OBJETIVO['timeout_drop']}s, presionar E")
    print("-" * 70)
    
    print("\n[SECUENCIA DE LOOT]")
    print("-" * 70)
    print("  🎁 Cuando un MOB muere (MOB → NULO):")
    print("     1. Se pausan TODOS los hilos")
    print("     2. Se presiona F 3 veces en 1 segundo")
    print("     3. Se reactivan todos los hilos")
    print("-" * 70)
    
    print("\n[SECUENCIA DE ESCAPE]")
    print("-" * 70)
    print(f"  🏃 Cuando un MOB lleva más de {ESCAPE_MOB['timeout_mob']}s:")
    print("     1. Se pausan TODOS los hilos")
    print(f"     2. Se hace clic {ESCAPE_MOB['veces']} veces en {ESCAPE_MOB['duracion_total']}s")
    print(f"     3. Alterna entre {len(ESCAPE_MOB['puntos_clic'])} puntos:")
    for i, punto in enumerate(ESCAPE_MOB['puntos_clic']):
        print(f"        - Punto {i+1}: ({punto['x']}, {punto['y']})")
    print("     4. Se reactivan todos los hilos")
    print("-" * 70)


def main():
    """Función principal del bot."""
    hilos = []
    
    try:
        mostrar_banner()
        
        # Buscar ventana del juego
        print("\n[INICIALIZACIÓN]")
        print("-" * 70)
        print("  Buscando ventana del juego...")
        game_window = GameWindow(GAME_WINDOW_TITLE)
        print(f"  ✅ Ventana encontrada (Handle: {game_window.hwnd})")
        
        mostrar_configuracion()
        mostrar_hilos()
        mostrar_reglas()
        
        # Crear hilos
        print("\n[INICIANDO HILOS]")
        print("-" * 70)
        
        # Hilo 1: Detector OCR
        detector_ocr = HiloDetectorOCR(game_window.hwnd)
        detector_ocr.iniciar()
        hilos.append(detector_ocr)
        print("  ✅ Hilo 1: Detector OCR iniciado")
        
        # Hilo 2: Habilidades
        habilidades = HiloHabilidades(game_window.hwnd)
        habilidades.iniciar()
        hilos.append(habilidades)
        print("  ✅ Hilo 2: Habilidades iniciado")
        
        # Hilo 3: Autocuración
        autocuracion = HiloAutocuracion(game_window.hwnd)
        autocuracion.iniciar()
        hilos.append(autocuracion)
        print("  ✅ Hilo 3: Autocuración iniciado")
        
        # Hilo 4: Observador de objetivo
        observador = HiloObservadorObjetivo(game_window.hwnd)
        observador.iniciar()
        hilos.append(observador)
        print("  ✅ Hilo 4: Observador de objetivo iniciado")

        # Hilo 5: Recoger drop (loot)
        hilo_loot = HiloRecogerDrop(game_window.hwnd)
        hilo_loot.iniciar()
        hilos.append(hilo_loot)
        print("  ✅ Hilo 5: Recoger drop iniciado")

        # Hilo 6: Mob trabado (escape)
        hilo_esc = HiloMobTrabado(game_window.hwnd)
        hilo_esc.iniciar()
        hilos.append(hilo_esc)
        print("  ✅ Hilo 6: Mob trabado iniciado")
        
        print("-" * 70)
        print("\n🚀 BOT EN EJECUCIÓN - Presiona Ctrl+C para detener\n")
        print("=" * 70)
        
        # Loop principal - mostrar estado
        while True:
            info = estado.obtener_info()
            tipo = info['tipo'].value.upper()
            nombre = info['nombre_coincidente'] or 'N/A'
            tiempo = info['tiempo_en_estado']
            similitud = info['similitud'] * 100
            
            # Crear barra de estado
            if info['tipo'].value == 'mob':
                emoji = "⚔️ "
                color_info = f"({similitud:.0f}%)"
            elif info['tipo'].value == 'drop':
                emoji = "🎁"
                color_info = f"({similitud:.0f}%)"
            else:
                emoji = "❓"
                color_info = ""
            
            status = f"{emoji} [{tipo:5s}] {nombre:20s} {color_info:8s} | Tiempo: {tiempo:5.1f}s"
            print(f"\r{status}", end='', flush=True)
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("⏹️  DETENIENDO BOT...")
        print("=" * 70)
        
        # Detener todos los hilos
        for hilo in hilos:
            hilo.detener()
        
        print("\n✅ Todos los hilos detenidos correctamente")
        print("👋 ¡Hasta pronto!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n📋 Asegúrate de que:")
        print(f"   1. El juego esté abierto")
        print(f"   2. El título de la ventana sea: '{GAME_WINDOW_TITLE}'")
        print(f"   3. Tesseract OCR esté instalado")
        
        # Detener hilos en caso de error
        for hilo in hilos:
            try:
                hilo.detener()
            except:
                pass
        
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

