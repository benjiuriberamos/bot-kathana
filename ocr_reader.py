import threading
import easyocr
import configuracion

class OCRReader:
    """
    Singleton thread-safe para inicializar y ejecutar EasyOCR.
    Evita inicializaciones múltiples de los modelos y colisiones de hilos.
    """
    _instance = None
    _lock = threading.Lock()
    _gpu_enabled = None

    @classmethod
    def get_reader(cls):
        # Obtener el valor actual de GPU desde la configuración
        gpu_config = getattr(configuracion, 'EASYOCR_GPU', True)
        
        # Si la instancia no existe, o si la configuración de GPU cambió, inicializar
        if cls._instance is None or cls._gpu_enabled != gpu_config:
            with cls._lock:
                if cls._instance is None or cls._gpu_enabled != gpu_config:
                    print(f"[OCRReader] Inicializando EasyOCR (idioma: 'en', GPU: {gpu_config})...")
                    cls._instance = easyocr.Reader(['en'], gpu=gpu_config)
                    cls._gpu_enabled = gpu_config
                    print("[OCRReader] EasyOCR inicializado correctamente.")
        return cls._instance

    @classmethod
    def image_to_string(cls, image, allowlist=None) -> str:
        """
        Extrae texto de una imagen y lo devuelve como una cadena con saltos de línea,
        emulando el comportamiento de pytesseract.image_to_string.
        
        Args:
            image: Imagen en formato numpy array (OpenCV), PIL o ruta de archivo
            allowlist: Cadena con caracteres permitidos (ej: '0123456789/')
            
        Returns:
            str: El texto detectado, unido por saltos de línea
        """
        reader = cls.get_reader()
        with cls._lock:
            try:
                if allowlist:
                    results = reader.readtext(image, allowlist=allowlist)
                else:
                    results = reader.readtext(image)
            except Exception as e:
                print(f"[OCRReader] Error al ejecutar readtext: {e}")
                return ""
        
        # Unir las líneas detectadas por EasyOCR
        # Cada resultado es una tupla: (bbox, texto, confianza)
        lineas = [res[1] for res in results]
        return "\n".join(lineas)
