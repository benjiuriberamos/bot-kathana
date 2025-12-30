"""
Interfaz gráfica principal del bot Kathana.
Interfaz de escritorio con PyQt5 para configurar y controlar el bot.
"""
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
    QListWidget, QListWidgetItem, QCheckBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QFileDialog, QGroupBox, QGridLayout, QTextEdit
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from config_manager import (
    obtener_configuracion_completa, guardar_configuracion, aplicar_configuracion_a_modulo
)
from bot_controller import BotController


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
        
        # Región OCR
        group = QGroupBox("Región de Captura OCR")
        grid = QGridLayout()
        
        ocr_region = self.config.get('OCR_REGION', {})
        grid.addWidget(QLabel("Left Offset:"), 0, 0)
        self.ocr_left = QSpinBox()
        self.ocr_left.setRange(0, 2000)
        self.ocr_left.setValue(ocr_region.get('left_offset', 5))
        grid.addWidget(self.ocr_left, 0, 1)
        
        grid.addWidget(QLabel("Top Offset:"), 1, 0)
        self.ocr_top = QSpinBox()
        self.ocr_top.setRange(0, 2000)
        self.ocr_top.setValue(ocr_region.get('top_offset', 90))
        grid.addWidget(self.ocr_top, 1, 1)
        
        grid.addWidget(QLabel("Width:"), 2, 0)
        self.ocr_width = QSpinBox()
        self.ocr_width.setRange(1, 2000)
        self.ocr_width.setValue(ocr_region.get('width', 150))
        grid.addWidget(self.ocr_width, 2, 1)
        
        grid.addWidget(QLabel("Height:"), 3, 0)
        self.ocr_height = QSpinBox()
        self.ocr_height.setRange(1, 2000)
        self.ocr_height.setValue(ocr_region.get('height', 15))
        grid.addWidget(self.ocr_height, 3, 1)
        
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
            'OCR_REGION': {
                'left_offset': self.ocr_left.value(),
                'top_offset': self.ocr_top.value(),
                'width': self.ocr_width.value(),
                'height': self.ocr_height.value(),
            },
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
    """Pestaña de configuración de Autocuración."""
    
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        autocuracion = self.config.get('AUTOCURACION', {})
        
        # Vida
        group_vida = QGroupBox("Vida")
        grid_vida = QGridLayout()
        
        vida_config = autocuracion.get('vida', {})
        grid_vida.addWidget(QLabel("Posición X:"), 0, 0)
        self.vida_x = QSpinBox()
        self.vida_x.setRange(0, 2000)
        self.vida_x.setValue(vida_config.get('x', 128))
        grid_vida.addWidget(self.vida_x, 0, 1)
        
        grid_vida.addWidget(QLabel("Posición Y:"), 1, 0)
        self.vida_y = QSpinBox()
        self.vida_y.setRange(0, 2000)
        self.vida_y.setValue(vida_config.get('y', 62))
        grid_vida.addWidget(self.vida_y, 1, 1)
        
        grid_vida.addWidget(QLabel("Teclas (separadas por coma):"), 2, 0)
        teclas_vida = vida_config.get('tecla', [])
        if isinstance(teclas_vida, list):
            teclas_str = ','.join(teclas_vida)
        else:
            teclas_str = str(teclas_vida)
        self.vida_teclas = QLineEdit(teclas_str)
        grid_vida.addWidget(self.vida_teclas, 2, 1)
        
        grid_vida.addWidget(QLabel("Intervalo con vida (s):"), 3, 0)
        self.vida_intervalo_con = QDoubleSpinBox()
        self.vida_intervalo_con.setRange(0.0, 60.0)
        self.vida_intervalo_con.setSingleStep(0.1)
        self.vida_intervalo_con.setDecimals(2)
        self.vida_intervalo_con.setValue(vida_config.get('intervalo_con', 1.0))
        grid_vida.addWidget(self.vida_intervalo_con, 3, 1)
        
        grid_vida.addWidget(QLabel("Intervalo sin vida (s):"), 4, 0)
        self.vida_intervalo_sin = QDoubleSpinBox()
        self.vida_intervalo_sin.setRange(0.0, 60.0)
        self.vida_intervalo_sin.setSingleStep(0.1)
        self.vida_intervalo_sin.setDecimals(2)
        self.vida_intervalo_sin.setValue(vida_config.get('intervalo_sin', 0.5))
        grid_vida.addWidget(self.vida_intervalo_sin, 4, 1)
        
        group_vida.setLayout(grid_vida)
        layout.addWidget(group_vida)
        
        # Maná
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
    
    def obtener_valores(self) -> dict:
        teclas_vida = [t.strip() for t in self.vida_teclas.text().split(',') if t.strip()]
        return {
            'AUTOCURACION': {
                'vida': {
                    'x': self.vida_x.value(),
                    'y': self.vida_y.value(),
                    'tecla': teclas_vida,
                    'intervalo_con': self.vida_intervalo_con.value(),
                    'intervalo_sin': self.vida_intervalo_sin.value(),
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
        self.tabla_timeouts.setColumnCount(2)
        self.tabla_timeouts.setHorizontalHeaderLabels(["Mob", "Timeout (s)"])
        self.tabla_timeouts.horizontalHeader().setStretchLastSection(True)
        
        self.tabla_timeouts.setRowCount(len(escape_by_mob))
        row = 0
        for mob, timeout in escape_by_mob.items():
            self.tabla_timeouts.setItem(row, 0, QTableWidgetItem(mob))
            self.tabla_timeouts.setItem(row, 1, QTableWidgetItem(str(timeout)))
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
        mob, ok1 = QInputDialog.getText(self, "Agregar Timeout", "Nombre del mob:")
        if ok1 and mob:
            timeout, ok2 = QInputDialog.getDouble(self, "Agregar Timeout", "Timeout (segundos):", 15.0, 0.0, 300.0)
            if ok2:
                row = self.tabla_timeouts.rowCount()
                self.tabla_timeouts.insertRow(row)
                self.tabla_timeouts.setItem(row, 0, QTableWidgetItem(mob))
                self.tabla_timeouts.setItem(row, 1, QTableWidgetItem(str(timeout)))
    
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
            timeout_str = self.tabla_timeouts.item(row, 1).text()
            try:
                timeout = float(timeout_str)
                escape_by_mob[mob] = timeout
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
                'puntos_clic': puntos,
                'veces': self.veces.value(),
                'duracion_total': self.duracion_total.value(),
            },
            'ESCAPE_BY_MOB': escape_by_mob,
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
        
        self.tab_items = ListaEditableTab(self.config, 'DROP_ITEMS_OBJETIVO', 'Item')
        self.tabs.addTab(self.tab_items, "Items Drop")
        
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
        ocr_region = config.get('OCR_REGION', {})
        self.tab_general.ocr_left.setValue(ocr_region.get('left_offset', 5))
        self.tab_general.ocr_top.setValue(ocr_region.get('top_offset', 90))
        self.tab_general.ocr_width.setValue(ocr_region.get('width', 150))
        self.tab_general.ocr_height.setValue(ocr_region.get('height', 15))
        self.tab_general.umbral.setValue(config.get('UMBRAL_SIMILITUD', 0.70))
        
        # Actualizar pestaña Mobs
        self.tab_mobs.lista.clear()
        for mob in config.get('MOBS_OBJETIVO', []):
            if mob:
                self.tab_mobs.lista.addItem(mob)
        
        # Actualizar pestaña Items
        self.tab_items.lista.clear()
        for item in config.get('DROP_ITEMS_OBJETIVO', []):
            if item:
                self.tab_items.lista.addItem(item)
        
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
        self.tab_autocuracion.vida_x.setValue(vida_config.get('x', 128))
        self.tab_autocuracion.vida_y.setValue(vida_config.get('y', 62))
        teclas_vida = vida_config.get('tecla', [])
        if isinstance(teclas_vida, list):
            teclas_str = ','.join(teclas_vida)
        else:
            teclas_str = str(teclas_vida)
        self.tab_autocuracion.vida_teclas.setText(teclas_str)
        self.tab_autocuracion.vida_intervalo_con.setValue(vida_config.get('intervalo_con', 1.0))
        self.tab_autocuracion.vida_intervalo_sin.setValue(vida_config.get('intervalo_sin', 0.5))
        
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
        
        self.tab_escape.lista_puntos.clear()
        puntos = escape_mob.get('puntos_clic', [])
        for punto in puntos:
            texto = f"X: {punto.get('x', 0)}, Y: {punto.get('y', 0)}"
            self.tab_escape.lista_puntos.addItem(texto)
        
        escape_by_mob = config.get('ESCAPE_BY_MOB', {})
        self.tab_escape.tabla_timeouts.setRowCount(len(escape_by_mob))
        row = 0
        for mob, timeout in escape_by_mob.items():
            self.tab_escape.tabla_timeouts.setItem(row, 0, QTableWidgetItem(mob))
            self.tab_escape.tabla_timeouts.setItem(row, 1, QTableWidgetItem(str(timeout)))
            row += 1
    
    def obtener_configuracion_desde_interfaz(self) -> dict:
        """Recopila la configuración actual desde todas las pestañas de la interfaz."""
        config = {}
        
        # Recopilar valores de todas las pestañas
        config.update(self.tab_general.obtener_valores())
        config['MOBS_OBJETIVO'] = self.tab_mobs.obtener_valores()
        config['DROP_ITEMS_OBJETIVO'] = self.tab_items.obtener_valores()
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
            tipo = estado_info['tipo'].upper()
            nombre = estado_info['nombre']
            tiempo = estado_info['tiempo']
            similitud = estado_info['similitud']
            
            if tipo == 'mob':
                emoji = "⚔️"
                info_text = f"{emoji} {tipo}: {nombre} ({similitud:.0f}%) | Tiempo: {tiempo:.1f}s"
            elif tipo == 'drop':
                emoji = "🎁"
                info_text = f"{emoji} {tipo}: {nombre} ({similitud:.0f}%) | Tiempo: {tiempo:.1f}s"
            else:
                emoji = "❓"
                info_text = f"{emoji} {tipo}: {nombre} | Tiempo: {tiempo:.1f}s"
            
            self.info_label.setText(info_text)


def main():
    """Función principal de la aplicación."""
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

