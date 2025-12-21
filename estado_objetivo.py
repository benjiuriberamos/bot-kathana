"""
Módulo de estado compartido para el objetivo.
Process-safe que mantiene el tipo de objetivo actual usando multiprocessing.

Tipos de objetivo:
- NULO: No hay objetivo (texto OCR vacío)
- MOB: Objetivo es un mob de la lista
- DROP: Objetivo es un item dropeado
"""
import multiprocessing
import threading
import time
from enum import Enum


class TipoObjetivo(Enum):
    """Enumeración de tipos de objetivo."""
    NULO = "nulo"
    MOB = "mob"
    DROP = "drop"


class EstadoObjetivo:
    """
    Clase para manejar el estado del objetivo.
    Process-safe para uso en paralelo entre múltiples procesos usando multiprocessing.Manager.
    """
    _instance = None
    _init_lock = None
    _manager = None
    
    def __new__(cls):
        # Usar threading.Lock para el singleton (solo se crea una vez en el proceso principal)
        import threading as thread_module
        if not hasattr(cls, '_init_lock') or cls._init_lock is None:
            cls._init_lock = thread_module.Lock()
        
        if cls._instance is None:
            with cls._init_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._inicializar()
        return cls._instance
    
    def _inicializar(self):
        """Inicializa el estado usando multiprocessing.Manager."""
        # Crear manager si no existe (solo en el proceso principal)
        if multiprocessing.current_process().name == 'MainProcess':
            if EstadoObjetivo._manager is None:
                EstadoObjetivo._manager = multiprocessing.Manager()
        else:
            return
        
        # Usar un diccionario compartido para todo el estado (más eficiente para strings)
        self._estado = EstadoObjetivo._manager.dict({
            'tipo': TipoObjetivo.NULO.value,
            'tipo_anterior': TipoObjetivo.NULO.value,
            'nombre': '',
            'nombre_coincidente': '',
            'similitud': 0.0,
            'timestamp_cambio': time.time(),
            'ejecutando_accion_loot': False,
        })
        
        # Control de procesos - por defecto todos activos
        self._procesos_activos = EstadoObjetivo._manager.dict({
            'autocuracion': True, # Siempre verdadero
            'detector_ocr': True, # Siempre verdadero
            'habilidades': False,
            'observador_objetivo': True,
            'mob_trabado': False,
            'recoger_drop': False,
        })

        self._procesos_activos_default = ['autocuracion','detector_ocr']
        
        # Lock para sincronización (ahora es multiprocessing.Lock)
        self._lock = multiprocessing.Lock()
    
    # ============================================================
    # Control de procesos
    # ============================================================
    
    def pausar_todos_los_hilos_excepto(self, nombre_hilo: str):
        """Pausa todos los procesos excepto el proceso especificado."""
        with self._lock:
            # Primero activar el proceso especificado
            if nombre_hilo in self._procesos_activos:
                self._procesos_activos[nombre_hilo] = True
            # Luego pausar los demás (excepto los que son default)
            for proceso in self._procesos_activos:
                if proceso != nombre_hilo and proceso not in self._procesos_activos_default:
                    self._procesos_activos[proceso] = False
            print(f"[ESTADO] ⏸️  Todos los procesos PAUSADOS excepto {nombre_hilo}")
    
    def activar_hilo(self, nombre_hilo: str):
        """Activa un proceso."""
        with self._lock:
            self._procesos_activos[nombre_hilo] = True
            print(f"[ESTADO] ▶️  Proceso {nombre_hilo} ACTIVADO")

    def hilo_activo(self, nombre_hilo: str) -> bool:
        """Verifica si un proceso está activo."""
        with self._lock:
            return self._procesos_activos.get(nombre_hilo, True)
    
    def pausar_todos_los_hilos(self):
        """Pausa todos los procesos."""
        with self._lock:
            for proceso in self._procesos_activos:
                self._procesos_activos[proceso] = False
            print("[ESTADO] ⏸️  Todos los procesos PAUSADOS")
    
    def reactivar_todos_los_hilos(self):
        """Reactiva todos los procesos."""
        with self._lock:
            for proceso in self._procesos_activos:
                self._procesos_activos[proceso] = True
            print("[ESTADO] ▶️  Todos los procesos REACTIVADOS")
    
    @property
    def ejecutando_loot(self) -> bool:
        """Retorna True si se está ejecutando la acción de loot."""
        return self._estado['ejecutando_accion_loot']
    
    def iniciar_accion_loot(self):
        """Marca que se está ejecutando la acción de loot."""
        self._estado['ejecutando_accion_loot'] = True
    
    def finalizar_accion_loot(self):
        """Marca que terminó la acción de loot."""
        self._estado['ejecutando_accion_loot'] = False
    
    def resetear_timestamp(self):
        """Resetea el timestamp del estado actual (reinicia el contador de tiempo)."""
        with self._lock:
            self._estado['timestamp_cambio'] = time.time()
            print("[ESTADO] ⏱️ Timestamp reseteado - Contador vuelve a 0")
    
    # ============================================================
    # Propiedades del estado
    # ============================================================
    
    @property
    def tipo(self) -> TipoObjetivo:
        """Retorna el tipo de objetivo actual."""
        return TipoObjetivo(self._estado['tipo'])
    
    @property
    def tipo_anterior(self) -> TipoObjetivo:
        """Retorna el tipo de objetivo anterior."""
        return TipoObjetivo(self._estado['tipo_anterior'])
    
    @property
    def nombre(self) -> str:
        """Retorna el nombre detectado por OCR."""
        return self._estado['nombre']
    
    @property
    def nombre_coincidente(self) -> str:
        """Retorna el nombre coincidente de la lista (mob o drop)."""
        return self._estado['nombre_coincidente']
    
    @property
    def similitud(self) -> float:
        """Retorna la similitud del match."""
        return self._estado['similitud']
    
    @property
    def timestamp_cambio(self) -> float:
        """Retorna el timestamp del último cambio de estado."""
        return self._estado['timestamp_cambio']
    
    @property
    def tiempo_en_estado_actual(self) -> float:
        """Retorna cuántos segundos lleva en el estado actual."""
        return time.time() - self._estado['timestamp_cambio']
    
    @property
    def es_nulo(self) -> bool:
        """Retorna True si no hay objetivo."""
        return self.tipo == TipoObjetivo.NULO
    
    @property
    def es_mob(self) -> bool:
        """Retorna True si el objetivo es un mob."""
        return self.tipo == TipoObjetivo.MOB
    
    @property
    def es_drop(self) -> bool:
        """Retorna True si el objetivo es un drop."""
        return self.tipo == TipoObjetivo.DROP
    
    # ============================================================
    # Métodos para establecer estado
    # ============================================================
    
    def establecer_nulo(self) -> bool:
        """
        Establece que no hay objetivo.
        
        Returns:
            True si hubo transición MOB→NULO (mob murió)
        """
        with self._lock:
            transicion_mob_a_nulo = (self._estado['tipo'] == TipoObjetivo.MOB.value)
            
            if self._estado['tipo'] != TipoObjetivo.NULO.value:
                self._estado['tipo_anterior'] = self._estado['tipo']
                self._estado['timestamp_cambio'] = time.time()
            
            self._estado['tipo'] = TipoObjetivo.NULO.value
            self._estado['nombre'] = ''
            self._estado['nombre_coincidente'] = ''
            self._estado['similitud'] = 0.0
        
        # Mover print fuera del lock para reducir tiempo de retención
        if transicion_mob_a_nulo:
            print("[ESTADO] Objetivo: NULO (MOB MURIÓ - Ejecutar loot)")
        else:
            print("[ESTADO] Objetivo: NULO (sin objetivo)")
        
        return transicion_mob_a_nulo
    
    def establecer_mob(self, nombre_detectado: str, nombre_coincidente: str, similitud: float):
        """
        Establece que el objetivo es un mob.
        
        Args:
            nombre_detectado: Nombre detectado por OCR
            nombre_coincidente: Nombre del mob de la lista
            similitud: Porcentaje de similitud (0-1)
        """
        with self._lock:
            cambio = self._estado['tipo'] != TipoObjetivo.MOB.value or self._estado['nombre_coincidente'] != nombre_coincidente
            if cambio:
                self._estado['tipo_anterior'] = self._estado['tipo']
                self._estado['timestamp_cambio'] = time.time()
            self._estado['tipo'] = TipoObjetivo.MOB.value
            self._estado['nombre'] = nombre_detectado or ''
            self._estado['nombre_coincidente'] = nombre_coincidente or ''
            self._estado['similitud'] = similitud
        
        # Mover print fuera del lock para reducir tiempo de retención
        if cambio:
            print(f"[ESTADO] Objetivo: MOB - {nombre_coincidente} ({similitud*100:.1f}%)")
    
    def establecer_drop(self, nombre_detectado: str, nombre_coincidente: str, similitud: float):
        """
        Establece que el objetivo es un item dropeado.
        
        Args:
            nombre_detectado: Nombre detectado por OCR
            nombre_coincidente: Nombre del item de la lista
            similitud: Porcentaje de similitud (0-1)
        """
        with self._lock:
            cambio = self._estado['tipo'] != TipoObjetivo.DROP.value or self._estado['nombre_coincidente'] != nombre_coincidente
            if cambio:
                self._estado['tipo_anterior'] = self._estado['tipo']
                self._estado['timestamp_cambio'] = time.time()
            self._estado['tipo'] = TipoObjetivo.DROP.value
            self._estado['nombre'] = nombre_detectado or ''
            self._estado['nombre_coincidente'] = nombre_coincidente or ''
            self._estado['similitud'] = similitud
        
        # Mover print fuera del lock para reducir tiempo de retención
        if cambio:
            print(f"[ESTADO] Objetivo: DROP - {nombre_coincidente} ({similitud*100:.1f}%)")
    
    def obtener_info(self) -> dict:
        """
        Retorna toda la información del estado actual.
        
        Returns:
            Diccionario con toda la información del objetivo
        """
        # Calcular tiempo fuera del lock para minimizar tiempo de retención
        tiempo_actual = time.time()
        with self._lock:
            return {
                'tipo': TipoObjetivo(self._estado['tipo']),
                'tipo_anterior': TipoObjetivo(self._estado['tipo_anterior']),
                'nombre': self._estado['nombre'] if self._estado['nombre'] else None,
                'nombre_coincidente': self._estado['nombre_coincidente'] if self._estado['nombre_coincidente'] else None,
                'similitud': self._estado['similitud'],
                'tiempo_en_estado': tiempo_actual - self._estado['timestamp_cambio'],
                'ejecutando_loot': self._estado['ejecutando_accion_loot'],
            }


# Instancia global del estado
estado = EstadoObjetivo()
