"""
Interfaz gráfica principal del bot Kathana.
Interfaz de escritorio con PyQt5 para configurar y controlar el bot.
"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
    QListWidget, QListWidgetItem, QCheckBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QFileDialog, QGroupBox, QGridLayout, QTextEdit, QFrame,
    QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QFont, QPainter, QPen, QBrush, QColor, QPolygonF

from config_manager import (
    obtener_configuracion_completa, guardar_configuracion, aplicar_configuracion_a_modulo
)
from bot_controller import BotController
from estado_objetivo import estado


class GeneralTab(QWidget):
    """Pestaña de configuración general."""
    
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Título ventana del juego
        group = QGroupBox("Ventana del Juego")
        grid = QGridLayout()
        
        grid.addWidget(QLabel("Título de la ventana:"), 0, 0)
        self.window_title = QLineEdit(self.config.get('GAME_WINDOW_TITLE', ''))
        grid.addWidget(self.window_title, 0, 1)
        
        group.setLayout(grid)
        layout.addWidget(group)
        
        # Tesseract OCR
        group = QGroupBox("Tesseract OCR")
        grid = QGridLayout()
        
        grid.addWidget(QLabel("Ruta de Tesseract:"), 0, 0)
        hbox = QHBoxLayout()
        self.tesseract_path = QLineEdit(self.config.get('TESSERACT_PATH', ''))
        btn_browse = QPushButton("Buscar...")
        btn_browse.clicked.connect(self.buscar_tesseract)
        hbox.addWidget(self.tesseract_path)
        hbox.addWidget(btn_browse)
        grid.addLayout(hbox, 0, 1)
        
        group.setLayout(grid)
        layout.addWidget(group)
        
        # Umbral de similitud
        group = QGroupBox("Umbral de Similitud")
        grid = QGridLayout()
        
        grid.addWidget(QLabel("Umbral (0.0 - 1.0):"), 0, 0)
        self.umbral = QDoubleSpinBox()
        self.umbral.setRange(0.0, 1.0)
        self.umbral.setSingleStep(0.01)
        self.umbral.setDecimals(2)
        self.umbral.setValue(self.config.get('UMBRAL_SIMILITUD', 0.70))
        grid.addWidget(self.umbral, 0, 1)
        
        group.setLayout(grid)
        layout.addWidget(group)
        
        # Notas del programador
        group = QGroupBox("📝 Notas e Información")
        notas_layout = QVBoxLayout()
        
        notas_texto = QTextEdit()
        notas_texto.setReadOnly(True)
        notas_texto.setMaximumHeight(180)
        notas_texto.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
            }
        """)
        notas_texto.setHtml("""
            <style>
                body { font-family: Arial, sans-serif; font-size: 11px; }
                h4 { color: #333; margin: 5px 0; }
                ul { margin: 2px 0 8px 15px; padding: 0; }
                li { margin: 2px 0; }
                .info { color: #0066cc; }
                .warning { color: #cc6600; }
                .auto { color: #28a745; }
            </style>
            <h4>🎯 Región de Captura OCR</h4>
            <ul>
                <li class="auto"><b>✓ Automático:</b> La posición del área de captura se calcula automáticamente según tu configuración de DPI de Windows.</li>
                <li>El bot detecta la altura de la barra de título (varía según DPI) y suma el offset fijo del juego.</li>
                <li>No necesitas configurar nada - funciona en cualquier resolución/DPI.</li>
            </ul>
            <h4>⚙️ Umbral de Similitud</h4>
            <ul>
                <li>Valor entre 0.0 y 1.0 (70-80% recomendado).</li>
                <li>Mayor valor = más estricto (menos falsos positivos).</li>
                <li>Menor valor = más permisivo (detecta más pero puede confundirse).</li>
            </ul>
            <h4 class="warning">⚠️ Requisitos</h4>
            <ul>
                <li>Tesseract OCR debe estar instalado en el sistema.</li>
                <li>El juego debe estar abierto y visible antes de iniciar el bot.</li>
            </ul>
        """)
        notas_layout.addWidget(notas_texto)
        
        group.setLayout(notas_layout)
        layout.addWidget(group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def buscar_tesseract(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Tesseract OCR", "", "Ejecutables (*.exe)"
        )
        if file_path:
            self.tesseract_path.setText(file_path)
    
    def obtener_valores(self) -> dict:
        """Retorna los valores actuales de la pestaña."""
        return {
            'GAME_WINDOW_TITLE': self.window_title.text(),
            'TESSERACT_PATH': self.tesseract_path.text(),
            'UMBRAL_SIMILITUD': self.umbral.value(),
        }


class ListaEditableTab(QWidget):
    """Pestaña base para listas editables (Mobs, Items)."""
    
    def __init__(self, config: dict, key: str, titulo: str):
        super().__init__()
        self.config = config
        self.key = key
        self.titulo = titulo
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Lista
        self.lista = QListWidget()
        items = self.config.get(self.key, [])
        for item in items:
            if item:  # Solo agregar items no vacíos
                self.lista.addItem(item)
        layout.addWidget(self.lista)
        
        # Botones
        hbox = QHBoxLayout()
        btn_agregar = QPushButton("Agregar")
        btn_agregar.clicked.connect(self.agregar_item)
        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.clicked.connect(self.eliminar_item)
        hbox.addWidget(btn_agregar)
        hbox.addWidget(btn_eliminar)
        hbox.addStretch()
        layout.addLayout(hbox)
        
        self.setLayout(layout)
    
    def agregar_item(self):
        from PyQt5.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, f"Agregar {self.titulo}", f"Nombre:")
        if ok and text:
            self.lista.addItem(text)
    
    def eliminar_item(self):
        current = self.lista.currentItem()
        if current:
            self.lista.takeItem(self.lista.row(current))
    
    def obtener_valores(self) -> list:
        """Retorna la lista de valores."""
        items = []
        for i in range(self.lista.count()):
            items.append(self.lista.item(i).text())
        return items


class LootDropTab(QWidget):
    """Pestaña de configuración de Loot/Drop."""
    
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        group = QGroupBox("Configuración de Loot")
        grid = QGridLayout()
        
        loot_config = self.config.get('LOOT_DROP', {})
        
        grid.addWidget(QLabel("Repeticiones F:"), 0, 0)
        self.repeticiones = QSpinBox()
        self.repeticiones.setRange(0, 100)
        self.repeticiones.setValue(loot_config.get('repeticiones_f', 1))
        grid.addWidget(self.repeticiones, 0, 1)
        
        grid.addWidget(QLabel("Intervalo F (segundos):"), 1, 0)
        self.intervalo = QDoubleSpinBox()
        self.intervalo.setRange(0.0, 10.0)
        self.intervalo.setSingleStep(0.1)
        self.intervalo.setDecimals(2)
        self.intervalo.setValue(loot_config.get('intervalo_f', 0.5))
        grid.addWidget(self.intervalo, 1, 1)
        
        group.setLayout(grid)
        layout.addWidget(group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def obtener_valores(self) -> dict:
        return {
            'LOOT_DROP': {
                'repeticiones_f': self.repeticiones.value(),
                'intervalo_f': self.intervalo.value(),
            }
        }


class HabilidadesTab(QWidget):
    """Pestaña de configuración de Habilidades."""
    
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Tabla de habilidades
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["Tecla", "Activa", "Cooldown (s)"])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        
        habilidades = self.config.get('HABILIDADES', {})
        self.tabla.setRowCount(len(habilidades))
        
        row = 0
        for tecla, hab_config in habilidades.items():
            self.tabla.setItem(row, 0, QTableWidgetItem(tecla))
            
            checkbox = QCheckBox()
            checkbox.setChecked(hab_config.get('active', False))
            self.tabla.setCellWidget(row, 1, checkbox)
            
            time_item = QTableWidgetItem(str(hab_config.get('time', 0.0)))
            self.tabla.setItem(row, 2, time_item)
            
            row += 1
        
        layout.addWidget(self.tabla)
        self.setLayout(layout)
    
    def obtener_valores(self) -> dict:
        habilidades = {}
        for row in range(self.tabla.rowCount()):
            tecla = self.tabla.item(row, 0).text()
            checkbox = self.tabla.cellWidget(row, 1)
            active = checkbox.isChecked()
            time_str = self.tabla.item(row, 2).text()
            try:
                time_val = float(time_str)
            except:
                time_val = 0.0
            habilidades[tecla] = {'active': active, 'time': time_val}
        return {'HABILIDADES': habilidades}


class AutocuracionTab(QWidget):
    """Pestaña de configuración de Autocuración con niveles."""
    
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        autocuracion = self.config.get('AUTOCURACION', {})
        
        # ========== VIDA ==========
        group_vida = QGroupBox("Vida - Niveles de Curación")
        vida_layout = QVBoxLayout()
        
        vida_config = autocuracion.get('vida', {})
        
        # Intervalo cuando hay vida
        hbox_intervalo = QHBoxLayout()
        hbox_intervalo.addWidget(QLabel("Intervalo con vida (s):"))
        self.vida_intervalo_con = QDoubleSpinBox()
        self.vida_intervalo_con.setRange(0.0, 60.0)
        self.vida_intervalo_con.setSingleStep(0.1)
        self.vida_intervalo_con.setDecimals(2)
        self.vida_intervalo_con.setValue(vida_config.get('intervalo_con', 1.0))
        hbox_intervalo.addWidget(self.vida_intervalo_con)
        hbox_intervalo.addStretch()
        vida_layout.addLayout(hbox_intervalo)
        
        # Nota explicativa
        nota = QLabel("Cada nivel verifica un píxel. Si no hay vida, ejecuta las teclas de ese nivel. en x puedes poner entre 10 y160")
        nota.setStyleSheet("color: gray; font-style: italic;")
        vida_layout.addWidget(nota)
        
        # Tabla de niveles
        self.tabla_niveles = QTableWidget()
        self.tabla_niveles.setColumnCount(5)
        self.tabla_niveles.setHorizontalHeaderLabels(["Nombre", "X", "Y", "Teclas", "Intervalo (s)"])
        self.tabla_niveles.horizontalHeader().setStretchLastSection(True)
        self.tabla_niveles.setMinimumHeight(150)
        
        # Cargar niveles existentes
        niveles = vida_config.get('niveles', [])
        if not niveles and 'x' in vida_config:
            # Migrar configuración antigua a nuevo formato
            teclas = vida_config.get('tecla', [])
            if isinstance(teclas, str):
                teclas = [teclas]
            niveles = [{
                'nombre': 'Nivel 1',
                'x': vida_config.get('x', 50),
                'y': vida_config.get('y', 62),
                'teclas': teclas,
                'intervalo_sin': vida_config.get('intervalo_sin', 0.5)
            }]
        
        self.tabla_niveles.setRowCount(len(niveles))
        for row, nivel in enumerate(niveles):
            self.tabla_niveles.setItem(row, 0, QTableWidgetItem(nivel.get('nombre', f'Nivel {row+1}')))
            self.tabla_niveles.setItem(row, 1, QTableWidgetItem(str(nivel.get('x', 50))))
            self.tabla_niveles.setItem(row, 2, QTableWidgetItem(str(nivel.get('y', 62))))
            teclas = nivel.get('teclas', [])
            self.tabla_niveles.setItem(row, 3, QTableWidgetItem(','.join(teclas)))
            self.tabla_niveles.setItem(row, 4, QTableWidgetItem(str(nivel.get('intervalo_sin', 0.5))))
        
        vida_layout.addWidget(self.tabla_niveles)
        
        # Botones para agregar/eliminar niveles
        hbox_btns = QHBoxLayout()
        btn_agregar = QPushButton("Agregar Nivel")
        btn_agregar.clicked.connect(self.agregar_nivel_vida)
        btn_eliminar = QPushButton("Eliminar Nivel")
        btn_eliminar.clicked.connect(self.eliminar_nivel_vida)
        hbox_btns.addWidget(btn_agregar)
        hbox_btns.addWidget(btn_eliminar)
        hbox_btns.addStretch()
        vida_layout.addLayout(hbox_btns)
        
        group_vida.setLayout(vida_layout)
        layout.addWidget(group_vida)
        
        # ========== MANÁ (sin cambios) ==========
        group_mana = QGroupBox("Maná")
        grid_mana = QGridLayout()
        
        mana_config = autocuracion.get('mana', {})
        grid_mana.addWidget(QLabel("Posición X:"), 0, 0)
        self.mana_x = QSpinBox()
        self.mana_x.setRange(0, 2000)
        self.mana_x.setValue(mana_config.get('x', 45))
        grid_mana.addWidget(self.mana_x, 0, 1)
        
        grid_mana.addWidget(QLabel("Posición Y:"), 1, 0)
        self.mana_y = QSpinBox()
        self.mana_y.setRange(0, 2000)
        self.mana_y.setValue(mana_config.get('y', 80))
        grid_mana.addWidget(self.mana_y, 1, 1)
        
        grid_mana.addWidget(QLabel("Tecla:"), 2, 0)
        self.mana_tecla = QLineEdit(mana_config.get('tecla', '9'))
        grid_mana.addWidget(self.mana_tecla, 2, 1)
        
        grid_mana.addWidget(QLabel("Intervalo con maná (s):"), 3, 0)
        self.mana_intervalo_con = QDoubleSpinBox()
        self.mana_intervalo_con.setRange(0.0, 60.0)
        self.mana_intervalo_con.setSingleStep(0.1)
        self.mana_intervalo_con.setDecimals(2)
        self.mana_intervalo_con.setValue(mana_config.get('intervalo_con', 1.0))
        grid_mana.addWidget(self.mana_intervalo_con, 3, 1)
        
        grid_mana.addWidget(QLabel("Intervalo sin maná (s):"), 4, 0)
        self.mana_intervalo_sin = QDoubleSpinBox()
        self.mana_intervalo_sin.setRange(0.0, 60.0)
        self.mana_intervalo_sin.setSingleStep(0.1)
        self.mana_intervalo_sin.setDecimals(2)
        self.mana_intervalo_sin.setValue(mana_config.get('intervalo_sin', 0.5))
        grid_mana.addWidget(self.mana_intervalo_sin, 4, 1)
        
        group_mana.setLayout(grid_mana)
        layout.addWidget(group_mana)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def agregar_nivel_vida(self):
        row = self.tabla_niveles.rowCount()
        self.tabla_niveles.insertRow(row)
        self.tabla_niveles.setItem(row, 0, QTableWidgetItem(f"Nivel {row+1}"))
        self.tabla_niveles.setItem(row, 1, QTableWidgetItem("50"))
        self.tabla_niveles.setItem(row, 2, QTableWidgetItem("62"))
        self.tabla_niveles.setItem(row, 3, QTableWidgetItem("0"))
        self.tabla_niveles.setItem(row, 4, QTableWidgetItem("0.5"))
    
    def eliminar_nivel_vida(self):
        current_row = self.tabla_niveles.currentRow()
        if current_row >= 0:
            self.tabla_niveles.removeRow(current_row)
    
    def obtener_valores(self) -> dict:
        # Obtener niveles de vida
        niveles = []
        for row in range(self.tabla_niveles.rowCount()):
            nombre = self.tabla_niveles.item(row, 0).text() if self.tabla_niveles.item(row, 0) else f"Nivel {row+1}"
            try:
                x = int(self.tabla_niveles.item(row, 1).text())
            except:
                x = 50
            try:
                y = int(self.tabla_niveles.item(row, 2).text())
            except:
                y = 62
            teclas_str = self.tabla_niveles.item(row, 3).text() if self.tabla_niveles.item(row, 3) else "0"
            teclas = [t.strip() for t in teclas_str.split(',') if t.strip()]
            try:
                intervalo_sin = float(self.tabla_niveles.item(row, 4).text())
            except:
                intervalo_sin = 0.5
            
            niveles.append({
                'nombre': nombre,
                'x': x,
                'y': y,
                'teclas': teclas,
                'intervalo_sin': intervalo_sin
            })
        
        return {
            'AUTOCURACION': {
                'vida': {
                    'niveles': niveles,
                    'intervalo_con': self.vida_intervalo_con.value(),
                },
                'mana': {
                    'x': self.mana_x.value(),
                    'y': self.mana_y.value(),
                    'tecla': self.mana_tecla.text(),
                    'intervalo_con': self.mana_intervalo_con.value(),
                    'intervalo_sin': self.mana_intervalo_sin.value(),
                }
            }
        }


class ObservadorTab(QWidget):
    """Pestaña de configuración del Observador."""
    
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        group = QGroupBox("Configuración del Observador")
        grid = QGridLayout()
        
        obs_config = self.config.get('OBSERVADOR_OBJETIVO', {})
        
        grid.addWidget(QLabel("Tecla para seleccionar objetivo:"), 0, 0)
        self.tecla_seleccionar = QLineEdit(obs_config.get('tecla_seleccionar', 'E'))
        self.tecla_seleccionar.setMaxLength(10)
        self.tecla_seleccionar.setPlaceholderText("Ej: E, TAB, Q")
        grid.addWidget(self.tecla_seleccionar, 0, 1)
        
        grid.addWidget(QLabel("Timeout DROP (segundos):"), 1, 0)
        self.timeout_drop = QDoubleSpinBox()
        self.timeout_drop.setRange(0.0, 60.0)
        self.timeout_drop.setSingleStep(0.1)
        self.timeout_drop.setDecimals(2)
        self.timeout_drop.setValue(obs_config.get('timeout_drop', 3.0))
        grid.addWidget(self.timeout_drop, 1, 1)
        
        grid.addWidget(QLabel("Intervalo de revisión (segundos):"), 2, 0)
        self.intervalo_revision = QDoubleSpinBox()
        self.intervalo_revision.setRange(0.0, 10.0)
        self.intervalo_revision.setSingleStep(0.01)
        self.intervalo_revision.setDecimals(3)
        self.intervalo_revision.setValue(obs_config.get('intervalo_revision', 0.1))
        grid.addWidget(self.intervalo_revision, 2, 1)
        
        # Nota de teclas disponibles
        grid.addWidget(QLabel("Teclas disponibles:"), 3, 0)
        grid.addWidget(QLabel("0-9, A-Z, TAB, SPACE, ENTER"), 3, 1)
        
        group.setLayout(grid)
        layout.addWidget(group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def obtener_valores(self) -> dict:
        return {
            'OBSERVADOR_OBJETIVO': {
                'tecla_seleccionar': self.tecla_seleccionar.text().upper().strip(),
                'timeout_drop': self.timeout_drop.value(),
                'intervalo_revision': self.intervalo_revision.value(),
            }
        }


class EscapeTab(QWidget):
    """Pestaña de configuración de Escape (Mob Trabado)."""
    
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        escape_mob = self.config.get('ESCAPE_MOB', {})
        escape_by_mob = self.config.get('ESCAPE_BY_MOB', {})
        
        # Configuración general
        group_general = QGroupBox("Configuración General")
        grid_general = QGridLayout()
        
        grid_general.addWidget(QLabel("Nombre del personaje:"), 0, 0)
        self.pjname = QLineEdit(escape_mob.get('pjname', ''))
        grid_general.addWidget(self.pjname, 0, 1)
        
        grid_general.addWidget(QLabel("Timeout mob (segundos):"), 1, 0)
        self.timeout_mob = QDoubleSpinBox()
        self.timeout_mob.setRange(0.0, 300.0)
        self.timeout_mob.setSingleStep(1.0)
        self.timeout_mob.setDecimals(1)
        self.timeout_mob.setValue(escape_mob.get('timeout_mob', 15.0))
        grid_general.addWidget(self.timeout_mob, 1, 1)
        
        punto_primero = escape_mob.get('punto_click_primero', {})
        grid_general.addWidget(QLabel("Punto click primero X:"), 2, 0)
        self.punto_primero_x = QSpinBox()
        self.punto_primero_x.setRange(0, 2000)
        self.punto_primero_x.setValue(punto_primero.get('x', 405))
        grid_general.addWidget(self.punto_primero_x, 2, 1)
        
        grid_general.addWidget(QLabel("Punto click primero Y:"), 3, 0)
        self.punto_primero_y = QSpinBox()
        self.punto_primero_y.setRange(0, 2000)
        self.punto_primero_y.setValue(punto_primero.get('y', 360))
        grid_general.addWidget(self.punto_primero_y, 3, 1)
        
        grid_general.addWidget(QLabel("Veces de clic:"), 4, 0)
        self.veces = QSpinBox()
        self.veces.setRange(1, 100)
        self.veces.setValue(escape_mob.get('veces', 1))
        grid_general.addWidget(self.veces, 4, 1)
        
        grid_general.addWidget(QLabel("Duración total (segundos):"), 5, 0)
        self.duracion_total = QDoubleSpinBox()
        self.duracion_total.setRange(0.0, 60.0)
        self.duracion_total.setSingleStep(0.1)
        self.duracion_total.setDecimals(2)
        self.duracion_total.setValue(escape_mob.get('duracion_total', 1.0))
        grid_general.addWidget(self.duracion_total, 5, 1)
        
        pixel_vida_mob = escape_mob.get('pixel_vida_mob', {'x': 1, 'y': 1})
        grid_general.addWidget(QLabel("Pixel Vida Mob X:"), 6, 0)
        self.pixel_vida_mob_x = QSpinBox()
        self.pixel_vida_mob_x.setRange(0, 2000)
        self.pixel_vida_mob_x.setValue(pixel_vida_mob.get('x', 1))
        grid_general.addWidget(self.pixel_vida_mob_x, 6, 1)
        
        grid_general.addWidget(QLabel("Pixel Vida Mob Y:"), 7, 0)
        self.pixel_vida_mob_y = QSpinBox()
        self.pixel_vida_mob_y.setRange(0, 2000)
        self.pixel_vida_mob_y.setValue(pixel_vida_mob.get('y', 1))
        grid_general.addWidget(self.pixel_vida_mob_y, 7, 1)
        
        group_general.setLayout(grid_general)
        layout.addWidget(group_general)
        
        # Puntos de clic
        group_puntos = QGroupBox("Puntos de Clic")
        vbox_puntos = QVBoxLayout()
        
        self.lista_puntos = QListWidget()
        puntos = escape_mob.get('puntos_clic', [])
        for punto in puntos:
            texto = f"X: {punto.get('x', 0)}, Y: {punto.get('y', 0)}"
            self.lista_puntos.addItem(texto)
        vbox_puntos.addWidget(self.lista_puntos)
        
        hbox_btns = QHBoxLayout()
        btn_agregar_punto = QPushButton("Agregar Punto")
        btn_agregar_punto.clicked.connect(self.agregar_punto)
        btn_eliminar_punto = QPushButton("Eliminar Punto")
        btn_eliminar_punto.clicked.connect(self.eliminar_punto)
        hbox_btns.addWidget(btn_agregar_punto)
        hbox_btns.addWidget(btn_eliminar_punto)
        hbox_btns.addStretch()
        vbox_puntos.addLayout(hbox_btns)
        
        group_puntos.setLayout(vbox_puntos)
        layout.addWidget(group_puntos)
        
        # Timeouts por mob
        group_timeouts = QGroupBox("Timeouts por Mob")
        vbox_timeouts = QVBoxLayout()
        
        self.tabla_timeouts = QTableWidget()
        self.tabla_timeouts.setColumnCount(5)
        self.tabla_timeouts.setHorizontalHeaderLabels(["Mob", "Timeout (s)", "Vida Normal", "Timeout Elite (s)", "Habs Elite"])
        self.tabla_timeouts.horizontalHeader().setStretchLastSection(True)
        
        self.tabla_timeouts.setRowCount(len(escape_by_mob))
        row = 0
        for mob, config_data in escape_by_mob.items():
            self.tabla_timeouts.setItem(row, 0, QTableWidgetItem(mob))
            if isinstance(config_data, dict):
                timeout = config_data.get("timeout", 15.0)
                vida = config_data.get("vida", 0)
                timeout_elite = config_data.get("tiempo_escape_elite", timeout)
                habilidades_elite = config_data.get("habilidades_elite", "")
            else:
                timeout = config_data
                vida = 0
                timeout_elite = timeout
                habilidades_elite = ""
                
            self.tabla_timeouts.setItem(row, 1, QTableWidgetItem(str(timeout)))
            self.tabla_timeouts.setItem(row, 2, QTableWidgetItem(str(vida)))
            self.tabla_timeouts.setItem(row, 3, QTableWidgetItem(str(timeout_elite)))
            self.tabla_timeouts.setItem(row, 4, QTableWidgetItem(habilidades_elite))
            row += 1
        
        vbox_timeouts.addWidget(self.tabla_timeouts)
        
        hbox_timeouts = QHBoxLayout()
        btn_agregar_timeout = QPushButton("Agregar")
        btn_agregar_timeout.clicked.connect(self.agregar_timeout)
        btn_eliminar_timeout = QPushButton("Eliminar")
        btn_eliminar_timeout.clicked.connect(self.eliminar_timeout)
        hbox_timeouts.addWidget(btn_agregar_timeout)
        hbox_timeouts.addWidget(btn_eliminar_timeout)
        hbox_timeouts.addStretch()
        vbox_timeouts.addLayout(hbox_timeouts)
        
        group_timeouts.setLayout(vbox_timeouts)
        layout.addWidget(group_timeouts)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def agregar_punto(self):
        from PyQt5.QtWidgets import QInputDialog
        x, ok1 = QInputDialog.getInt(self, "Agregar Punto", "Coordenada X:", 0, 0, 2000)
        if ok1:
            y, ok2 = QInputDialog.getInt(self, "Agregar Punto", "Coordenada Y:", 0, 0, 2000)
            if ok2:
                texto = f"X: {x}, Y: {y}"
                self.lista_puntos.addItem(texto)
    
    def eliminar_punto(self):
        current = self.lista_puntos.currentItem()
        if current:
            self.lista_puntos.takeItem(self.lista_puntos.row(current))
    
    def agregar_timeout(self):
        from PyQt5.QtWidgets import QInputDialog
        mob, ok1 = QInputDialog.getText(self, "Agregar", "Nombre del mob:")
        if ok1 and mob:
            timeout, ok2 = QInputDialog.getDouble(self, "Agregar", "Timeout (s):", 15.0, 0.0, 300.0)
            if ok2:
                vida, ok3 = QInputDialog.getInt(self, "Agregar", "Vida Normal:", 0, 0, 999999)
                if ok3:
                    row = self.tabla_timeouts.rowCount()
                    self.tabla_timeouts.insertRow(row)
                    self.tabla_timeouts.setItem(row, 0, QTableWidgetItem(mob))
                    self.tabla_timeouts.setItem(row, 1, QTableWidgetItem(str(timeout)))
                    self.tabla_timeouts.setItem(row, 2, QTableWidgetItem(str(vida)))
                    self.tabla_timeouts.setItem(row, 3, QTableWidgetItem(str(timeout))) # Por defecto mismo timeout
                    self.tabla_timeouts.setItem(row, 4, QTableWidgetItem(""))
    
    def eliminar_timeout(self):
        current_row = self.tabla_timeouts.currentRow()
        if current_row >= 0:
            self.tabla_timeouts.removeRow(current_row)
    
    def obtener_valores(self) -> dict:
        # Puntos de clic
        puntos = []
        for i in range(self.lista_puntos.count()):
            texto = self.lista_puntos.item(i).text()
            # Extraer X e Y del texto "X: 790, Y: 60"
            partes = texto.split(',')
            x = int(partes[0].split(':')[1].strip())
            y = int(partes[1].split(':')[1].strip())
            puntos.append({'x': x, 'y': y})
        
        # Timeouts por mob
        escape_by_mob = {}
        for row in range(self.tabla_timeouts.rowCount()):
            mob = self.tabla_timeouts.item(row, 0).text()
            try:
                timeout = float(self.tabla_timeouts.item(row, 1).text() if self.tabla_timeouts.item(row, 1) else 15.0)
                vida = int(self.tabla_timeouts.item(row, 2).text() if self.tabla_timeouts.item(row, 2) else 0)
                timeout_elite = float(self.tabla_timeouts.item(row, 3).text() if self.tabla_timeouts.item(row, 3) else timeout)
                habilidades = self.tabla_timeouts.item(row, 4).text() if self.tabla_timeouts.item(row, 4) else ""
                
                escape_by_mob[mob] = {
                    "timeout": timeout,
                    "vida": vida,
                    "tiempo_escape_elite": timeout_elite,
                    "habilidades_elite": habilidades
                }
            except:
                pass
        
        return {
            'ESCAPE_MOB': {
                'pjname': self.pjname.text(),
                'timeout_mob': self.timeout_mob.value(),
                'punto_click_primero': {
                    'x': self.punto_primero_x.value(),
                    'y': self.punto_primero_y.value(),
                },
                'pixel_vida_mob': {
                    'x': self.pixel_vida_mob_x.value(),
                    'y': self.pixel_vida_mob_y.value(),
                },
                'puntos_clic': puntos,
                'veces': self.veces.value(),
                'duracion_total': self.duracion_total.value(),
            },
            'ESCAPE_BY_MOB': escape_by_mob,
        }


class MapaVisualizacion(QFrame):
    """Widget que muestra una visualización del mapa con el polígono y la posición actual."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(250, 250)
        self.setMaximumSize(300, 300)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setStyleSheet("background-color: #1a1a2e; border: 2px solid #16213e; border-radius: 5px;")
        
        # Datos del mapa
        self.mapa_size = 1000  # El mapa es 1000x1000
        self.poligono = []
        self.pos_actual = None  # (x, y) o None
        self.dentro_area = True
    
    def set_poligono(self, puntos: list):
        """Establece los puntos del polígono."""
        self.poligono = puntos
        self.update()
    
    def set_posicion(self, x: int, y: int, dentro: bool):
        """Actualiza la posición actual del personaje."""
        self.pos_actual = (x, y)
        self.dentro_area = dentro
        self.update()
    
    def clear_posicion(self):
        """Limpia la posición actual."""
        self.pos_actual = None
        self.update()
    
    def _escalar_punto(self, x: float, y: float) -> tuple:
        """Convierte coordenadas del mapa a coordenadas del widget."""
        margen = 15
        ancho_util = self.width() - 2 * margen
        alto_util = self.height() - 2 * margen
        
        px = margen + (x / self.mapa_size) * ancho_util
        py = margen + (y / self.mapa_size) * alto_util
        return (px, py)
    
    def paintEvent(self, event):
        """Dibuja el mapa, polígono y posición."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        margen = 15
        ancho = self.width()
        alto = self.height()
        
        # Fondo con grid
        painter.setPen(QPen(QColor(40, 40, 60), 1))
        step = (ancho - 2 * margen) / 10
        for i in range(11):
            x = margen + i * step
            painter.drawLine(int(x), margen, int(x), alto - margen)
            y = margen + i * step
            painter.drawLine(margen, int(y), ancho - margen, int(y))
        
        # Borde del área del mapa
        painter.setPen(QPen(QColor(100, 100, 150), 2))
        painter.drawRect(margen, margen, ancho - 2*margen, alto - 2*margen)
        
        # Etiquetas de coordenadas
        painter.setPen(QColor(150, 150, 180))
        painter.setFont(QFont("Arial", 7))
        painter.drawText(margen, alto - 3, "0")
        painter.drawText(ancho - margen - 25, alto - 3, "1000")
        painter.drawText(3, margen + 10, "0")
        painter.drawText(3, alto - margen, "1000")
        
        # Dibujar polígono
        if len(self.poligono) >= 3:
            # Relleno semitransparente
            poly_points = QPolygonF()
            for punto in self.poligono:
                px, py = self._escalar_punto(punto[0], punto[1])
                poly_points.append(QPointF(px, py))
            
            painter.setBrush(QBrush(QColor(0, 255, 100, 40)))
            painter.setPen(QPen(QColor(0, 255, 100), 2))
            painter.drawPolygon(poly_points)
            
            # Dibujar vértices
            painter.setBrush(QBrush(QColor(0, 255, 100)))
            for punto in self.poligono:
                px, py = self._escalar_punto(punto[0], punto[1])
                painter.drawEllipse(int(px) - 4, int(py) - 4, 8, 8)
        
        # Dibujar posición actual
        if self.pos_actual:
            px, py = self._escalar_punto(self.pos_actual[0], self.pos_actual[1])
            
            # Color según si está dentro o fuera
            if self.dentro_area:
                color = QColor(0, 200, 255)  # Cyan si está dentro
            else:
                color = QColor(255, 50, 50)  # Rojo si está fuera
            
            # Círculo exterior
            painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 100)))
            painter.setPen(QPen(color, 2))
            painter.drawEllipse(int(px) - 10, int(py) - 10, 20, 20)
            
            # Punto central
            painter.setBrush(QBrush(color))
            painter.drawEllipse(int(px) - 5, int(py) - 5, 10, 10)
            
            # Mostrar coordenadas
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Arial", 8, QFont.Bold))
            texto = f"({self.pos_actual[0]}, {self.pos_actual[1]})"
            painter.drawText(int(px) + 12, int(py) + 4, texto)
        
        painter.end()


class ControlAreaTab(QWidget):
    """Pestaña de Control de Área - Mantiene al personaje dentro de un polígono."""
    
    def __init__(self, config: dict):
        super().__init__()
        self.config = config.get('CONTROL_AREA', {})
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Layout principal horizontal: izquierda config, derecha mapa
        main_hbox = QHBoxLayout()
        
        # --- Columna izquierda: Configuración ---
        left_layout = QVBoxLayout()
        
        # Habilitado
        group_enabled = QGroupBox("Activación")
        hbox_enabled = QHBoxLayout()
        
        self.checkbox_habilitado = QCheckBox("Habilitar Control de Área")
        self.checkbox_habilitado.setChecked(self.config.get('habilitado', False))
        self.checkbox_habilitado.setStyleSheet("font-weight: bold; font-size: 12px;")
        hbox_enabled.addWidget(self.checkbox_habilitado)
        hbox_enabled.addStretch()
        
        group_enabled.setLayout(hbox_enabled)
        left_layout.addWidget(group_enabled)
        
        # Polígono
        group_poligono = QGroupBox("Polígono de Área Permitida")
        vbox_poligono = QVBoxLayout()
        
        info_poligono = QLabel("Coordenadas del mapa (X / Y del minimapa):")
        info_poligono.setStyleSheet("color: #666;")
        vbox_poligono.addWidget(info_poligono)
        
        self.tabla_poligono = QTableWidget()
        self.tabla_poligono.setColumnCount(2)
        self.tabla_poligono.setHorizontalHeaderLabels(["X", "Y"])
        self.tabla_poligono.horizontalHeader().setStretchLastSection(True)
        self.tabla_poligono.setMaximumHeight(120)
        
        poligono = self.config.get('poligono', [])
        self.tabla_poligono.setRowCount(len(poligono))
        for row, punto in enumerate(poligono):
            self.tabla_poligono.setItem(row, 0, QTableWidgetItem(str(punto[0])))
            self.tabla_poligono.setItem(row, 1, QTableWidgetItem(str(punto[1])))
        
        # Conectar cambios en la tabla para actualizar el mapa
        self.tabla_poligono.itemChanged.connect(self.actualizar_mapa_desde_tabla)
        
        vbox_poligono.addWidget(self.tabla_poligono)
        
        hbox_btns = QHBoxLayout()
        btn_agregar = QPushButton("+ Agregar")
        btn_agregar.clicked.connect(self.agregar_punto)
        btn_eliminar = QPushButton("- Eliminar")
        btn_eliminar.clicked.connect(self.eliminar_punto)
        hbox_btns.addWidget(btn_agregar)
        hbox_btns.addWidget(btn_eliminar)
        hbox_btns.addStretch()
        vbox_poligono.addLayout(hbox_btns)
        
        group_poligono.setLayout(vbox_poligono)
        left_layout.addWidget(group_poligono)
        
        main_hbox.addLayout(left_layout, stretch=1)
        
        # --- Columna derecha: Visualización del Mapa ---
        right_layout = QVBoxLayout()
        
        group_mapa = QGroupBox("🗺️ Visualización del Mapa")
        vbox_mapa = QVBoxLayout()
        
        self.mapa_widget = MapaVisualizacion()
        self.mapa_widget.set_poligono(poligono)
        vbox_mapa.addWidget(self.mapa_widget, alignment=Qt.AlignCenter)
        
        # Label de estado
        self.label_estado = QLabel("Posición: -- / --")
        self.label_estado.setAlignment(Qt.AlignCenter)
        self.label_estado.setStyleSheet("font-size: 11px; color: #888;")
        vbox_mapa.addWidget(self.label_estado)
        
        group_mapa.setLayout(vbox_mapa)
        right_layout.addWidget(group_mapa)
        right_layout.addStretch()
        
        main_hbox.addLayout(right_layout)
        
        layout.addLayout(main_hbox)
        
        # Intervalos
        group_intervalos = QGroupBox("Intervalos de Tiempo")
        grid_intervalos = QGridLayout()
        
        grid_intervalos.addWidget(QLabel("Intervalo lectura (s):"), 0, 0)
        self.intervalo_lectura = QDoubleSpinBox()
        self.intervalo_lectura.setRange(0.1, 10.0)
        self.intervalo_lectura.setSingleStep(0.1)
        self.intervalo_lectura.setDecimals(2)
        self.intervalo_lectura.setValue(self.config.get('intervalo_lectura', 0.5))
        grid_intervalos.addWidget(self.intervalo_lectura, 0, 1)
        
        grid_intervalos.addWidget(QLabel("Intervalo corrección (s):"), 1, 0)
        self.intervalo_correccion = QDoubleSpinBox()
        self.intervalo_correccion.setRange(0.1, 10.0)
        self.intervalo_correccion.setSingleStep(0.1)
        self.intervalo_correccion.setDecimals(2)
        self.intervalo_correccion.setValue(self.config.get('intervalo_correccion', 0.2))
        grid_intervalos.addWidget(self.intervalo_correccion, 1, 1)
        
        grid_intervalos.addWidget(QLabel("Duración movimiento (s):"), 2, 0)
        self.duracion_movimiento = QDoubleSpinBox()
        self.duracion_movimiento.setRange(0.1, 5.0)
        self.duracion_movimiento.setSingleStep(0.1)
        self.duracion_movimiento.setDecimals(2)
        self.duracion_movimiento.setValue(self.config.get('duracion_movimiento', 0.3))
        grid_intervalos.addWidget(self.duracion_movimiento, 2, 1)
        
        group_intervalos.setLayout(grid_intervalos)
        layout.addWidget(group_intervalos)
        
        # Notas
        group_notas = QGroupBox("📝 Notas")
        vbox_notas = QVBoxLayout()
        
        notas = QTextEdit()
        notas.setReadOnly(True)
        notas.setMaximumHeight(120)
        notas.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ddd;")
        notas.setHtml("""
            <style>
                body { font-size: 11px; }
                ul { margin: 5px 0 5px 15px; }
            </style>
            <b>Cómo funciona:</b>
            <ul>
                <li>El bot lee las coordenadas X/Y del minimapa usando OCR.</li>
                <li>Si el personaje sale del polígono, se pausan todas las acciones excepto autocuración.</li>
                <li>El bot presiona W/A/S/D para regresar al centro del polígono.</li>
                <li>Los controles asumen cámara invertida (W=Sur, S=Norte, A=Este, D=Oeste).</li>
            </ul>
        """)
        vbox_notas.addWidget(notas)
        
        group_notas.setLayout(vbox_notas)
        layout.addWidget(group_notas)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def actualizar_mapa_desde_tabla(self):
        """Actualiza el widget del mapa cuando cambian los puntos del polígono."""
        poligono = []
        for row in range(self.tabla_poligono.rowCount()):
            try:
                item_x = self.tabla_poligono.item(row, 0)
                item_y = self.tabla_poligono.item(row, 1)
                if item_x and item_y:
                    x = int(item_x.text())
                    y = int(item_y.text())
                    poligono.append([x, y])
            except:
                pass
        self.mapa_widget.set_poligono(poligono)
    
    def actualizar_posicion(self, x: int, y: int, dentro: bool):
        """Actualiza la posición del personaje en el mapa."""
        self.mapa_widget.set_posicion(x, y, dentro)
        estado_txt = "DENTRO" if dentro else "FUERA"
        color = "#00c853" if dentro else "#ff5252"
        self.label_estado.setText(f"Posición: {x} / {y} - <span style='color:{color}'>{estado_txt}</span>")
    
    def limpiar_posicion(self):
        """Limpia la posición del mapa."""
        self.mapa_widget.clear_posicion()
        self.label_estado.setText("Posición: -- / --")
    
    def agregar_punto(self):
        from PyQt5.QtWidgets import QInputDialog
        x, ok1 = QInputDialog.getInt(self, "Agregar Punto", "Coordenada X del mapa:", 0, 0, 1000)
        if ok1:
            y, ok2 = QInputDialog.getInt(self, "Agregar Punto", "Coordenada Y del mapa:", 0, 0, 1000)
            if ok2:
                row = self.tabla_poligono.rowCount()
                self.tabla_poligono.insertRow(row)
                self.tabla_poligono.setItem(row, 0, QTableWidgetItem(str(x)))
                self.tabla_poligono.setItem(row, 1, QTableWidgetItem(str(y)))
                self.actualizar_mapa_desde_tabla()
    
    def eliminar_punto(self):
        current_row = self.tabla_poligono.currentRow()
        if current_row >= 0:
            self.tabla_poligono.removeRow(current_row)
            self.actualizar_mapa_desde_tabla()
    
    def obtener_valores(self) -> dict:
        # Polígono
        poligono = []
        for row in range(self.tabla_poligono.rowCount()):
            try:
                x = int(self.tabla_poligono.item(row, 0).text())
                y = int(self.tabla_poligono.item(row, 1).text())
                poligono.append([x, y])
            except:
                pass
        
        return {
            'CONTROL_AREA': {
                'habilitado': self.checkbox_habilitado.isChecked(),
                'poligono': poligono,
                'intervalo_lectura': self.intervalo_lectura.value(),
                'intervalo_correccion': self.intervalo_correccion.value(),
                'duracion_movimiento': self.duracion_movimiento.value(),
            }
        }


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación."""
    
    def __init__(self):
        super().__init__()
        self.bot_controller = BotController(status_callback=self.actualizar_estado)
        
        # Cargar configuración desde JSON y aplicarla al módulo
        self.config = obtener_configuracion_completa()
        aplicar_configuracion_a_modulo(self.config)
        
        self.init_ui()
        
        # Timer para actualizar estado
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_estado_periodico)
        self.timer.start(500)  # Actualizar cada 500ms
    
    def init_ui(self):
        self.setWindowTitle("Bot Kathana - Configuración")
        self.setGeometry(100, 100, 900, 700)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Barra de estado superior
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Estado: Detenido")
        self.status_label.setFont(QFont("Arial", 10, QFont.Bold))
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        self.info_label = QLabel("Objetivo: N/A | Tiempo: 0.0s")
        status_layout.addWidget(self.info_label)
        layout.addLayout(status_layout)
        
        # Pestañas
        self.tabs = QTabWidget()
        
        self.tab_general = GeneralTab(self.config)
        self.tabs.addTab(self.tab_general, "General")
        
        self.tab_mobs = ListaEditableTab(self.config, 'MOBS_OBJETIVO', 'Mob')
        self.tabs.addTab(self.tab_mobs, "Mobs Objetivo")
        
        self.tab_loot = LootDropTab(self.config)
        self.tabs.addTab(self.tab_loot, "Loot/Drop")
        
        self.tab_habilidades = HabilidadesTab(self.config)
        self.tabs.addTab(self.tab_habilidades, "Habilidades")
        
        self.tab_autocuracion = AutocuracionTab(self.config)
        self.tabs.addTab(self.tab_autocuracion, "Autocuración")
        
        self.tab_observador = ObservadorTab(self.config)
        self.tabs.addTab(self.tab_observador, "Observador")
        
        self.tab_escape = EscapeTab(self.config)
        self.tabs.addTab(self.tab_escape, "Escape")
        
        layout.addWidget(self.tabs)
        
        # Botones inferiores
        hbox_btns = QHBoxLayout()
        
        btn_guardar = QPushButton("Guardar Configuración")
        btn_guardar.clicked.connect(self.guardar_configuracion)
        hbox_btns.addWidget(btn_guardar)
        
        hbox_btns.addStretch()
        
        self.btn_run_stop = QPushButton("RUN")
        self.btn_run_stop.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_run_stop.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        self.btn_run_stop.clicked.connect(self.toggle_bot)
        hbox_btns.addWidget(self.btn_run_stop)
        
        layout.addLayout(hbox_btns)
        
        central_widget.setLayout(layout)
    
    def guardar_configuracion(self):
        """Guarda la configuración desde todas las pestañas en config.json."""
        try:
            # Obtener configuración actual desde la interfaz
            config = self.obtener_configuracion_desde_interfaz()
            
            # Guardar en JSON
            if guardar_configuracion(config):
                # Aplicar al módulo de configuración
                aplicar_configuracion_a_modulo(config)
                
                # Actualizar la configuración local y recargar la interfaz
                self.config = config
                self.actualizar_interfaz_desde_config(config)
                
                QMessageBox.information(self, "Éxito", "Configuración guardada correctamente y aplicada en tiempo real")
            else:
                QMessageBox.warning(self, "Error", "Error al guardar la configuración")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar: {e}")
    
    def actualizar_interfaz_desde_config(self, config: dict):
        """Actualiza todos los campos de la interfaz con los valores de la configuración."""
        # Actualizar pestaña General
        self.tab_general.window_title.setText(config.get('GAME_WINDOW_TITLE', ''))
        self.tab_general.tesseract_path.setText(config.get('TESSERACT_PATH', ''))
        self.tab_general.umbral.setValue(config.get('UMBRAL_SIMILITUD', 0.70))
        
        # Actualizar pestaña Mobs
        self.tab_mobs.lista.clear()
        for mob in config.get('MOBS_OBJETIVO', []):
            if mob:
                self.tab_mobs.lista.addItem(mob)
        
        # Actualizar pestaña Loot
        loot_config = config.get('LOOT_DROP', {})
        self.tab_loot.repeticiones.setValue(loot_config.get('repeticiones_f', 1))
        self.tab_loot.intervalo.setValue(loot_config.get('intervalo_f', 0.5))
        
        # Actualizar pestaña Habilidades
        habilidades = config.get('HABILIDADES', {})
        self.tab_habilidades.tabla.setRowCount(len(habilidades))
        row = 0
        for tecla, hab_config in habilidades.items():
            self.tab_habilidades.tabla.setItem(row, 0, QTableWidgetItem(tecla))
            checkbox = QCheckBox()
            checkbox.setChecked(hab_config.get('active', False))
            self.tab_habilidades.tabla.setCellWidget(row, 1, checkbox)
            time_item = QTableWidgetItem(str(hab_config.get('time', 0.0)))
            self.tab_habilidades.tabla.setItem(row, 2, time_item)
            row += 1
        
        # Actualizar pestaña Autocuración
        autocuracion = config.get('AUTOCURACION', {})
        vida_config = autocuracion.get('vida', {})
        self.tab_autocuracion.vida_intervalo_con.setValue(vida_config.get('intervalo_con', 1.0))
        
        # Actualizar tabla de niveles de vida
        niveles = vida_config.get('niveles', [])
        if not niveles and 'x' in vida_config:
            # Migrar configuración antigua
            teclas = vida_config.get('tecla', [])
            if isinstance(teclas, str):
                teclas = [teclas]
            niveles = [{
                'nombre': 'Nivel 1',
                'x': vida_config.get('x', 50),
                'y': vida_config.get('y', 62),
                'teclas': teclas,
                'intervalo_sin': vida_config.get('intervalo_sin', 0.5)
            }]
        
        self.tab_autocuracion.tabla_niveles.setRowCount(len(niveles))
        for row, nivel in enumerate(niveles):
            self.tab_autocuracion.tabla_niveles.setItem(row, 0, QTableWidgetItem(nivel.get('nombre', f'Nivel {row+1}')))
            self.tab_autocuracion.tabla_niveles.setItem(row, 1, QTableWidgetItem(str(nivel.get('x', 50))))
            self.tab_autocuracion.tabla_niveles.setItem(row, 2, QTableWidgetItem(str(nivel.get('y', 62))))
            teclas = nivel.get('teclas', [])
            self.tab_autocuracion.tabla_niveles.setItem(row, 3, QTableWidgetItem(','.join(teclas)))
            self.tab_autocuracion.tabla_niveles.setItem(row, 4, QTableWidgetItem(str(nivel.get('intervalo_sin', 0.5))))
        
        mana_config = autocuracion.get('mana', {})
        self.tab_autocuracion.mana_x.setValue(mana_config.get('x', 45))
        self.tab_autocuracion.mana_y.setValue(mana_config.get('y', 80))
        self.tab_autocuracion.mana_tecla.setText(mana_config.get('tecla', '9'))
        self.tab_autocuracion.mana_intervalo_con.setValue(mana_config.get('intervalo_con', 1.0))
        self.tab_autocuracion.mana_intervalo_sin.setValue(mana_config.get('intervalo_sin', 0.5))
        
        # Actualizar pestaña Observador
        obs_config = config.get('OBSERVADOR_OBJETIVO', {})
        self.tab_observador.tecla_seleccionar.setText(obs_config.get('tecla_seleccionar', 'E'))
        self.tab_observador.timeout_drop.setValue(obs_config.get('timeout_drop', 3.0))
        self.tab_observador.intervalo_revision.setValue(obs_config.get('intervalo_revision', 0.1))
        
        # Actualizar pestaña Escape
        escape_mob = config.get('ESCAPE_MOB', {})
        self.tab_escape.pjname.setText(escape_mob.get('pjname', ''))
        self.tab_escape.timeout_mob.setValue(escape_mob.get('timeout_mob', 15.0))
        punto_primero = escape_mob.get('punto_click_primero', {})
        self.tab_escape.punto_primero_x.setValue(punto_primero.get('x', 405))
        self.tab_escape.punto_primero_y.setValue(punto_primero.get('y', 360))
        self.tab_escape.veces.setValue(escape_mob.get('veces', 1))
        self.tab_escape.duracion_total.setValue(escape_mob.get('duracion_total', 1.0))
        
        pixel_vida_mob = escape_mob.get('pixel_vida_mob', {'x': 1, 'y': 1})
        self.tab_escape.pixel_vida_mob_x.setValue(pixel_vida_mob.get('x', 1))
        self.tab_escape.pixel_vida_mob_y.setValue(pixel_vida_mob.get('y', 1))
        
        self.tab_escape.lista_puntos.clear()
        puntos = escape_mob.get('puntos_clic', [])
        for punto in puntos:
            texto = f"X: {punto.get('x', 0)}, Y: {punto.get('y', 0)}"
            self.tab_escape.lista_puntos.addItem(texto)
        
        escape_by_mob = config.get('ESCAPE_BY_MOB', {})
        self.tab_escape.tabla_timeouts.setRowCount(len(escape_by_mob))
        row = 0
        for mob, config_data in escape_by_mob.items():
            self.tab_escape.tabla_timeouts.setItem(row, 0, QTableWidgetItem(mob))
            if isinstance(config_data, dict):
                timeout = config_data.get("timeout", 15.0)
                vida = config_data.get("vida", 0)
                timeout_elite = config_data.get("tiempo_escape_elite", timeout)
                habilidades_elite = config_data.get("habilidades_elite", "")
            else:
                timeout = config_data
                vida = 0
                timeout_elite = timeout
                habilidades_elite = ""
                
            self.tab_escape.tabla_timeouts.setItem(row, 1, QTableWidgetItem(str(timeout)))
            self.tab_escape.tabla_timeouts.setItem(row, 2, QTableWidgetItem(str(vida)))
            self.tab_escape.tabla_timeouts.setItem(row, 3, QTableWidgetItem(str(timeout_elite)))
            self.tab_escape.tabla_timeouts.setItem(row, 4, QTableWidgetItem(habilidades_elite))
            row += 1
        
        # tab_control_area eliminado
    
    def obtener_configuracion_desde_interfaz(self) -> dict:
        """Recopila la configuración actual desde todas las pestañas de la interfaz."""
        config = {}
        
        # Recopilar valores de todas las pestañas
        config.update(self.tab_general.obtener_valores())
        config['MOBS_OBJETIVO'] = self.tab_mobs.obtener_valores()
        config.update(self.tab_loot.obtener_valores())
        config.update(self.tab_habilidades.obtener_valores())
        config.update(self.tab_autocuracion.obtener_valores())
        config.update(self.tab_observador.obtener_valores())
        config.update(self.tab_escape.obtener_valores())
        
        return config
    
    def toggle_bot(self):
        """Inicia o detiene el bot."""
        if self.bot_controller.esta_ejecutando():
            # Detener
            exito, mensaje = self.bot_controller.detener()
            if exito:
                self.btn_run_stop.setText("RUN")
                self.btn_run_stop.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
                self.status_label.setText("Estado: Detenido")
            else:
                QMessageBox.warning(self, "Error", mensaje)
        else:
            # Obtener configuración actual desde la interfaz
            try:
                config = self.obtener_configuracion_desde_interfaz()
                
                # Aplicar directamente al módulo de configuración (sin guardar en JSON)
                aplicar_configuracion_a_modulo(config)
                
                # Actualizar configuración local
                self.config = config
                
                # Iniciar el bot con los valores de la interfaz
                exito, mensaje = self.bot_controller.iniciar()
                if exito:
                    self.btn_run_stop.setText("STOP")
                    self.btn_run_stop.setStyleSheet("background-color: #f44336; color: white; padding: 10px;")
                    self.status_label.setText("Estado: Ejecutando")
                else:
                    QMessageBox.critical(self, "Error", mensaje)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al obtener configuración: {e}")
    
    def actualizar_estado(self, info: dict):
        """Callback para actualizar el estado desde el bot."""
        # Este método se llama desde el bot_controller
        pass
    
    def actualizar_estado_periodico(self):
        """Actualiza el estado periódicamente."""
        if self.bot_controller.esta_ejecutando():
            estado_info = self.bot_controller.obtener_estado()
            tipo = estado_info['tipo'].lower()
            nombre = estado_info['nombre']
            tiempo = estado_info['tiempo']
            similitud = estado_info['similitud']
            es_elite = estado_info.get('es_elite', False)
            
            tag_elite = " [Elite]" if es_elite else ""
            
            if tipo == 'mob':
                emoji = "⚔️"
                info_text = f"{emoji} {tipo}: {nombre}{tag_elite} ({similitud:.0f}%) | Tiempo: {tiempo:.1f}s"
            elif tipo == 'drop':
                emoji = "🎁"
                info_text = f"{emoji} {tipo}: {nombre} ({similitud:.0f}%) | Tiempo: {tiempo:.1f}s"
            else:
                emoji = "❓"
                info_text = f"{emoji} {tipo}: {nombre} | Tiempo: {tiempo:.1f}s"
            
            self.info_label.setText(info_text)
        else:
            # Bot detenido
            pass


def main():
    """Función principal de la aplicación."""
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

