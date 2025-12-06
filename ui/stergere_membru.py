# Modificat pentru a șterge membri în loc de a-i lichida.
# Aplicat design glossy 3D bombat modern din celelalte module.
import os
import sqlite3
import sys
import logging
from datetime import datetime

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QCheckBox,
    QApplication, QMainWindow, QFrame, QGridLayout, QLineEdit, QScrollArea,
    QTextEdit, QSizePolicy, QCompleter, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QFont, QColor

# --- Configurare Căi Baze de Date ---
if getattr(sys, 'frozen', False):
    BASE_RESOURCE_PATH = os.path.dirname(sys.executable)
else:
    BASE_RESOURCE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

DB_MEMBRII = os.path.join(BASE_RESOURCE_PATH, "MEMBRII.db")
DB_DEPCRED = os.path.join(BASE_RESOURCE_PATH, "DEPCRED.db")
DB_ACTIVI = os.path.join(BASE_RESOURCE_PATH, "ACTIVI.db")
DB_INACTIVI = os.path.join(BASE_RESOURCE_PATH, "INACTIVI.db")
DB_CHITANTE = os.path.join(BASE_RESOURCE_PATH, "CHITANTE.db")
DB_LICHIDATI = os.path.join(BASE_RESOURCE_PATH, "LICHIDATI.db")

# --- Importuri Utilitare ---
try:
    from ui.validari import afiseaza_eroare, CustomDialogYesNo, afiseaza_info, afiseaza_warning
except ImportError as e:
    logging.error(f"Eroare la importul ui.validari: {e}. Se folosesc dialoguri standard.")


    def afiseaza_eroare(mesaj: str, parent=None):
        QMessageBox.critical(parent, "Eroare", mesaj)


    def afiseaza_info(mesaj: str, parent=None):
        QMessageBox.information(parent, "Informație", mesaj)


    def afiseaza_warning(mesaj: str, parent=None):
        QMessageBox.warning(parent, "Atenție", mesaj)


    class CustomDialogYesNo(QMessageBox):
        def __init__(self, title: str, message: str, icon_path: str = None, parent=None):
            super().__init__(parent)
            self.setWindowTitle(title)
            self.setText(message)
            self.setIcon(QMessageBox.Question)
            self.da_buton = self.addButton("Da", QMessageBox.YesRole)
            self.nu_buton = self.addButton("Nu", QMessageBox.NoRole)
            self.setDefaultButton(self.nu_buton)

# Configurare logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# --- Clasa SyncedTextEdit (pentru scroll sincronizat) ---
class SyncedTextEdit(QTextEdit):
    """ QTextEdit cu scroll sincronizat între mai multe instanțe. """

    def __init__(self, siblings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.siblings = siblings

    def wheelEvent(self, event):
        """ Propagă evenimentul de scroll la celelalte QTextEdit din listă. """
        scrollbar = self.verticalScrollBar()
        can_scroll = scrollbar.minimum() < scrollbar.maximum()

        if not can_scroll:
            super().wheelEvent(event)
            return

        old_val = scrollbar.value()
        super().wheelEvent(event)
        new_val = scrollbar.value()

        if new_val != old_val:
            for te in self.siblings:
                if te is not self:
                    bar = te.verticalScrollBar()
                    if bar.value() != new_val:
                        bar.setValue(new_val)


# --- Clasa Principală a Widgetului ---
class StergereMembruWidget(QWidget):
    """ Widget pentru căutarea și ștergerea unui membru CAR din bazele de date. """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._verificare_activa = False
        self._loaded_nr_fisa = None
        self._coloane_financiare_widgets = []
        self._coloane_financiare_layout_map = {}

        # Inițializare UI, stiluri și semnale
        self._init_ui()
        self._apply_styles()
        self._connect_signals()

        # Configurare specifică (coloane financiare)
        self._setup_coloane_financiare()

        # Setăm starea inițială a formularului (needitabil)
        self._set_form_editable(False)
        self.reset_form()

        # Setăm titlul ferestrei dacă widget-ul este fereastra principală
        if self.parent() is None or isinstance(self.parentWidget(), QMainWindow):
            try:
                self.window().setWindowTitle("Ștergere Membru CAR")
            except AttributeError:
                logging.warning("Nu s-a putut seta titlul ferestrei.")

    def _set_form_editable(self, editable: bool):
        """ Activează/dezactivează câmpurile needitabile ale formularului. """
        self.txt_adresa.setReadOnly(not editable)
        self.txt_calitate.setReadOnly(not editable)
        self.txt_data_insc.setReadOnly(not editable)
        for widget in self._coloane_financiare_widgets:
            widget.setReadOnly(not editable)

    # --- Metode de Inițializare UI ---
    def _init_ui(self):
        """ Construiește interfața grafică principală modernă. """
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)

        # Configurăm secțiunile UI: Header, Zona de Scroll, Acțiuni
        self._setup_header_frame()
        self._setup_scroll_area()
        self._setup_actions_area()

    def _setup_header_frame(self):
        """ Creează frame-ul superior cu câmpurile de căutare și informații membru - Design Modern. """
        self.header_frame = QFrame()
        self.header_frame.setObjectName("header_frame")
        header_layout = QGridLayout(self.header_frame)
        header_layout.setContentsMargins(15, 12, 15, 12)
        header_layout.setSpacing(12)

        # Etichete și câmpuri de text
        self.lbl_nume = QLabel("Nume Prenume:")
        self.txt_nume = QLineEdit()
        self.txt_nume.setPlaceholderText("Căutare după nume...")
        self.txt_nume.setToolTip("Introduceți primele litere ale numelui...")

        self.lbl_nr_fisa = QLabel("Număr Fișă:")
        self.txt_nr_fisa = QLineEdit()
        self.txt_nr_fisa.setPlaceholderText("Căutare după fișă...")
        self.txt_nr_fisa.setToolTip("Introduceți numărul fișei...")

        self.lbl_adresa = QLabel("Adresa:")
        self.txt_adresa = QLineEdit()
        self.txt_adresa.setReadOnly(True)

        self.lbl_calitate = QLabel("Calitatea:")
        self.txt_calitate = QLineEdit()
        self.txt_calitate.setReadOnly(True)

        self.lbl_data_insc = QLabel("Data înscrierii:")
        self.txt_data_insc = QLineEdit()
        self.txt_data_insc.setReadOnly(True)

        # Butonul de Resetare cu design modern
        self.reset_button = QPushButton("Golește formular")
        self.reset_button.setObjectName("reset_button")
        self.reset_button.setToolTip("Resetează formularul și golește câmpurile")
        self.reset_button.setCursor(Qt.PointingHandCursor)
        self.reset_button.setMinimumHeight(35)

        # Butonul de Ștergere Membru cu design modern PERICULOS
        self.buton_sterge = QPushButton("⚠️ Șterge Definitiv")
        self.buton_sterge.setObjectName("delete_button")
        self.buton_sterge.setToolTip("ATENȚIE: Șterge DEFINITIV membrul din toate bazele de date!")
        self.buton_sterge.setCursor(Qt.PointingHandCursor)
        self.buton_sterge.setEnabled(False)
        self.buton_sterge.setMinimumHeight(35)

        # Aplicăm efecte de umbră pentru butoane
        self._apply_shadow_effect(self.reset_button)
        self._apply_shadow_effect(self.buton_sterge)

        # Adăugare widget-uri în layout-ul grid
        header_layout.addWidget(self.lbl_nume, 0, 0)
        header_layout.addWidget(self.txt_nume, 0, 1)
        header_layout.addWidget(self.lbl_nr_fisa, 0, 2)
        header_layout.addWidget(self.txt_nr_fisa, 0, 3)

        header_layout.addWidget(self.lbl_adresa, 1, 0)
        header_layout.addWidget(self.txt_adresa, 1, 1)
        header_layout.addWidget(self.lbl_calitate, 1, 2)
        header_layout.addWidget(self.txt_calitate, 1, 3)

        header_layout.addWidget(self.lbl_data_insc, 2, 0)
        header_layout.addWidget(self.txt_data_insc, 2, 1)
        header_layout.addWidget(self.reset_button, 2, 2)
        header_layout.addWidget(self.buton_sterge, 2, 3)

        # Setăm extinderea coloanelor
        header_layout.setColumnStretch(1, 2)
        header_layout.setColumnStretch(3, 2)

        self.main_layout.addWidget(self.header_frame)

        # Configurare QCompleter pentru sugestii de nume
        self._update_completer_flag = True
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchStartsWith)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.txt_nume.setCompleter(self.completer)

    def _apply_shadow_effect(self, widget):
        """ Aplică efectul de umbră 3D la un widget. """
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 40))
        widget.setGraphicsEffect(shadow)

    def _apply_header_shadow_effect(self, header_widget):
        """ Aplică efectul de umbră 3D PREMIUM la headerele secțiunilor. """
        header_shadow = QGraphicsDropShadowEffect()
        header_shadow.setBlurRadius(10)  # Mai mare pentru mai mult relief
        header_shadow.setOffset(0, 3)  # Offset mai mare pentru efect ridicat
        header_shadow.setColor(QColor(0, 0, 0, 60))  # Mai intens pentru contrast
        header_widget.setGraphicsEffect(header_shadow)

    def _setup_scroll_area(self):
        """ Creează zona de scroll cu design modern îmbunătățit. """
        scroll_container = QWidget()
        scroll_hbox = QHBoxLayout(scroll_container)
        scroll_hbox.setContentsMargins(0, 0, 0, 0)
        scroll_hbox.setSpacing(8)

        self.columns_frame = QFrame()
        self.columns_frame.setObjectName("columns_frame")
        self.columns_frame.setStyleSheet(
            "QFrame#columns_frame { border: none; background-color: transparent; padding: 0px; }")
        columns_layout = QHBoxLayout(self.columns_frame)
        columns_layout.setContentsMargins(0, 0, 0, 0)
        columns_layout.setSpacing(8)

        # Creăm secțiunile vizuale cu design modern 3D
        self.loan_section = self._create_financial_section_frame(
            "Situație Împrumuturi", "#e74c3c", "#fff5f5", "#ffcdd2"
        )
        self.date_section = self._create_financial_section_frame(
            "Dată", "#6c757d", "#f8f9fa", "#dee2e6"
        )
        self.deposit_section = self._create_financial_section_frame(
            "Situație Depuneri", "#28a745", "#f8fff8", "#d4edda"
        )

        # Layout-uri interne pentru coloanele fiecărei secțiuni
        self.loan_columns_layout = QHBoxLayout()
        self.loan_columns_layout.setContentsMargins(0, 0, 0, 0)
        self.loan_columns_layout.setSpacing(2)
        self.date_columns_layout = QHBoxLayout()
        self.date_columns_layout.setContentsMargins(0, 0, 0, 0)
        self.date_columns_layout.setSpacing(2)
        self.deposit_columns_layout = QHBoxLayout()
        self.deposit_columns_layout.setContentsMargins(0, 0, 0, 0)
        self.deposit_columns_layout.setSpacing(2)

        # Adăugăm layout-urile de coloane în secțiunile corespunzătoare
        self.loan_section.layout().addLayout(self.loan_columns_layout)
        self.date_section.layout().addLayout(self.date_columns_layout)
        self.deposit_section.layout().addLayout(self.deposit_columns_layout)

        # Adăugăm secțiunile în layout-ul principal cu proporții optimizate
        columns_layout.addWidget(self.loan_section, stretch=4)
        columns_layout.addWidget(self.date_section, stretch=1)
        columns_layout.addWidget(self.deposit_section, stretch=3)

        scroll_hbox.addWidget(self.columns_frame)

        # Creăm widget-ul QScrollArea cu stiluri moderne
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(scroll_container)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setMinimumHeight(250)
        self.main_layout.addWidget(self.scroll_area, stretch=1)

    def _create_financial_section_frame(self, title, border_color, bg_color, header_bg_color):
        """ Creează un QFrame stilizat MODERN 3D cu efecte glossy pentru o secțiune financiară. """
        section = QFrame()
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(8, 8, 8, 8)
        section_layout.setSpacing(6)

        # Design MODERN 3D cu gradienți îmbunătățiți
        if "Împrumuturi" in title:
            section.setStyleSheet(f"""
                QFrame {{ 
                    border: 3px solid {border_color}; 
                    border-radius: 12px; 
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {bg_color}, stop:1 #ffebee); 
                }}
            """)
        elif "Depuneri" in title:
            section.setStyleSheet(f"""
                QFrame {{ 
                    border: 3px solid {border_color}; 
                    border-radius: 12px; 
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {bg_color}, stop:1 #e8f5e8); 
                }}
            """)
        else:  # Dată
            section.setStyleSheet(f"""
                QFrame {{ 
                    border: 3px solid {border_color}; 
                    border-radius: 12px; 
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {bg_color}, stop:1 #e9ecef); 
                }}
            """)

        # Eticheta de titlu cu design 3D modern EXACT ca în celelalte module
        lbl_header = QLabel(title)
        lbl_header.setAlignment(Qt.AlignCenter)
        lbl_header.setMinimumHeight(38)

        # 🎨 STILURI SPECIFICE HARDCODATE exact ca în adaugare_membru.py, sume_lunare.py, verificare_fise.py
        if "Împrumuturi" in title:
            lbl_header.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffcdd2, stop:1 #ef9a9a);
                    border: 2px solid #e74c3c;
                    border-radius: 8px;
                    padding: 8px 15px;
                    font-weight: bold;
                    font-size: 11pt;
                    color: #2c3e50;
                    margin-bottom: 6px;
                }
            """)
        elif "Depuneri" in title:
            lbl_header.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #d4edda, stop:1 #a3d977);
                    border: 2px solid #28a745;
                    border-radius: 8px;
                    padding: 8px 15px;
                    font-weight: bold;
                    font-size: 11pt;
                    color: #2c3e50;
                    margin-bottom: 6px;
                }
            """)
        else:  # Dată
            lbl_header.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #dee2e6, stop:1 #adb5bd);
                    border: 2px solid #6c757d;
                    border-radius: 8px;
                    padding: 8px 15px;
                    font-weight: bold;
                    font-size: 11pt;
                    color: #2c3e50;
                    margin-bottom: 6px;
                }
            """)

        section_layout.addWidget(lbl_header)

        # Aplicăm efectul de umbră PREMIUM la secțiune
        self._apply_shadow_effect(section)

        # 🌟 ADĂUGAT: Aplicăm efectul de umbră și la HEADER pentru efect 3D complet
        self._apply_header_shadow_effect(lbl_header)

        return section

    def _setup_actions_area(self):
        """ Creează frame-ul inferior pentru acțiuni. """
        self.actions_frame = QFrame()
        self.actions_layout = QHBoxLayout(self.actions_frame)
        self.actions_layout.setContentsMargins(0, 5, 0, 0)
        self.actions_layout.addStretch(1)
        self.actions_layout.addStretch(1)
        self.main_layout.addWidget(self.actions_frame)

    def _apply_styles(self):
        """ Aplică stiluri CSS moderne cu efecte 3D și gradienți. """
        # Stiluri generale moderne cu efecte îmbunătățite
        general_styles = """
            StergereMembruWidget, QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
            QScrollArea { 
                border: none; 
                background-color: transparent;
            }
            /* ScrollBar modern cu design 3D */
            QScrollBar:vertical {
                border: none;
                background: rgba(0,0,0,0.1);
                width: 12px;
                margin: 0;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: rgba(74, 144, 226, 0.7);
                min-height: 20px;
                border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(74, 144, 226, 0.9);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar:horizontal {
                border: none;
                background: rgba(0,0,0,0.1);
                height: 12px;
                margin: 0;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background: rgba(74, 144, 226, 0.7);
                min-width: 20px;
                border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background: rgba(74, 144, 226, 0.9);
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
                width: 0px;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 2px solid #b3d1ff;
                border-radius: 6px;
                padding: 6px 10px;
                min-height: 23px;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border-color: #4a90e2;
                box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
            }
            QLineEdit:read-only {
                background-color: #f8f9fa;
                color: #6c757d;
                border-color: #dee2e6;
            }
            QLabel { 
                color: #2c3e50; 
                padding-bottom: 2px; 
                font-weight: bold;
            }
        """

        # Stiluri pentru header cu design modern 3D
        header_styles = """
            QFrame#header_frame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8fbff, stop:1 #e7f3ff);
                border: 2px solid #4a90e2;
                border-radius: 10px;
                padding: 10px 15px;
            }
            QFrame#header_frame QLabel {
                font-weight: bold; 
                padding-bottom: 0px; 
                background: none;
                border: none;
                color: #2c3e50;
            }
        """

        # Stiluri moderne pentru butoane cu efecte 3D
        button_styles = """
            QPushButton#reset_button {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff6b6b, stop:1 #ee5a52);
                border: 2px solid #e74c3c;
                border-radius: 8px;
                font-size: 10pt; font-weight: bold;
                padding: 8px 16px; color: white; 
                min-width: 140px;
            }
            QPushButton#reset_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff7b7b, stop:1 #ff6b6b);
                border-color: #dc3545;
                transform: translateY(-1px);
            }
            QPushButton#reset_button:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ee5a52, stop:1 #e74c3c);
                transform: translateY(0px);
            }

            QPushButton#delete_button {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #dc3545, stop:1 #a71e2a);
                border: 2px solid #a71e2a;
                border-radius: 8px;
                color: white; 
                font-weight: bold;
                padding: 8px 16px;
                min-width: 160px;
                font-size: 10pt;
            }
            QPushButton#delete_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e74c3c, stop:1 #dc3545);
                border-color: #921925;
                transform: translateY(-1px);
            }
            QPushButton#delete_button:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #a71e2a, stop:1 #8b1921);
                transform: translateY(0px);
            }
            QPushButton#delete_button:disabled {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6c757d, stop:1 #5a6268);
                color: #cccccc;
                border-color: #6c757d;
            }
        """

        self.setStyleSheet(general_styles + header_styles + button_styles)
        font = QFont("Segoe UI", 10)
        self.setFont(font)

    def _connect_signals(self):
        """ Conectează semnalele widget-urilor la slot-urile corespunzătoare. """
        # Căutare după nume
        self.txt_nume.textChanged.connect(self._update_completer_model)
        self.completer.activated[str].connect(self._handle_name_selected)
        self.completer.highlighted.connect(lambda: setattr(self, '_update_completer_flag', False))
        self.txt_nume.editingFinished.connect(self._handle_name_finished)

        # Căutare după Nr. Fișă
        self.txt_nr_fisa.editingFinished.connect(self._handle_fisa_entered)

        # Butoane de acțiune
        self.reset_button.clicked.connect(self.reset_form)
        self.buton_sterge.clicked.connect(self._confirm_and_delete_member)

    # --- Metode pentru Coloane Financiare ---
    def _setup_coloane_financiare(self):
        """ Adaugă coloanele financiare în secțiunile corespunzătoare. """
        # Secțiunea Împrumuturi
        self._add_financial_column(self.loan_columns_layout, 'dobanda', 'Dobândă', read_only=True)
        self._add_financial_column(self.loan_columns_layout, 'impr_deb', 'Împrumut', read_only=True)
        self._add_financial_column(self.loan_columns_layout, 'impr_cred', 'Rată Achitată', read_only=True)
        self._add_financial_column(self.loan_columns_layout, 'impr_sold', 'Sold Împrumut', read_only=True)
        # Secțiunea Dată
        self._add_financial_column(self.date_columns_layout, 'luna_an', 'Luna-An', read_only=True)
        # Secțiunea Depuneri
        self._add_financial_column(self.deposit_columns_layout, 'dep_deb', 'Cotizație', read_only=True)
        self._add_financial_column(self.deposit_columns_layout, 'dep_cred', 'Retragere Fond', read_only=True)
        self._add_financial_column(self.deposit_columns_layout, 'dep_sold', 'Sold Depunere', read_only=True)

        # Setăm referințele 'siblings' pentru sincronizarea scroll-ului
        for te in self._coloane_financiare_widgets:
            te.siblings = self._coloane_financiare_widgets

    def _add_financial_column(self, section_layout, column_name, title, add_label=True, read_only=True):
        """ Creează și adaugă o coloană financiară cu design modern îmbunătățit. """
        text_edit = SyncedTextEdit(siblings=self._coloane_financiare_widgets)
        text_edit.setReadOnly(read_only)
        text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        font = QFont("Consolas", 10)
        if not font.exactMatch():
            font = QFont("Courier New", 10)
        text_edit.setFont(font)

        # Stil modern pentru QTextEdit cu efecte 3D
        text_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #adb5bd;
                border-top: none;
                border-radius: 0px;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px; 
                padding: 6px; 
                background-color: #ffffff; 
                color: #495057;
                selection-background-color: #b3d1ff;
            }
            QTextEdit:read-only {
                background-color: #f8f9fa; 
                color: #6c757d;
            }
            QTextEdit:focus {
                border-color: #4a90e2;
                background-color: #fafbfc;
            }
        """)

        label = None
        layout = QVBoxLayout()
        layout.setSpacing(0)

        if add_label:
            label = QLabel(title)
            label.setAlignment(Qt.AlignCenter)
            label.setFixedHeight(32)
            # Stil modern pentru label cu gradient
            label.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f1f3f4, stop:1 #e8eaed);
                    border: 2px solid #adb5bd;
                    border-bottom: none;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px; 
                    padding: 6px;
                    font-weight: bold; 
                    font-size: 9pt; 
                    color: #2c3e50;
                }
            """)
            layout.addWidget(label)

        layout.addWidget(text_edit, stretch=1)
        section_layout.addLayout(layout)

        column_data = {"layout": layout, "label": label, "text_edit": text_edit}
        self._coloane_financiare_layout_map[column_name] = column_data
        self._coloane_financiare_widgets.append(text_edit)
        return column_data

    # --- Metode de Gestionare Evenimente și Logică ---
    def showEvent(self, event):
        """ Apelată când widget-ul devine vizibil. Setează focusul inițial. """
        logging.debug(f"{self.__class__.__name__} afișat. Se setează focusul.")
        target = self.txt_nr_fisa if self.txt_nr_fisa.isEnabled() else self.txt_nume
        QtCore.QTimer.singleShot(0, lambda: target.setFocus())
        super().showEvent(event)

    def hideEvent(self, event):
        """ Apelată când widget-ul este ascuns. Resetează formularul. """
        logging.debug(f"{self.__class__.__name__} ascuns. Se resetează formularul.")
        self.reset_form()
        super().hideEvent(event)

    def _handle_name_selected(self, selected_name):
        """ Slot apelat când un nume este selectat din lista QCompleter. """
        logging.info(f"Nume selectat din completer: {selected_name}")
        self._load_member_data(name=selected_name)
        self._update_completer_flag = False

    def _handle_name_finished(self):
        """ Slot apelat la finalizarea editării numelui (Enter sau pierdere focus). """
        if not self._update_completer_flag:
            self._update_completer_flag = True
            return

        entered_name = self.txt_nume.text().strip()
        if not entered_name:
            return

        current_completion = self.completer.currentCompletion()
        if current_completion and current_completion.upper() == entered_name.upper():
            logging.info(f"Nume confirmat prin Enter/Focus Lost: {current_completion}")
            self._load_member_data(name=current_completion)
        else:
            logging.info(f"Nume introdus manual '{entered_name}'. Se încearcă încărcarea.")
            nr_fisa_check = self._get_nr_fisa_for_name(entered_name)
            if nr_fisa_check:
                self._load_member_data(name=entered_name)
            else:
                logging.warning(f"Numele '{entered_name}' nu a fost găsit. Nu se încarcă date.")

        self._update_completer_flag = True

    def _handle_fisa_entered(self):
        """ Slot apelat la finalizarea editării Nr. Fișă. """
        nr_fisa_str = self.txt_nr_fisa.text().strip()
        if nr_fisa_str.isdigit():
            logging.info(f"Nr. Fișă introdus: {nr_fisa_str}")
            self._load_member_data(nr_fisa=int(nr_fisa_str))
        elif nr_fisa_str:
            afiseaza_warning("Numărul fișei trebuie să fie numeric.", parent=self)
            self.txt_nr_fisa.selectAll()
            self.txt_nr_fisa.setFocus()

    def _load_member_data(self, nr_fisa=None, name=None):
        """ Metodă centrală pentru încărcarea datelor unui membru (personale și financiare). """
        if self._verificare_activa:
            return
        self._verificare_activa = True
        self.reset_form(clear_search_fields=False)
        self._loaded_nr_fisa = None
        self.buton_sterge.setEnabled(False)

        target_nr_fisa = nr_fisa
        target_name = name

        try:
            # Pas 1: Determinăm Nr. Fișă și Numele corecte
            if target_nr_fisa is None and target_name:
                logging.debug(f"Căutare fișă pentru nume: '{target_name}'")
                target_nr_fisa = self._get_nr_fisa_for_name(target_name)
                if not target_nr_fisa:
                    afiseaza_info(f"Membrul '{target_name}' nu a fost găsit în baza de date.", parent=self)
                    return
                self.txt_nr_fisa.setText(str(target_nr_fisa))
                logging.debug(f"Fișă găsită: {target_nr_fisa}")

            elif target_nr_fisa is not None:
                logging.debug(f"Căutare date pentru fișa: {target_nr_fisa}")
                member_data_temp = self._get_member_data_from_membrii(target_nr_fisa)
                if not member_data_temp:
                    # Fișa nu există în MEMBRII.db, verificăm dacă există în DEPCRED.db
                    logging.warning(f"Fișa {target_nr_fisa} nu există în MEMBRII.db. Se verifică în DEPCRED.db...")
                    if self._check_member_exists_in_depcred(target_nr_fisa):
                        # Fișa există în DEPCRED dar nu în MEMBRII - DISCREPANȚĂ DE INTEGRITATE
                        logging.warning(f"⚠️ DISCREPANȚĂ: Fișa {target_nr_fisa} există în DEPCRED dar NU în MEMBRII!")
                        afiseaza_warning(
                            f"⚠️ ATENȚIE: Discrepanță de integritate detectată!\n\n"
                            f"Fișa {target_nr_fisa} are istoric financiar în DEPCRED.db,\n"
                            f"dar NU există înregistrare corespunzătoare în MEMBRII.db.\n\n"
                            f"Acest membru va fi afișat cu date incomplete.\n"
                            f"Recomandare: Verificați integritatea bazelor de date.",
                            parent=self
                        )
                        # Continuăm încărcarea cu date limitate (fără nume, adresă, etc.)
                        target_name = f"[FIȘĂ {target_nr_fisa} - Date incomplete]"
                        self.txt_nume.setText(target_name)
                        logging.debug(f"Se continuă cu date incomplete pentru fișa {target_nr_fisa}")
                    else:
                        # Fișa nu există nici în MEMBRII, nici în DEPCRED
                        afiseaza_info(f"Fișa cu numărul {target_nr_fisa} nu există în nicio bază de date.", parent=self)
                        return
                else:
                    target_name = member_data_temp.get("NUM_PREN", "")
                    self.txt_nume.setText(target_name)
                    logging.debug(f"Nume găsit: '{target_name}'")
            else:
                logging.warning("_load_member_data apelat fără nr_fisa sau nume.")
                return

            # Pas 2: Avem un Nr. Fișă valid
            self._loaded_nr_fisa = target_nr_fisa
            logging.info(f"Încărcare date complete pentru fișa: {self._loaded_nr_fisa}, Nume: {target_name}")

            # Pas 3: Încărcăm datele personale din MEMBRII.db
            member_data = self._get_member_data_from_membrii(self._loaded_nr_fisa)
            if member_data:
                # Datele personale există în MEMBRII.db (caz normal)
                self.txt_adresa.setText(member_data.get("DOMICILIUL", ""))
                self.txt_calitate.setText(member_data.get("CALITATEA", ""))
                self.txt_data_insc.setText(member_data.get("DATA_INSCR", ""))
                # Setăm tooltip-uri pentru informații complete
                self.txt_adresa.setToolTip(member_data.get("DOMICILIUL", ""))
                self.txt_calitate.setToolTip(member_data.get("CALITATEA", ""))
                self.txt_data_insc.setToolTip(member_data.get("DATA_INSCR", ""))
                self.txt_nr_fisa.setToolTip(str(self._loaded_nr_fisa))
                self.txt_nume.setToolTip(target_name)
            else:
                # Membru există doar în DEPCRED (discrepanță de integritate)
                # Afișăm câmpuri goale pentru date personale, dar permitem ștergerea
                logging.warning(f"Fișa {self._loaded_nr_fisa} nu are date personale în MEMBRII.db - se afișează doar istoric financiar")
                self.txt_adresa.setText("[Date lipsă - doar istoric financiar]")
                self.txt_calitate.setText("[Date lipsă]")
                self.txt_data_insc.setText("[Date lipsă]")
                # Setăm tooltip-uri explicative
                self.txt_adresa.setToolTip("⚠️ Membru fără înregistrare în MEMBRII.db")
                self.txt_calitate.setToolTip("⚠️ Membru fără înregistrare în MEMBRII.db")
                self.txt_data_insc.setToolTip("⚠️ Membru fără înregistrare în MEMBRII.db")
                self.txt_nr_fisa.setToolTip(f"⚠️ Fișă {self._loaded_nr_fisa} - Doar în DEPCRED.db")
                self.txt_nume.setToolTip(target_name)
                # Continuăm încărcarea - nu returnam!

            # Pas 4: Încărcăm datele financiare din DEPCRED.db
            self._populate_financial_data(self._loaded_nr_fisa)

            # Pas 5: Finalizăm starea UI
            self._set_form_editable(False)
            self.txt_nume.setEnabled(False)
            self.txt_nr_fisa.setEnabled(False)
            self.buton_sterge.setEnabled(True)
            logging.info(f"Date încărcate cu succes pentru {target_name} ({self._loaded_nr_fisa}).")

        except Exception as e:
            logging.error(f"Eroare în _load_member_data: {e}", exc_info=True)
            afiseaza_eroare(f"A apărut o eroare la încărcarea datelor membrului:\n{str(e)}", parent=self)
            self.reset_form()
        finally:
            self._verificare_activa = False
            self._update_completer_flag = True

    def _populate_financial_data(self, nr_fisa):
        """ Încarcă și afișează istoricul financiar din DEPCRED.db în coloanele dedicate. """
        logging.info(f"Populare date financiare din DEPCRED pentru fișa {nr_fisa}...")
        for widget in self._coloane_financiare_widgets:
            widget.clear()

        depcred_data = self._get_member_details_depcred(nr_fisa)
        if not depcred_data:
            logging.warning(f"Nu există înregistrări în DEPCRED.db pentru fișa {nr_fisa}")
            return

        # Pregătim un dicționar pentru a colecta liniile fiecărei coloane
        lines = {cd["text_edit"]: [] for cd in self._coloane_financiare_layout_map.values()}
        idx_to_col_name = {
            0: 'dobanda', 1: 'impr_deb', 2: 'impr_cred', 3: 'impr_sold',
            6: 'dep_deb', 7: 'dep_cred', 8: 'dep_sold'
        }

        # Iterăm prin fiecare rând (lună/an) din datele financiare
        for row in depcred_data:
            # Populăm coloanele financiare
            for idx, col_name in idx_to_col_name.items():
                if col_name in self._coloane_financiare_layout_map:
                    widget = self._coloane_financiare_layout_map[col_name]["text_edit"]
                    value = row[idx] if row[idx] is not None else 0.0
                    lines[widget].append(f"{value:.2f}")

            # Populăm coloana de dată (Luna-An)
            if 'luna_an' in self._coloane_financiare_layout_map:
                luna, anul = row[4], row[5]
                luna_an_val = f"{luna:02d}-{anul}" if luna and anul else "??-????"
                widget = self._coloane_financiare_layout_map['luna_an']["text_edit"]
                lines[widget].append(luna_an_val)

        # Setăm textul final pentru fiecare QTextEdit
        for widget, line_list in lines.items():
            widget.setText("\n".join(line_list))

        # Resetăm scrollbar-ul la început pentru toate coloanele
        for te in self._coloane_financiare_widgets:
            te.verticalScrollBar().setValue(te.verticalScrollBar().minimum())

    def _update_completer_model(self):
        """ Actualizează modelul QCompleter pe baza textului introdus în txt_nume. """
        if not self._update_completer_flag:
            logging.debug("_update_completer_model: Flag este False, se omite.")
            return

        prefix = self.txt_nume.text().strip()
        logging.debug(f"_update_completer_model: Prefix='{prefix}'")
        if len(prefix) < 2:
            self.completer.setModel(None)
            return

        names_dict = self._get_names_starting_with(prefix)
        names_list = list(names_dict.keys())
        logging.debug(f"_update_completer_model: Nume găsite={len(names_list)}")

        model = QStringListModel(names_list)
        self.completer.setModel(model)

        if names_list and self.txt_nume.hasFocus() and not self.completer.popup().isVisible():
            logging.debug("_update_completer_model: Se forțează afișarea popup.")
            self.completer.complete()
        elif not names_list:
            self.completer.popup().hide()

    def reset_form(self, clear_search_fields=True):
        """ Resetează formularul la starea inițială. """
        sender_button = self.sender()
        is_reset_button = sender_button == self.reset_button
        logging.debug(
            f"Resetare formular... Apelat de {'Reset Button' if is_reset_button else 'altceva'}. clear_search_fields={clear_search_fields}")

        if is_reset_button:
            clear_search_fields = True
            logging.debug("Forțat clear_search_fields=True deoarece a fost apăsat butonul Reset.")

        self._loaded_nr_fisa = None

        # Golește câmpurile de informații membru și tooltip-urile
        self.txt_adresa.clear();
        self.txt_adresa.setToolTip("")
        self.txt_calitate.clear();
        self.txt_calitate.setToolTip("")
        self.txt_data_insc.clear();
        self.txt_data_insc.setToolTip("")

        # Golește opțional câmpurile de căutare
        if clear_search_fields:
            logging.debug("Curățare câmpuri căutare (Nume/Fișă).")
            self.txt_nume.clear();
            self.txt_nume.setToolTip("Introduceți primele litere...")
            self.txt_nr_fisa.clear();
            self.txt_nr_fisa.setToolTip("Introduceți numărul fișei...")
            self.completer.setModel(None)
        else:
            logging.debug("NU se curăță câmpurile de căutare (Nume/Fișă).")

        # Golește coloanele financiare
        for widget in self._coloane_financiare_widgets:
            widget.clear()

        # Resetează starea butoanelor și câmpurilor de căutare
        self._set_form_editable(False)
        self.txt_nume.setEnabled(True)
        self.txt_nr_fisa.setEnabled(True)
        self.buton_sterge.setEnabled(False)

        # Resetează flag-urile interne
        self._update_completer_flag = True
        self._verificare_activa = False

        # Setăm focusul înapoi pe câmpul Nr. Fișă
        target_focus = self.txt_nr_fisa if self.txt_nr_fisa.isEnabled() else self.txt_nume
        logging.debug(f"Setare focus pe: {target_focus.objectName()}")
        QtCore.QTimer.singleShot(0, lambda: target_focus.setFocus())
        logging.debug("Resetare formular finalizată.")

    # --- Metode pentru Ștergere Membru ---
    def _confirm_and_delete_member(self):
        """ Afișează dialogul de confirmare și inițiază ștergerea dacă se confirmă. """
        if self._loaded_nr_fisa is None:
            afiseaza_warning("Nu este selectat niciun membru pentru ștergere.", parent=self)
            return

        nr_fisa = self._loaded_nr_fisa
        nume = self.txt_nume.text()

        # Dialog de avertizare cu design îmbunătățit
        dialog = CustomDialogYesNo(
            title="⚠️ CONFIRMARE ȘTERGERE DEFINITIVĂ",
            message=(
                f"!!! ATENȚIE MAXIMĂ !!!\n\n"
                f"Sunteți pe cale să ștergeți DEFINITIV și IREVERSIBIL\n"
                f"toate datele asociate membrului:\n\n"
                f"   📁 Fișa: {nr_fisa}\n"
                f"   👤 Nume: {nume}\n\n"
                f"🗑️ Această acțiune va elimina înregistrările din:\n"
                f"   • MEMBRII.db (date personale)\n"
                f"   • DEPCRED.db (istoric financiar complet)\n"
                f"   • ACTIVI.db (dacă există)\n"
                f"   • LICHIDATI.db (dacă există)\n\n"
                f"⚠️ ATENȚIE: Acțiunea NU poate fi ANULATĂ!\n\n"
                f"Sigur doriți să continuați cu ștergerea?"
            ),
            parent=self
        )
        result = dialog.exec_()

        if dialog.clickedButton() == dialog.da_buton:
            logging.info(f"Confirmare primită pentru ștergerea fișei {nr_fisa} ({nume}).")
            success, message = self._delete_member_from_databases(nr_fisa)
            if success:
                afiseaza_info(
                    f"✅ Membrul {nume} (fișa {nr_fisa}) a fost șters cu succes din toate bazele de date.\n\n{message}",
                    parent=self)
                self.reset_form()
            else:
                afiseaza_eroare(f"❌ Ștergerea membrului {nume} (fișa {nr_fisa}) a eșuat.\n\nDetalii: {message}",
                                parent=self)
        else:
            logging.info(f"Ștergerea fișei {nr_fisa} ({nume}) a fost anulată de utilizator.")

    def _delete_member_from_databases(self, nr_fisa):
        """ Șterge înregistrările pentru nr_fisa specificat din bazele de date relevante.
            CORECTATĂ pentru structura reală a bazelor de date. """
        if nr_fisa is None:
            return False, "Număr fișă invalid."

        # CORECTATĂ: Structura reală bazată pe analiza efectuată
        databases_to_process = {
            DB_MEMBRII: ("MEMBRII", "NR_FISA"),  # Tabel: MEMBRII (majuscule)
            DB_DEPCRED: ("DEPCRED", "NR_FISA"),  # Tabel: DEPCRED (majuscule)
            DB_ACTIVI: ("ACTIVI", "NR_FISA"),  # Tabel: ACTIVI (majuscule)
            DB_INACTIVI: ("inactivi", "nr_fisa"),  # Presupunem structura similară
            DB_LICHIDATI: ("lichidati", "nr_fisa"),  # Tabel: lichidati (minuscule)
        }

        errors = []
        success_messages = []
        overall_success = True

        for db_path, (table_name, key_column) in databases_to_process.items():
            conn = None
            rows_affected = 0
            try:
                if not os.path.exists(db_path):
                    msg = f"Baza de date {os.path.basename(db_path)} nu a fost găsită. Se omite."
                    logging.warning(msg)
                    success_messages.append(f"- {msg}")
                    continue

                logging.info(
                    f"Procesare {os.path.basename(db_path)}: Ștergere fișa {nr_fisa} din tabelul {table_name}...")
                conn = sqlite3.connect(db_path, timeout=30.0)
                cursor = conn.cursor()

                # Verificăm dacă tabelul există (EXACT cum este în baza de date)
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
                if cursor.fetchone() is None:
                    msg = f"Tabelul '{table_name}' nu există în {os.path.basename(db_path)}. Se omite."
                    logging.warning(msg)
                    success_messages.append(f"- {msg}")
                    if conn:
                        conn.close()
                    continue

                # Verificăm dacă coloana există în tabel
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [row[1] for row in cursor.fetchall()]
                if key_column not in columns:
                    msg = f"Coloana '{key_column}' nu există în tabelul '{table_name}' din {os.path.basename(db_path)}. Se omite."
                    logging.warning(msg)
                    success_messages.append(f"- {msg}")
                    if conn:
                        conn.close()
                    continue

                # Dezactivăm foreign key constraints temporar pentru siguranță
                cursor.execute("PRAGMA foreign_keys = OFF")

                # Executăm comanda DELETE cu structura CORECTĂ
                sql = f"DELETE FROM {table_name} WHERE {key_column} = ?"
                logging.debug(f"Executare SQL: {sql} cu parametrul {nr_fisa}")
                cursor.execute(sql, (nr_fisa,))
                rows_affected = cursor.rowcount

                # Reactivăm foreign key constraints
                cursor.execute("PRAGMA foreign_keys = ON")

                logging.debug(f"Rânduri afectate în {table_name}: {rows_affected}. Se încearcă commit...")
                conn.commit()
                logging.info(f"Commit reușit pentru {os.path.basename(db_path)}.")

                # Adăugăm mesajul de succes
                if rows_affected > 0:
                    msg = f"✅ Șters {rows_affected} rând(uri) din {table_name} ({os.path.basename(db_path)})."
                    success_messages.append(f"- {msg}")
                else:
                    msg = f"ℹ️ Nicio înregistrare găsită pentru fișa {nr_fisa} în {table_name} ({os.path.basename(db_path)})."
                    success_messages.append(f"- {msg}")

            except sqlite3.Error as e:
                error_msg = f"❌ EROARE SQLite la ștergerea din {os.path.basename(db_path)} (tabel {table_name}): {e}"
                logging.error(error_msg, exc_info=True)
                errors.append(f"- {error_msg}")
                overall_success = False
                if conn:
                    try:
                        logging.warning("Se încearcă rollback...")
                        conn.rollback()
                        logging.warning("Rollback efectuat.")
                    except Exception as rb_err:
                        logging.error(f"Eroare la rollback pentru {os.path.basename(db_path)}: {rb_err}")
            except Exception as e:
                error_msg = f"❌ EROARE neașteptată la procesarea {os.path.basename(db_path)}: {e}"
                logging.error(error_msg, exc_info=True)
                errors.append(f"- {error_msg}")
                overall_success = False
                if conn:
                    try:
                        logging.warning("Se încearcă rollback...")
                        conn.rollback()
                        logging.warning("Rollback efectuat.")
                    except Exception as rb_err:
                        logging.error(f"Eroare la rollback pentru {os.path.basename(db_path)}: {rb_err}")
            finally:
                if conn:
                    conn.close()
                    logging.debug(f"Deconectat de la {db_path}")

        # Construim mesajul final
        final_message = "📋 Rezumat operațiuni:\n" + "\n".join(success_messages)
        if errors:
            final_message += "\n\n⚠️ ATENȚIE! ERORI ÎNTÂMPINATE:\n" + "\n".join(errors)

        return overall_success, final_message

    # BONUS: Metodă de verificare pentru a confirma ștergerea
    def _verify_member_deleted(self, nr_fisa):
        """Verifică că membrul a fost șters din bazele de date principale."""
        verification_results = []

        # Verificăm bazele de date principale
        main_databases = {
            DB_MEMBRII: ("MEMBRII", "NR_FISA"),  # Tabel: MEMBRII (majuscule)
            DB_DEPCRED: ("DEPCRED", "NR_FISA"),  # Tabel: DEPCRED (majuscule)
            DB_ACTIVI: ("ACTIVI", "NR_FISA"),  # Tabel: ACTIVI (majuscule)
            DB_INACTIVI: ("inactivi", "nr_fisa"),  # Presupunem structura similară
            DB_LICHIDATI: ("lichidati", "nr_fisa"),  # Tabel: lichidati (minuscule)
        }

        for db_path, (table_name, key_column) in main_databases.items():
            if not os.path.exists(db_path):
                continue

            try:
                conn = sqlite3.connect(db_path, timeout=30.0)
                cursor = conn.cursor()

                # Verifică dacă tabelul există
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
                if cursor.fetchone() is None:
                    continue

                # Caută înregistrări rămase
                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {key_column} = ?", (nr_fisa,))
                count = cursor.fetchone()[0]

                if count > 0:
                    verification_results.append(
                        f"⚠️ Găsite {count} înregistrări în {table_name} ({os.path.basename(db_path)})")
                else:
                    verification_results.append(f"✅ Curățat din {table_name} ({os.path.basename(db_path)})")

                conn.close()

            except Exception as e:
                verification_results.append(f"❌ Eroare verificare {os.path.basename(db_path)}: {e}")

        return verification_results

    # Versiune extinsă a metodei de ștergere cu verificare
    def _delete_member_with_verification(self, nr_fisa):
        """Șterge membrul și verifică ștergerea completă."""
        # Executăm ștergerea
        success, message = self._delete_member_from_databases(nr_fisa)

        if success:
            # Verificăm rezultatele
            verification = self._verify_member_deleted(nr_fisa)
            message += "\n\n🔍 VERIFICARE ȘTERGERE:\n" + "\n".join(verification)

        return success, message

    # --- Metode Statice pentru Acces la Baza de Date ---
    @staticmethod
    def _get_names_starting_with(prefix):
        """ Returnează un dicționar {nume: nr_fisa} pentru membrii al căror nume începe cu prefixul dat. """
        results = {}
        conn = None
        try:
            conn = sqlite3.connect(DB_MEMBRII, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT NR_FISA, NUM_PREN FROM membrii WHERE NUM_PREN LIKE ? COLLATE NOCASE ORDER BY NUM_PREN LIMIT 50",
                (prefix + '%',)
            )
            results = {row[1]: row[0] for row in cursor.fetchall()}
        except sqlite3.Error as e:
            logging.error(f"Eroare SQLite la _get_names_starting_with: {e}")
        finally:
            if conn:
                conn.close()
        return results

    @staticmethod
    def _get_nr_fisa_for_name(name):
        """ Returnează NR_FISA pentru un nume exact dat (case-insensitive). """
        if not name:
            return None
        conn = None
        nr_fisa_result = None
        try:
            conn = sqlite3.connect(DB_MEMBRII, timeout=30.0)
            cur = conn.cursor()
            cur.execute("SELECT NR_FISA FROM membrii WHERE NUM_PREN = ? COLLATE NOCASE", (name,))
            row = cur.fetchone()
            if row:
                nr_fisa_result = row[0]
        except sqlite3.Error as e:
            logging.error(f"Eroare SQLite la _get_nr_fisa_for_name: {e}")
            afiseaza_eroare(f"Eroare la căutarea fișei pentru nume '{name}':\n{e}")
        finally:
            if conn:
                conn.close()
        return nr_fisa_result

    @staticmethod
    def _get_member_data_from_membrii(nr_fisa):
        """ Returnează datele personale (dicționar) pentru un NR_FISA dat din MEMBRII.db. """
        if not nr_fisa:
            return None
        conn = None
        member_data_result = None
        try:
            conn = sqlite3.connect(DB_MEMBRII, timeout=30.0)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(
                "SELECT NR_FISA, NUM_PREN, CALITATEA, DOMICILIUL, DATA_INSCR FROM membrii WHERE NR_FISA = ?",
                (nr_fisa,)
            )
            row = cur.fetchone()
            if row:
                member_data_result = dict(row)
        except sqlite3.Error as e:
            logging.error(f"Eroare SQLite la _get_member_data_from_membrii pentru fișa {nr_fisa}: {e}")
            afiseaza_eroare(f"Eroare la citirea datelor personale pentru fișa {nr_fisa}:\n{e}")
        finally:
            if conn:
                conn.close()
        return member_data_result

    @staticmethod
    def _get_member_details_depcred(nr_fisa):
        """ Returnează istoricul financiar (listă de tuple) pentru un NR_FISA dat din DEPCRED.db. """
        if not nr_fisa:
            return []
        data = []
        conn = None
        try:
            conn = sqlite3.connect(DB_DEPCRED, timeout=30.0)
            cur = conn.cursor()
            cur.execute("""
                SELECT DOBANDA, IMPR_DEB, IMPR_CRED, IMPR_SOLD, LUNA, ANUL, DEP_DEB, DEP_CRED, DEP_SOLD, PRIMA
                FROM depcred
                WHERE NR_FISA = ?
                ORDER BY ANUL DESC, LUNA DESC
            """, (nr_fisa,))
            data = cur.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Eroare SQLite la _get_member_details_depcred pentru fișa {nr_fisa}: {e}")
            afiseaza_eroare(f"Eroare la citirea istoricului financiar pentru fișa {nr_fisa}:\n{e}")
        finally:
            if conn:
                conn.close()
        return data

    @staticmethod
    def _check_member_exists_in_depcred(nr_fisa):
        """
        Verifică dacă există înregistrări pentru NR_FISA în DEPCRED.db.
        Returnează True dacă există cel puțin o înregistrare, False altfel.
        """
        if not nr_fisa:
            return False
        conn = None
        exists = False
        try:
            conn = sqlite3.connect(DB_DEPCRED, timeout=30.0)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM DEPCRED WHERE NR_FISA = ?", (nr_fisa,))
            count = cur.fetchone()[0]
            exists = count > 0
        except sqlite3.Error as e:
            logging.error(f"Eroare SQLite la _check_member_exists_in_depcred pentru fișa {nr_fisa}: {e}")
        finally:
            if conn:
                conn.close()
        return exists


# =========================================
# Bloc pentru Testare Directă (Opțional)
# =========================================
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Creăm o fereastră principală simplă pentru a găzdui widget-ul
    main_window = QMainWindow()
    main_window.setWindowTitle("Test Ștergere Membru CAR - Design Modern 3D")
    main_window.setGeometry(100, 100, 1000, 700)

    # Creăm instanța widget-ului nostru
    stergere_widget = StergereMembruWidget()

    # Setăm widget-ul ca widget central al ferestrei principale
    main_window.setCentralWidget(stergere_widget)

    # Afișăm fereastra
    main_window.show()

    # Pornim bucla de evenimente a aplicației Qt
    sys.exit(app.exec_())