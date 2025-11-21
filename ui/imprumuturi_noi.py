import json
import os
import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QCheckBox, QMessageBox,
    QGraphicsDropShadowEffect, QApplication, QAbstractItemView, QSizePolicy,
    QMainWindow
)
from PyQt5.QtGui import QFont, QColor, QIcon
from PyQt5.QtCore import Qt, QTimer, QSize, QRect

if getattr(sys, 'frozen', False):
    BASE_RESOURCE_PATH = os.path.dirname(sys.executable)
else:
    current_script_path = os.path.abspath(__file__)
    ui_directory = os.path.dirname(current_script_path)
    BASE_RESOURCE_PATH = os.path.dirname(ui_directory)

# Definim căile către bazele de date
DB_DEPCRED = os.path.join(BASE_RESOURCE_PATH, "DEPCRED.db")
DB_MEMBRII = os.path.join(BASE_RESOURCE_PATH, "MEMBRII.db")

# Fișiere JSON separate pentru fiecare mod
JSON_IMPRUMUTURI_ACORDATE = os.path.join(BASE_RESOURCE_PATH, "imprumuturi_noi_acordate.json")
JSON_PRIMA_RATA = os.path.join(BASE_RESOURCE_PATH, "imprumuturi_noi_prima_rata.json")
CONFIG_PATH = os.path.join(BASE_RESOURCE_PATH, "imprumuturi_noi_config.json")


def format_number_ro(value, decimals=0):
    """Formatează număr conform standard RO"""
    if decimals > 0:
        intreg = int(value)
        zecimal = value - intreg
        intreg_formatted = f"{intreg:,}".replace(',', '.')
        zecimal_formatted = f"{zecimal:.{decimals}f}"[2:]
        return f"{intreg_formatted},{zecimal_formatted}"
    else:
        return f"{int(value):,}".replace(',', '.')


class ImprumuturiNoiWidget(QWidget):
    """Widget flotant compact pentru afișarea împrumuturilor noi cu cache și JSON separat"""

    # Moduri de funcționare
    MOD_IMPRUMUTURI_ACORDATE = "imprumuturi_acordate"
    MOD_PRIMA_RATA = "prima_rata"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = None
        self.current_mode = self.MOD_PRIMA_RATA  # Modul implicit

        # Stocare ultimul row selectat pentru restaurare la showEvent
        self._last_selected_row = 0

        # Cache pentru evitarea query-urilor repetitive
        self._cache = {
            self.MOD_IMPRUMUTURI_ACORDATE: None,
            self.MOD_PRIMA_RATA: None
        }

        self.setWindowTitle("Împrumuturi Noi")
        self.setWindowFlags(Qt.Window)

        # Încarcă preferința salvată
        self._load_preferences()

        self._setup_ui()

        # Restaurează geometria salvată DUPĂ setup UI
        self._restore_geometry()

        self.load_data()

    def _get_json_path(self, mod=None):
        """
        Returnează calea către fișierul JSON corespunzător modului.

        Args:
            mod: Modul pentru care se cere calea (None = modul curent)

        Returns:
            str: Calea completă către fișierul JSON
        """
        if mod is None:
            mod = self.current_mode

        if mod == self.MOD_IMPRUMUTURI_ACORDATE:
            return JSON_IMPRUMUTURI_ACORDATE
        else:
            return JSON_PRIMA_RATA

    def _invalidate_cache(self, mod=None):
        """
        Invalidează cache-ul pentru un mod specific sau pentru toate modurile.

        Args:
            mod: Modul pentru care se invalidează cache-ul (None = toate modurile)
        """
        if mod is None:
            # Invalidează toate
            self._cache[self.MOD_IMPRUMUTURI_ACORDATE] = None
            self._cache[self.MOD_PRIMA_RATA] = None
            print("Cache invalidat complet pentru ambele moduri")
        else:
            self._cache[mod] = None
            print(f"Cache invalidat pentru modul: {mod}")

    def _load_preferences(self):
        """Încarcă preferințele salvate din fișierul de configurare"""
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.current_mode = config.get("mod_implicit", self.MOD_PRIMA_RATA)

                    # Încarcă ultima selecție pentru fiecare mod
                    ultima_selectie = config.get("ultima_selectie", {})
                    self._last_selected_row = {
                        self.MOD_IMPRUMUTURI_ACORDATE: ultima_selectie.get(self.MOD_IMPRUMUTURI_ACORDATE, 0),
                        self.MOD_PRIMA_RATA: ultima_selectie.get(self.MOD_PRIMA_RATA, 0)
                    }
                    print(f"Preferință încărcată: {self.current_mode}")
                    print(f"Selecție restaurată: {self._last_selected_row}")
        except Exception as e:
            print(f"Eroare la încărcarea preferințelor: {e}")
            self.current_mode = self.MOD_PRIMA_RATA
            self._last_selected_row = {
                self.MOD_IMPRUMUTURI_ACORDATE: 0,
                self.MOD_PRIMA_RATA: 0
            }

    def _save_preferences(self):
        """Salvează preferințele curente în fișierul de configurare"""
        try:
            # Încarcă configurația existentă pentru a păstra geometria
            config = {}
            if os.path.exists(CONFIG_PATH):
                try:
                    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                except:
                    pass

            # Actualizează modul implicit și selecția
            config["mod_implicit"] = self.current_mode
            config["ultima_selectie"] = {
                self.MOD_IMPRUMUTURI_ACORDATE: self._last_selected_row[self.MOD_IMPRUMUTURI_ACORDATE],
                self.MOD_PRIMA_RATA: self._last_selected_row[self.MOD_PRIMA_RATA]
            }
            config["data_salvare"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"Preferință salvată: {self.current_mode}")
            print(f"Selecție salvată: {self._last_selected_row}")
        except Exception as e:
            print(f"Eroare la salvarea preferințelor: {e}")

    def _save_current_selection(self):
        """Salvează selecția curentă pentru modul curent"""
        try:
            current_row = self.table.currentRow()
            if current_row >= 0:
                self._last_selected_row[self.current_mode] = current_row
                print(f"Selecție salvată pentru {self.current_mode}: rândul {current_row}")

                # Salvează imediat în fișier
                self._save_preferences()
        except Exception as e:
            print(f"Eroare la salvarea selecției: {e}")

    def _restore_geometry(self):
        """Restaurează geometria ferestrei folosind metoda nativă PyQt5"""
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                geometry_base64 = config.get("window_geometry_native")

                if geometry_base64:
                    # Decodifică din base64 și restaurează
                    import base64
                    geometry_bytes = base64.b64decode(geometry_base64)
                    success = self.restoreGeometry(geometry_bytes)

                    if success:
                        print(
                            f"Geometrie restaurată (nativ): {self.size().width()}x{self.size().height()} la ({self.pos().x()}, {self.pos().y()})")
                        return
                    else:
                        print("Restaurare geometrie eșuată, folosesc dimensiuni implicite")
        except Exception as e:
            print(f"Eroare la restaurarea geometriei: {e}")

        # Dacă nu există geometrie salvată sau a apărut o eroare, setează dimensiuni implicite
        self.resize(500, 550)
        print("Dimensiuni implicite setate: 500x550")

    def _save_geometry(self):
        """Salvează geometria completă a ferestrei folosind metoda nativă PyQt5"""
        try:
            # Încarcă configurația existentă
            config = {}
            if os.path.exists(CONFIG_PATH):
                try:
                    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                except:
                    pass

            # Salvează geometria folosind saveGeometry() nativ
            # Convertim QByteArray în base64 pentru stocare în JSON
            geometry_bytes = self.saveGeometry()
            import base64
            geometry_base64 = base64.b64encode(geometry_bytes).decode('utf-8')

            config["window_geometry_native"] = geometry_base64
            config["data_salvare"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            print(
                f"Geometrie salvată (nativ): {self.size().width()}x{self.size().height()} la ({self.pos().x()}, {self.pos().y()})")
        except Exception as e:
            print(f"Eroare la salvarea geometriei: {e}")

    def closeEvent(self, event):
        """Eveniment la închiderea ferestrei - salvează geometria"""
        self._save_geometry()
        super().closeEvent(event)

    def hideEvent(self, event):
        """Eveniment la ascunderea ferestrei - salvează automat starea checkbox-urilor"""
        try:
            # Salvează ultima poziție selectată
            self._save_current_selection()

            # Sincronizează starea checkbox-urilor cu datele JSON înainte de ascundere
            if self.data and "imprumuturi" in self.data:
                for row in range(self.table.rowCount()):
                    checkbox_widget = self.table.cellWidget(row, 1)
                    if checkbox_widget:
                        checkbox = checkbox_widget.findChild(QCheckBox)
                        if checkbox and row < len(self.data["imprumuturi"]):
                            self.data["imprumuturi"][row]["procesat"] = checkbox.isChecked()

                # Salvează modificările în JSON fără a afișa mesaje
                json_path = self._get_json_path(self.current_mode)
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False)

                # Actualizează cache-ul cu noile date
                self._cache[self.current_mode] = self.data

                print(f"Salvare automată în fundal la ascunderea ferestrei pentru modul: {self.current_mode}")
        except Exception as e:
            print(f"Eroare la salvarea automată în fundal: {e}")

        super().hideEvent(event)

    def _activate_main_window(self):
        """Metodă helper pentru activarea ferestrei principale cu întârziere"""
        try:
            # SALVEAZĂ selecția curentă înainte de a ascunde fereastra
            self._save_current_selection()

            for widget in QApplication.topLevelWidgets():
                if isinstance(widget, QMainWindow) and widget.isVisible():
                    widget.raise_()
                    widget.activateWindow()
                    break
        except Exception as e:
            print(f"Eroare la activarea ferestrei principale: {e}")

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Toggle pentru selectarea modului
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(0)

        self.btn_mod_acordate = QPushButton("Împrumuturi Acordate")
        self.btn_mod_acordate.setCheckable(True)
        self.btn_mod_acordate.setFixedHeight(32)
        self.btn_mod_acordate.clicked.connect(lambda: self._switch_mode(self.MOD_IMPRUMUTURI_ACORDATE))

        self.btn_mod_prima_rata = QPushButton("Prima Rată de Stabilit")
        self.btn_mod_prima_rata.setCheckable(True)
        self.btn_mod_prima_rata.setFixedHeight(32)
        self.btn_mod_prima_rata.clicked.connect(lambda: self._switch_mode(self.MOD_PRIMA_RATA))

        # Setăm starea inițială conform modului curent
        if self.current_mode == self.MOD_IMPRUMUTURI_ACORDATE:
            self.btn_mod_acordate.setChecked(True)
        else:
            self.btn_mod_prima_rata.setChecked(True)

        # Stilizare toggle buttons
        self._update_toggle_styles()

        mode_layout.addWidget(self.btn_mod_acordate)
        mode_layout.addWidget(self.btn_mod_prima_rata)

        main_layout.addLayout(mode_layout)

        # Label descriptiv pentru modul curent
        self.mode_description = QLabel()
        self.mode_description.setWordWrap(True)
        self.mode_description.setStyleSheet("""
            QLabel {
                font-size: 9px;
                color: #555;
                padding: 4px 6px;
                background-color: #f0f0f0;
                border-radius: 3px;
                border-left: 3px solid #3498db;
            }
        """)
        self._update_mode_description()
        main_layout.addWidget(self.mode_description)

        # Tabel împrumuturi (2 coloane: Nume și Prenume, Procesat)
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Nume Prenume", "Procesat"])

        # Configurare header tabel
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Nume Prenume ocupă tot spațiul disponibil
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # Procesat dimensiune fixă

        # Setează lățimea pentru coloana checkbox
        self.table.setColumnWidth(1, 80)

        # Configurare comportament tabel pentru navigare celulă cu celulă
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setTabKeyNavigation(True)

        # Politică de dimensionare
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Stilizare tabel
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                gridline-color: #ecf0f1;
                font-size: 10px;
            }
            QTableWidget::item {
                padding: 6px;
                color: #2c3e50;
                background-color: white;
            }
            QTableWidget::item:hover {
                background-color: #e8f4f8;
                cursor: pointer;
            }
            QTableWidget::item:alternate {
                background-color: #f8f9fa;
            }
            QTableWidget::item:selected {
                background-color: #3498db !important;
                color: #2c3e50 !important;
                border: none;
            }
            QTableWidget::item:selected:alternate {
                background-color: #3498db !important;
                color: #2c3e50 !important;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
                font-size: 10px;
            }
        """)

        # Conectare semnal pentru click pe celule - copiere automată în clipboard
        self.table.cellClicked.connect(self._on_table_cell_clicked)

        # Conectare semnal pentru tracking continuu al selecției
        self.table.currentCellChanged.connect(self._on_selection_changed)

        main_layout.addWidget(self.table)

        # Layout pentru butoane și info
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(8)

        # Buton actualizare
        self.btn_refresh = QPushButton("Actualizează")
        self.btn_refresh.setStyleSheet(self._get_button_style("#3498db"))
        self.btn_refresh.clicked.connect(self.refresh_data)
        self.btn_refresh.setFixedHeight(32)

        # Buton salvare
        self.btn_save = QPushButton("Salvează")
        self.btn_save.setStyleSheet(self._get_button_style("#27ae60"))
        self.btn_save.clicked.connect(self.save_status)
        self.btn_save.setFixedHeight(32)

        # Buton ștergere
        self.btn_delete = QPushButton("Șterge")
        self.btn_delete.setStyleSheet(self._get_button_style("#e74c3c"))
        self.btn_delete.clicked.connect(self.delete_list)
        self.btn_delete.setFixedHeight(32)

        bottom_layout.addWidget(self.btn_refresh)
        bottom_layout.addWidget(self.btn_save)
        bottom_layout.addWidget(self.btn_delete)
        bottom_layout.addStretch()

        # Pictogramă info cu tooltip
        self.info_icon = QLabel("ℹ️")
        self.info_icon.setStyleSheet("""
            QLabel {
                font-size: 18px;
                padding: 5px;
                background-color: #e8f4f8;
                border-radius: 12px;
                border: 1px solid #3498db;
            }
        """)
        self.info_icon.setFixedSize(28, 28)
        self.info_icon.setAlignment(Qt.AlignCenter)
        self.info_icon.setToolTip(
            "<b>Instrucțiuni:</b><br>"
            "• <b>Toggle superior</b>: comută între moduri (folosește cache)<br>"
            "• <b>Actualizează</b>: reîncarcă date din baza de date<br>"
            "• <b>Împrumuturi Acordate</b>: listă împrumuturi din luna sursă<br>"
            "• <b>Prima Rată</b>: membri care trebuie să plătească prima rată<br>"
            "• Fiecare mod are propriul JSON și istoric<br>"
            "• Navighează cu <b>TAB</b> sau <b>săgețile</b> (↑↓←→)<br>"
            "• Apasă <b>ENTER</b> pentru a copia în clipboard<br>"
            "• Apasă <b>F12</b> pentru comutare rapidă între ferestre<br>"
        )

        bottom_layout.addWidget(self.info_icon)

        main_layout.addLayout(bottom_layout)

        # Shadow effect pentru fereastră
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

    def _update_toggle_styles(self):
        """Actualizează stilurile butoanelor toggle în funcție de starea lor"""
        # Stil pentru buton activ
        active_style = """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 0px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """

        # Stil pentru buton inactiv
        inactive_style = """
            QPushButton {
                background-color: #ecf0f1;
                color: #555;
                border: 1px solid #bdc3c7;
                border-radius: 0px;
                padding: 6px 12px;
                font-weight: normal;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #d5dbdb;
            }
        """

        # Rotunjim colțurile exterioare
        if self.btn_mod_acordate.isChecked():
            self.btn_mod_acordate.setStyleSheet(
                active_style.replace("border-radius: 0px;", "border-radius: 4px 0px 0px 4px;"))
            self.btn_mod_prima_rata.setStyleSheet(
                inactive_style.replace("border-radius: 0px;", "border-radius: 0px 4px 4px 0px;"))
        else:
            self.btn_mod_acordate.setStyleSheet(
                inactive_style.replace("border-radius: 0px;", "border-radius: 4px 0px 0px 4px;"))
            self.btn_mod_prima_rata.setStyleSheet(
                active_style.replace("border-radius: 0px;", "border-radius: 0px 4px 4px 0px;"))

    def _update_mode_description(self):
        """Actualizează descrierea modului curent"""
        if self.current_mode == self.MOD_IMPRUMUTURI_ACORDATE:
            self.mode_description.setText(
                "Mod: Împrumuturi Acordate - Afișează membrii care au primit împrumuturi noi"
            )
        else:
            self.mode_description.setText(
                "Mod: Prima Rată - Afișează membrii care trebuie să stabilească prima rată"
            )

    def _switch_mode(self, new_mode):
        """Comută între modurile de funcționare (FOLOSEȘTE CACHE)"""
        if self.current_mode == new_mode:
            return  # Deja în acest mod

        print(f"Comutare la modul: {new_mode}")

        # Salvează selecția curentă pentru modul vechi
        self._save_current_selection()

        self.current_mode = new_mode

        # Actualizează starea butoanelor
        self.btn_mod_acordate.setChecked(new_mode == self.MOD_IMPRUMUTURI_ACORDATE)
        self.btn_mod_prima_rata.setChecked(new_mode == self.MOD_PRIMA_RATA)

        # Actualizează stilurile
        self._update_toggle_styles()

        # Actualizează descrierea
        self._update_mode_description()

        # Salvează preferința
        self._save_preferences()

        # Încarcă datele (folosește cache dacă e disponibil)
        self.load_data()

    def _get_button_style(self, color):
        """Generează stilul pentru butoane"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: black;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(color, 40)};
            }}
        """

    def _darken_color(self, hex_color, amount=20):
        """Întunecă o culoare hex"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        new_rgb = tuple(max(0, c - amount) for c in rgb)
        return f"#{''.join([f'{c:02x}' for c in new_rgb])}"

    def _get_latest_month_year(self):
        """
        Găsește cea mai recentă lună/an disponibilă în DEPCRED.
        """
        try:
            with sqlite3.connect(DB_DEPCRED, timeout=30.0) as conn:
                c = conn.cursor()
                c.execute("""
                    SELECT MAX(anul * 12 + luna) as ultima_perioada
                    FROM depcred
                """)
                row = c.fetchone()
                if not row or not row[0]:
                    now = datetime.now()
                    return now.month, now.year

                ultima_perioada = row[0]
                ultima_anul = ultima_perioada // 12
                ultima_luna = ultima_perioada % 12
                if ultima_luna == 0:
                    ultima_luna = 12
                    ultima_anul -= 1

                return ultima_luna, ultima_anul
        except Exception as e:
            print(f"Eroare la găsirea ultimei luni: {e}")
            now = datetime.now()
            return now.month, now.year

    def _detecteaza_imprumuturi_acordate(self, luna_sursa, anul_sursa):
        """
        MOD 1: Detectează împrumuturi acordate în luna sursă.
        Criteriu: IMPR_DEB > 0 în luna sursă

        Returns:
            list: Lista de tupluri (nr_fisa, num_pren, impr_deb, impr_sold)
        """
        try:
            with sqlite3.connect(DB_DEPCRED, timeout=30.0) as conn_d:
                c_d = conn_d.cursor()

                c_d.execute("""
                    SELECT 
                        d.nr_fisa,
                        d.impr_deb,
                        d.impr_sold
                    FROM depcred d
                    WHERE d.anul = ? AND d.luna = ? AND d.impr_deb > 0
                    ORDER BY d.nr_fisa
                """, (anul_sursa, luna_sursa))

                imprumuturi_raw = c_d.fetchall()

            if not imprumuturi_raw:
                return []

            # Obținem numele din MEMBRII.db
            imprumuturi_complete = []
            with sqlite3.connect(DB_MEMBRII, timeout=30.0) as conn_m:
                c_m = conn_m.cursor()

                for nr_fisa, impr_deb, impr_sold in imprumuturi_raw:
                    c_m.execute("""
                        SELECT num_pren 
                        FROM membrii 
                        WHERE nr_fisa = ?
                    """, (nr_fisa,))

                    row = c_m.fetchone()
                    num_pren = row[0] if row else f"Membru {nr_fisa}"

                    imprumuturi_complete.append((nr_fisa, num_pren, impr_deb, impr_sold))

            return imprumuturi_complete

        except Exception as e:
            print(f"Eroare la detectarea împrumuturilor acordate: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _detecteaza_membri_prima_rata(self, luna_tinta, anul_tinta):
        """
        MOD 2: Detectează membrii care trebuie să stabilească prima rată.
        Logică identică cu marcarea "!NOU!" din sume_lunare.py

        Returns:
            list: Lista de tupluri (nr_fisa, num_pren, impr_deb_sursa, impr_sold_tinta)
        """
        try:
            # Calculăm luna sursă
            if luna_tinta == 1:
                luna_sursa = 12
                anul_sursa = anul_tinta - 1
            else:
                luna_sursa = luna_tinta - 1
                anul_sursa = anul_tinta

            with sqlite3.connect(DB_DEPCRED, timeout=30.0) as conn:
                c = conn.cursor()

                # Query complex cu JOIN pentru detectare
                c.execute("""
                    SELECT 
                        tinta.nr_fisa,
                        sursa.impr_deb,
                        tinta.impr_sold
                    FROM depcred AS tinta
                    INNER JOIN depcred AS sursa 
                        ON tinta.nr_fisa = sursa.nr_fisa
                        AND sursa.luna = ? AND sursa.anul = ?
                    WHERE 
                        tinta.luna = ? AND tinta.anul = ?
                        AND sursa.impr_deb > 0
                        AND tinta.impr_sold > 0.005
                        AND (tinta.impr_cred = 0 OR tinta.impr_cred IS NULL)
                        AND (tinta.impr_deb = 0 OR tinta.impr_deb IS NULL)
                    ORDER BY tinta.nr_fisa
                """, (luna_sursa, anul_sursa, luna_tinta, anul_tinta))

                membri_detectati = c.fetchall()

            if not membri_detectati:
                return []

            # Obținem numele din MEMBRII.db
            membri_complete = []
            with sqlite3.connect(DB_MEMBRII, timeout=30.0) as conn_m:
                c_m = conn_m.cursor()

                for nr_fisa, impr_deb_sursa, impr_sold_tinta in membri_detectati:
                    c_m.execute("""
                        SELECT num_pren 
                        FROM membrii 
                        WHERE nr_fisa = ?
                    """, (nr_fisa,))

                    row = c_m.fetchone()
                    num_pren = row[0] if row else f"Membru {nr_fisa}"

                    membri_complete.append((nr_fisa, num_pren, impr_deb_sursa, impr_sold_tinta))

            return membri_complete

        except Exception as e:
            print(f"Eroare la detectarea membrilor cu prima rată: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _genereaza_json(self, imprumuturi_lista, luna, anul, mod):
        """
        Generează fișierul JSON cu lista de împrumuturi pentru modul specificat.
        """
        try:
            suma_totala = sum(imp[2] for imp in imprumuturi_lista)

            json_data = {
                "mod": mod,
                "luna": luna,
                "anul": anul,
                "data_detectare": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_imprumuturi": len(imprumuturi_lista),
                "suma_totala": suma_totala,
                "imprumuturi": [
                    {
                        "nr_fisa": nr_fisa,
                        "num_pren": num_pren,
                        "suma": suma,
                        "impr_sold": impr_sold,
                        "procesat": False
                    }
                    for nr_fisa, num_pren, suma, impr_sold in imprumuturi_lista
                ]
            }

            json_path = self._get_json_path(mod)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

            print(f"JSON generat cu succes: {json_path}")
            print(f"  Mod: {mod}")
            print(f"  Total împrumuturi: {len(imprumuturi_lista)}")
            print(f"  Sumă totală: {suma_totala:,.2f}")

            return True

        except Exception as e:
            print(f"Eroare la generarea JSON: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _actualizeaza_json_existent(self, json_data_existent, imprumuturi_noi_db, luna, anul, mod):
        """
        Actualizează JSON-ul existent prin adăugarea membrilor noi.
        """
        try:
            membri_existenti = {
                imp["nr_fisa"]: imp
                for imp in json_data_existent.get("imprumuturi", [])
            }

            membri_noi = []
            for nr_fisa, num_pren, suma, impr_sold in imprumuturi_noi_db:
                if nr_fisa not in membri_existenti:
                    membri_noi.append({
                        "nr_fisa": nr_fisa,
                        "num_pren": num_pren,
                        "suma": suma,
                        "impr_sold": impr_sold,
                        "procesat": False
                    })

            if not membri_noi:
                print("Niciun membru nou de adăugat în JSON")
                return True, 0

            json_data_existent["imprumuturi"].extend(membri_noi)
            json_data_existent["imprumuturi"].sort(key=lambda x: x["nr_fisa"])
            json_data_existent["total_imprumuturi"] = len(json_data_existent["imprumuturi"])
            json_data_existent["suma_totala"] = sum(imp["suma"] for imp in json_data_existent["imprumuturi"])
            json_data_existent["data_detectare"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            json_data_existent["mod"] = mod

            json_path = self._get_json_path(mod)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data_existent, f, indent=2, ensure_ascii=False)

            print(f"JSON actualizat cu succes: {json_path}")
            print(f"  Membri noi adăugați: {len(membri_noi)}")

            return True, len(membri_noi)

        except Exception as e:
            print(f"Eroare la actualizarea JSON existent: {e}")
            import traceback
            traceback.print_exc()
            return False, 0

    def _verifica_si_genereaza_json(self, force_refresh=False):
        """
        Verifică dacă există împrumuturi și generează/actualizează JSON-ul
        în funcție de modul curent.

        Args:
            force_refresh: Dacă True, ignoră cache-ul și reîncarcă din DB
        """
        try:
            # Verifică cache-ul dacă nu e forțat refresh
            if not force_refresh and self._cache[self.current_mode] is not None:
                print(f"Date încărcate din CACHE pentru modul: {self.current_mode}")
                return True, 0  # Date deja în cache

            print(f"Interogare bază de date pentru modul: {self.current_mode}")

            ultima_luna, ultima_anul = self._get_latest_month_year()

            # Detectăm în funcție de modul curent
            if self.current_mode == self.MOD_IMPRUMUTURI_ACORDATE:
                imprumuturi_db = self._detecteaza_imprumuturi_acordate(ultima_luna, ultima_anul)
                luna_referinta = ultima_luna
                anul_referinta = ultima_anul
            else:
                imprumuturi_db = self._detecteaza_membri_prima_rata(ultima_luna, ultima_anul)
                luna_referinta = ultima_luna
                anul_referinta = ultima_anul

            if not imprumuturi_db:
                print(f"Nu există împrumuturi pentru modul {self.current_mode}")
                return False, 0

            json_path = self._get_json_path(self.current_mode)

            # Verificăm dacă JSON-ul există pentru acest mod
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)

                # Verificăm dacă e pentru aceeași lună/an
                if existing_data.get("luna") == luna_referinta and \
                        existing_data.get("anul") == anul_referinta:
                    print(f"JSON existent pentru {luna_referinta}/{anul_referinta}")
                    succes, membri_noi = self._actualizeaza_json_existent(
                        existing_data, imprumuturi_db, luna_referinta, anul_referinta, self.current_mode
                    )
                    return succes, membri_noi

            # Generăm JSON nou
            succes = self._genereaza_json(imprumuturi_db, luna_referinta, anul_referinta, self.current_mode)
            return succes, len(imprumuturi_db) if succes else 0

        except Exception as e:
            print(f"Eroare la verificare/generare JSON: {e}")
            return False, 0

    def load_data(self, force_refresh=False):
        """
        Încarcă datele din JSON în funcție de modul curent.
        Folosește cache dacă e disponibil, altfel interoghează DB.

        Args:
            force_refresh: Dacă True, ignoră cache-ul și forțează refresh din DB
        """
        try:
            # Verifică cache DOAR dacă nu e forțat refresh
            if not force_refresh and self._cache[self.current_mode] is not None:
                print(f"Încărcare date din CACHE pentru modul: {self.current_mode}")
                self.data = self._cache[self.current_mode]
                imprumuturi = self.data.get("imprumuturi", [])
                self._update_table(imprumuturi)
                return

            # Verifică și generează/actualizează JSON
            json_generat, membri_noi_adaugati = self._verifica_si_genereaza_json(force_refresh)

            json_path = self._get_json_path(self.current_mode)

            if not json_generat or not os.path.exists(json_path):
                mod_text = "împrumuturi acordate" if self.current_mode == self.MOD_IMPRUMUTURI_ACORDATE else "membri cu prima rată de stabilit"
                QMessageBox.information(
                    self,
                    "Fără date",
                    f"Nu există {mod_text} pentru luna curentă.\n\n"
                    f"Datele se detectează automat din baza de date DEPCRED."
                )
                self.data = None
                self._cache[self.current_mode] = None
                self._update_table([])
                return

            if membri_noi_adaugati > 0:
                QMessageBox.information(
                    self,
                    "Listă actualizată",
                    f"Au fost adăugați {membri_noi_adaugati} membri noi.\n\n"
                    f"Statusul 'procesat' al membrilor existenți a fost păstrat."
                )

            # Încarcă JSON-ul
            with open(json_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

            # Salvează în cache
            self._cache[self.current_mode] = self.data
            print(f"Date salvate în CACHE pentru modul: {self.current_mode}")

            imprumuturi = self.data.get("imprumuturi", [])
            self._update_table(imprumuturi)

        except json.JSONDecodeError as e:
            QMessageBox.critical(
                self,
                "Eroare JSON",
                f"Fișierul JSON este corupt:\n{e}\n\nȘterge fișierul și apasă 'Actualizează'."
            )
            self.data = None
            self._cache[self.current_mode] = None
            self._update_table([])
        except Exception as e:
            QMessageBox.critical(
                self,
                "Eroare",
                f"Eroare la încărcarea datelor:\n{e}"
            )
            self.data = None
            self._cache[self.current_mode] = None
            self._update_table([])

    def refresh_data(self):
        """
        Butonul Actualizează: invalidează cache-ul și forțează refresh din DB.
        """
        print("REFRESH FORȚAT - Invalidare cache și reîncărcare din baza de date")
        self._invalidate_cache(self.current_mode)
        self.load_data(force_refresh=True)

    def _update_table(self, imprumuturi):
        """Actualizează tabelul cu datele din listă"""
        self.table.setRowCount(0)

        for imp in imprumuturi:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Coloana 0: Nume Prenume
            num_pren_item = QTableWidgetItem(imp.get("num_pren", ""))
            self.table.setItem(row, 0, num_pren_item)

            # Coloana 1: Checkbox Procesat
            checkbox = QCheckBox()
            checkbox.setChecked(imp.get("procesat", False))
            checkbox.setStyleSheet("""
                QCheckBox {
                    padding: 5px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
            """)

            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)

            self.table.setCellWidget(row, 1, checkbox_widget)

        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 28)

    def _copy_to_clipboard(self, text):
        """Copiază text în clipboard cu feedback vizual"""
        clipboard = QApplication.clipboard()
        clipboard.setText(str(text))

        original_title = self.windowTitle()
        self.setWindowTitle(f"Copiat: {text}")
        QTimer.singleShot(1500, lambda: self.setWindowTitle(original_title))

    def _on_table_cell_clicked(self, row, column):
        """Gestionare click pe celulele tabelului pentru copiere automată în clipboard"""
        # Pentru coloana checkbox (coloana 1), toggle starea
        if column == 1:
            checkbox_widget = self.table.cellWidget(row, 1)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(not checkbox.isChecked())
        # Pentru coloana cu text (coloana 0), copiază conținutul
        else:
            item = self.table.item(row, column)
            if item:
                text = item.text()
                self._copy_to_clipboard(text)

    def _on_selection_changed(self, current_row, current_column, previous_row, previous_column):
        """
        Tracking continuu al selecției pentru persistență precisă.
        Apelat automat la orice schimbare de celulă selectată.
        """
        if current_row >= 0:
            self._last_selected_row[self.current_mode] = current_row
            # Salvăm automat la fiecare schimbare a selecției
            self._save_preferences()

    def _restore_selection(self):
        """Restaurează ultima selecție salvată pentru modul curent"""
        if self.table.rowCount() > 0:
            try:
                # Obține ultima selecție salvată pentru modul curent
                target_row = self._last_selected_row.get(self.current_mode, 0)
        
                # Validează că row-ul salvat este în limita tabelului curent
                if target_row < 0 or target_row >= self.table.rowCount():
                    target_row = 0
        
                # Selectează rândul țintă
                self.table.setCurrentCell(target_row, 0)
        
                # Asigură vizibilitatea prin scroll
                self.table.scrollToItem(self.table.item(target_row, 0), QAbstractItemView.PositionAtCenter)
        
                # Copiază numele în clipboard
                nume_item = self.table.item(target_row, 0)
                if nume_item:
                    nume = nume_item.text()
                    clipboard = QApplication.clipboard()
                    clipboard.setText(nume)
                    print(f"Selecție restaurată pentru {self.current_mode}: rândul {target_row + 1}: {nume}")
        
            except Exception as e:
                print(f"Eroare la restaurarea selecției: {e}")

    def showEvent(self, event):
        """Eveniment la afișarea widget-ului"""
        super().showEvent(event)
        # Folosim un timer scurt pentru a restaura selecția după ce tabelul este complet populat
        QTimer.singleShot(100, self._restore_selection)

    def keyPressEvent(self, event):
        """Gestionare avansată pentru taste"""
        # Interceptare F12 pentru comutare către fereastra principală
        if event.key() == Qt.Key_F12:
            try:
                # Ascunde fereastra curentă
                self.hide()

                # Găsește și activează fereastra principală folosind QTimer pentru siguranță
                QTimer.singleShot(50, self._activate_main_window)

                event.accept()
                return
            except Exception as e:
                print(f"Eroare la comutare către fereastra principală: {e}")
                self.show()
                return

        # Restul logicii existente pentru taste
        current_row = self.table.currentRow()
        current_col = self.table.currentColumn()

        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if current_row >= 0 and current_col >= 0:
                if current_col == 1:
                    checkbox_widget = self.table.cellWidget(current_row, 1)
                    if checkbox_widget:
                        checkbox = checkbox_widget.findChild(QCheckBox)
                        if checkbox:
                            checkbox.setChecked(not checkbox.isChecked())
                else:
                    item = self.table.item(current_row, current_col)
                    if item:
                        text = item.text()
                        self._copy_to_clipboard(text)
            return

        if event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            if current_row >= 0 and current_col >= 0 and current_col != 1:
                item = self.table.item(current_row, current_col)
                if item:
                    text = item.text()
                    self._copy_to_clipboard(text)
            return

        super().keyPressEvent(event)



    def save_status(self):
        """
        Salvează statusul procesat în JSON și INVALIDEAZĂ CACHE-UL.
        """
        if not self.data:
            QMessageBox.warning(self, "Atenție", "Nu există date de salvat.")
            return

        try:
            for row in range(self.table.rowCount()):
                checkbox_widget = self.table.cellWidget(row, 1)
                if checkbox_widget:
                    checkbox = checkbox_widget.findChild(QCheckBox)
                    if checkbox and row < len(self.data["imprumuturi"]):
                        self.data["imprumuturi"][row]["procesat"] = checkbox.isChecked()

            json_path = self._get_json_path(self.current_mode)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)

            # INVALIDEAZĂ CACHE după salvare pentru a reflecta modificările
            print(f"Salvare reușită - invalidare cache pentru modul: {self.current_mode}")
            self._invalidate_cache(self.current_mode)

            QMessageBox.information(
                self,
                "Salvare reușită",
                "Statusul împrumuturilor a fost salvat cu succes!"
            )

            # Reîncarcă pentru actualizare (va reîncărca din JSON fresh)
            self.load_data(force_refresh=False)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Eroare salvare",
                f"Nu s-a putut salva statusul:\n{e}"
            )

    def delete_list(self):
        """
        Șterge lista de împrumuturi (doar JSON-ul pentru modul curent).
        """
        mod_text = "Împrumuturi Acordate" if self.current_mode == self.MOD_IMPRUMUTURI_ACORDATE else "Prima Rată"

        reply = QMessageBox.question(
            self,
            "Confirmare ștergere",
            f"Sigur dorești să ștergi lista pentru modul '{mod_text}'?\n\n"
            f"Această acțiune este ireversibilă!\n\n"
            f"Doar lista pentru modul curent va fi ștearsă\n"
            f"Cealaltă listă rămâne intactă\n"
            f"Lista va fi regenerată automat la următoarea detectare",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                json_path = self._get_json_path(self.current_mode)

                if os.path.exists(json_path):
                    os.remove(json_path)

                    # Invalidează cache pentru modul curent
                    self._invalidate_cache(self.current_mode)

                    QMessageBox.information(
                        self,
                        "Ștergere reușită",
                        f"Lista pentru modul '{mod_text}' a fost ștearsă cu succes!\n\n"
                        f"Cealaltă listă a rămas intactă."
                    )
                    self.data = None
                    self._update_table([])
                else:
                    QMessageBox.warning(
                        self,
                        "Atenție",
                        "Fișierul nu există deja."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Eroare ștergere",
                    f"Nu s-a putut șterge fișierul:\n{e}"
                )


# Pentru testare independentă
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Creare baze de date de test dacă nu există
    if not os.path.exists(DB_DEPCRED):
        print(f"Creare bază de date test: {DB_DEPCRED}")
        with sqlite3.connect(DB_DEPCRED) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS depcred (
                    nr_fisa INTEGER,
                    luna INTEGER,
                    anul INTEGER,
                    dobanda REAL,
                    impr_deb REAL,
                    impr_cred REAL,
                    impr_sold REAL,
                    dep_deb REAL,
                    dep_cred REAL,
                    dep_sold REAL,
                    prima INTEGER
                )
            """)

            # Date test: Iunie = împrumuturi acordate, Iulie = prima rată de stabilit
            test_data = [
                # Iunie 2025 - împrumuturi acordate
                (1262, 6, 2025, 0, 15000.0, 0, 15000.0, 100, 0, 5000, 0),
                (2054, 6, 2025, 0, 15000.0, 0, 15000.0, 100, 0, 3000, 0),
                (2413, 6, 2025, 0, 15000.0, 0, 15000.0, 100, 0, 4000, 0),
                # Iulie 2025 - prima rată de stabilit (IMPR_CRED = 0)
                (1262, 7, 2025, 0, 0, 0, 15000.0, 100, 0, 5100, 0),
                (2054, 7, 2025, 0, 0, 0, 15000.0, 100, 0, 3100, 0),
                (2413, 7, 2025, 0, 0, 0, 15000.0, 100, 0, 4100, 0),
            ]

            conn.executemany("""
                INSERT INTO depcred VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, test_data)
            conn.commit()
            print("Bază DEPCRED creată cu date test pentru ambele moduri")

    if not os.path.exists(DB_MEMBRII):
        print(f"Creare bază de date test: {DB_MEMBRII}")
        with sqlite3.connect(DB_MEMBRII) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS membrii (
                    NR_FISA INTEGER PRIMARY KEY,
                    NUM_PREN TEXT NOT NULL,
                    DOMICILIUL TEXT NOT NULL,
                    CALITATEA TEXT NOT NULL,
                    DATA_INSCR TEXT NOT NULL,
                    COTIZATIE_STANDARD NUMERIC NOT NULL DEFAULT 0
                )
            """)

            test_membri = [
                (1262, 'Popescu Ion', 'Petroșani, str. Minerilor nr. 10', 'Membru', '01-01-2020', 100),
                (2054, 'Ionescu Maria', 'Petroșani, str. Libertății nr. 25', 'Membru', '15-03-2021', 100),
                (2413, 'Gheorghe Vasile', 'Petroșani, str. Victoriei nr. 7', 'Membru', '10-06-2022', 100)
            ]

            conn.executemany("""
                INSERT INTO membrii VALUES (?, ?, ?, ?, ?, ?)
            """, test_membri)
            conn.commit()
            print("Bază MEMBRII creată cu 3 membri")

    widget = ImprumuturiNoiWidget()
    widget.show()

    sys.exit(app.exec_())