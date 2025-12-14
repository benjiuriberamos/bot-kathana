"""
Módulo de estado compartido para el objetivo.
Singleton thread-safe que mantiene el tipo de objetivo actual.

Tipos de objetivo:
- NULO: No hay objetivo (texto OCR vacío)
- MOB: Objetivo es un mob de la lista
- DROP: Objetivo es un item dropeado
"""
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
    Clase singleton para manejar el estado del objetivo.
    Thread-safe para uso en paralelo entre múltiples hilos.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._inicializar()
        return cls._instance
    
    def _inicializar(self):
        """Inicializa el estado."""
        self._tipo = TipoObjetivo.NULO
        self._tipo_anterior = TipoObjetivo.NULO
        self._nombre = None
        self._nombre_coincidente = None
        self._similitud = 0.0
        self._timestamp_cambio = time.time()
        # Usar un solo RLock para evitar deadlocks y permitir reentrancia
        self._lock = threading.RLock()
        
        # Control de hilos - por defecto todos activos
        self._hilos_activos = {
            'autocuracion': True, # Siempre verdadero
            'detector_ocr': True, # Siempre verdadero
            'habilidades': False,
            'observador_objetivo': True,
            'mob_trabado': False,
            'recoger_drop': False,
        }

        self._hilos_activos_default = ['autocuracion','detector_ocr']
        
        # Flag para indicar que se está ejecutando acción de loot
        self._ejecutando_accion_loot = False
    
    # ============================================================
    # Control de hilos
    # ============================================================
    
    def pausar_todos_los_hilos_excepto(self, nombre_hilo: str):
        """Pausa todos los hilos excepto el hilo especificado."""
        with self._lock:
            # Primero activar el hilo especificado
            if nombre_hilo in self._hilos_activos:
                self._hilos_activos[nombre_hilo] = True
            # Luego pausar los demás (excepto los que son default)
            for hilo in self._hilos_activos:
                if hilo != nombre_hilo and hilo not in self._hilos_activos_default:
                    self._hilos_activos[hilo] = False
            print(f"[ESTADO] ⏸️  Todos los hilos PAUSADOS excepto {nombre_hilo}")
    
    def activar_hilo(self, nombre_hilo: str):
        """Activa un hilo."""
        with self._lock:
            self._hilos_activos[nombre_hilo] = True
            print(f"[ESTADO] ▶️  Hilo {nombre_hilo} ACTIVADO")

    def hilo_activo(self, nombre_hilo: str) -> bool:
        """Verifica si un hilo está activo."""
        with self._lock:
            return self._hilos_activos.get(nombre_hilo, True)
    
    def pausar_todos_los_hilos(self):
        """Pausa todos los hilos."""
        with self._lock:
            for hilo in self._hilos_activos:
                self._hilos_activos[hilo] = False
            print("[ESTADO] ⏸️  Todos los hilos PAUSADOS")
    
    def reactivar_todos_los_hilos(self):
        """Reactiva todos los hilos."""
        with self._lock:
            for hilo in self._hilos_activos:
                self._hilos_activos[hilo] = True
            print("[ESTADO] ▶️  Todos los hilos REACTIVADOS")
    
    @property
    def ejecutando_loot(self) -> bool:
        """Retorna True si se está ejecutando la acción de loot."""
        with self._lock:
            return self._ejecutando_accion_loot
    
    def iniciar_accion_loot(self):
        """Marca que se está ejecutando la acción de loot."""
        with self._lock:
            self._ejecutando_accion_loot = True
    
    def finalizar_accion_loot(self):
        """Marca que terminó la acción de loot."""
        with self._lock:
            self._ejecutando_accion_loot = False
    
    def resetear_timestamp(self):
        """Resetea el timestamp del estado actual (reinicia el contador de tiempo)."""
        with self._lock:
            self._timestamp_cambio = time.time()
            print("[ESTADO] ⏱️ Timestamp reseteado - Contador vuelve a 0")
    
    # ============================================================
    # Propiedades del estado
    # ============================================================
    
    @property
    def tipo(self) -> TipoObjetivo:
        """Retorna el tipo de objetivo actual."""
        with self._lock:
            return self._tipo
    
    @property
    def tipo_anterior(self) -> TipoObjetivo:
        """Retorna el tipo de objetivo anterior."""
        with self._lock:
            return self._tipo_anterior
    
    @property
    def nombre(self) -> str:
        """Retorna el nombre detectado por OCR."""
        with self._lock:
            return self._nombre
    
    @property
    def nombre_coincidente(self) -> str:
        """Retorna el nombre coincidente de la lista (mob o drop)."""
        with self._lock:
            return self._nombre_coincidente
    
    @property
    def similitud(self) -> float:
        """Retorna la similitud del match."""
        with self._lock:
            return self._similitud
    
    @property
    def timestamp_cambio(self) -> float:
        """Retorna el timestamp del último cambio de estado."""
        with self._lock:
            return self._timestamp_cambio
    
    @property
    def tiempo_en_estado_actual(self) -> float:
        """Retorna cuántos segundos lleva en el estado actual."""
        with self._lock:
            return time.time() - self._timestamp_cambio
    
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
            transicion_mob_a_nulo = (self._tipo == TipoObjetivo.MOB)
            
            if self._tipo != TipoObjetivo.NULO:
                self._tipo_anterior = self._tipo
                self._timestamp_cambio = time.time()
            
            self._tipo = TipoObjetivo.NULO
            self._nombre = None
            self._nombre_coincidente = None
            self._similitud = 0.0
        
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
            cambio = self._tipo != TipoObjetivo.MOB or self._nombre_coincidente != nombre_coincidente
            if cambio:
                self._tipo_anterior = self._tipo
                self._timestamp_cambio = time.time()
            self._tipo = TipoObjetivo.MOB
            self._nombre = nombre_detectado
            self._nombre_coincidente = nombre_coincidente
            self._similitud = similitud
        
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
            cambio = self._tipo != TipoObjetivo.DROP or self._nombre_coincidente != nombre_coincidente
            if cambio:
                self._tipo_anterior = self._tipo
                self._timestamp_cambio = time.time()
            self._tipo = TipoObjetivo.DROP
            self._nombre = nombre_detectado
            self._nombre_coincidente = nombre_coincidente
            self._similitud = similitud
        
        # Mover print fuera del lock para reducir tiempo de retención
        if cambio:
            print(f"[ESTADO] Objetivo: DROP - {nombre_coincidente} ({similitud*100:.1f}%)")
    
    def obtener_info(self) -> dict:
        """
        Retorna toda la información del estado actual.
        
        Returns:
            Diccionario con toda la información del objetivo
        """
        with self._lock:
            # Calcular tiempo fuera del return para minimizar tiempo en lock
            tiempo_actual = time.time()
            return {
                'tipo': self._tipo,
                'tipo_anterior': self._tipo_anterior,
                'nombre': self._nombre,
                'nombre_coincidente': self._nombre_coincidente,
                'similitud': self._similitud,
                'tiempo_en_estado': tiempo_actual - self._timestamp_cambio,
                'ejecutando_loot': self._ejecutando_accion_loot,
            }


# Instancia global del estado
estado = EstadoObjetivo()
