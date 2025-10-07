import sys
import os
import sqlite3
import logging
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

# Importuri PyQt5 corecte
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QSizePolicy, QScrollArea, QFrame, QTextEdit, QGridLayout,
    QApplication, QMainWindow
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Importăm funcțiile din validari.py
try:
    from ui.validari import (
        verifica_campuri_completate, verifica_format_data,
        verifica_format_luna_an, valideaza_numar_real, verifica_numere,
        anunta_membru_existent, anunta_membru_inexistent,
        afiseaza_eroare, afiseaza_info, afiseaza_warning
    )
except ImportError as e:
    print(f"EROARE: Nu s-a putut importa modulul 'validari'. Detalii: {e}")


    # Definim funcții placeholder
    def afiseaza_eroare(mesaj, parent=None):
        QMessageBox.critical(parent, "Eroare", mesaj)


    def afiseaza_info(mesaj, parent=None):
        QMessageBox.information(parent, "Info", mesaj)


    def afiseaza_warning(mesaj, parent=None):
        QMessageBox.warning(parent, "Atenție", mesaj)


    def anunta_membru_existent(parent, nr_fisa):
        return QMessageBox.question(parent, "Membru Existent", f"Membrul {nr_fisa} există. Modificați?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes


    def anunta_membru_inexistent(parent, nr_fisa):
        return QMessageBox.question(parent, "Membru Inexistent", f"Membrul {nr_fisa} nu există. Adăugați?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes


    def verifica_campuri_completate(widget, campuri, nume):
        return True  # Dummy


    def verifica_format_data(widget, camp, silent=False):
        return True  # Dummy


    def verifica_numere(widget, campuri, nume):
        return True  # Dummy


    def verifica_format_luna_an(widget, camp, silent=False):
        return True  # Dummy

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configurarea căilor pentru DB
try:
    if getattr(sys, 'frozen', False):
        BASE_RESOURCE_PATH = os.path.dirname(sys.executable)
    else:
        current_script_path = os.path.abspath(__file__)
        ui_directory = os.path.dirname(current_script_path)
        BASE_RESOURCE_PATH = os.path.dirname(ui_directory)

    DB_MEMBRII = os.path.join(BASE_RESOURCE_PATH, "MEMBRII.db")
    DB_DEPCRED = os.path.join(BASE_RESOURCE_PATH, "DEPCRED.db")

except Exception as e:
    print(f"Eroare critică la configurarea căilor DB: {e}")
    DB_MEMBRII = "MEMBRII.db"
    DB_DEPCRED = "DEPCRED.db"


class SyncedTextEdit(QTextEdit):
    """ QTextEdit cu scroll sincronizat și navigare TAB. """

    def __init__(self, siblings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.siblings = siblings

    def wheelEvent(self, event):
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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab:
            # Găsim indexul acestui widget în lista de frați
            if self in self.siblings:
                current_index = self.siblings.index(self)
                # Calculăm indexul următorului widget (cu wrapping)
                next_index = (current_index + 1) % len(self.siblings)
                # Setăm focus pe următorul widget
                self.siblings[next_index].setFocus()
        else:
            # Pentru alte taste, folosim comportamentul standard
            super().keyPressEvent(event)


class AdaugareMembruWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.verificare_activa = False
        self._loaded_nr_fisa = None  # Stocăm fișa încărcată/verificată

        # Definim atributele pentru a evita probleme de inițializare
        self.nr_fisa_input = None
        self.nume_input = None
        self.adresa_input = None
        self.calitate_input = None
        self.data_input = None
        self.reset_button = None
        self.col_dobanda = None
        self.col_impr_deb = None
        self.col_impr_cred = None
        self.col_impr_sold = None
        self.col_luna_an = None
        self.col_dep_deb = None
        self.col_dep_cred = None
        self.col_dep_sold = None
        self.coloane_financiare = []
        self.actions_frame = None
        self.actions_layout = None
        self.header_frame = None

        # Inițializăm interfața și conectăm semnalele
        self.init_ui()
        self.apply_styles()
        self.connect_signals()
        self.reset_form()

    def _get_financial_columns_map(self):
        """Returnează un dicționar cu mapări între numele coloanelor și widget-urile lor."""
        return {
            'dobanda': self.col_dobanda,
            'impr_deb': self.col_impr_deb,
            'impr_cred': self.col_impr_cred,
            'impr_sold': self.col_impr_sold,
            'luna_an': self.col_luna_an,
            'dep_deb': self.col_dep_deb,
            'dep_cred': self.col_dep_cred,
            'dep_sold': self.col_dep_sold
        }

    def _clear_actions(self):
        """Șterge butoanele de acțiune din layout."""
        while self.actions_layout.count() > 2:
            item = self.actions_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

    def init_ui(self):
        """Inițializează elementele de interfață utilizator cu design îmbunătățit."""
        self.setMinimumSize(650, 180)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Header îmbunătățit cu gradient și stil modern
        self.header_frame = QFrame()
        self.header_frame.setObjectName("header_frame")
        header_layout = QGridLayout(self.header_frame)
        header_layout.setContentsMargins(15, 12, 15, 12)
        header_layout.setSpacing(12)

        self.nr_fisa_input = QLineEdit()
        self.nume_input = QLineEdit()
        self.adresa_input = QLineEdit()
        self.calitate_input = QLineEdit()
        self.data_input = QLineEdit()

        # Buton reset stilizat modern
        self.reset_button = QPushButton("Golește formularul")
        self.reset_button.setFixedHeight(38)
        self.reset_button.setObjectName("reset_button")
        self.reset_button.setToolTip("Resetează formularul")
        self.reset_button.setCursor(Qt.PointingHandCursor)

        header_layout.addWidget(QLabel("Nume Prenume:"), 0, 0)
        header_layout.addWidget(self.nume_input, 0, 1)
        header_layout.addWidget(QLabel("Adresă:"), 0, 2)
        header_layout.addWidget(self.adresa_input, 0, 3)
        header_layout.addWidget(QLabel("Calitate:"), 1, 0)
        header_layout.addWidget(self.calitate_input, 1, 1)
        header_layout.addWidget(QLabel("Data înscrierii:"), 1, 2)
        header_layout.addWidget(self.data_input, 1, 3)
        header_layout.addWidget(QLabel("Număr fișă:"), 2, 0)
        header_layout.addWidget(self.nr_fisa_input, 2, 1)
        # Spacer pentru a împinge butonul la dreapta
        header_layout.addItem(
            QtWidgets.QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum), 2, 2
        )
        header_layout.addWidget(self.reset_button, 2, 3)

        header_layout.setColumnStretch(1, 2)
        header_layout.setColumnStretch(3, 2)

        main_layout.addWidget(self.header_frame)

        # Tooltips pentru câmpuri
        self.nume_input.textChanged.connect(lambda text: self.nume_input.setToolTip(text))
        self.adresa_input.textChanged.connect(lambda text: self.adresa_input.setToolTip(text))
        self.calitate_input.textChanged.connect(lambda text: self.calitate_input.setToolTip(text))

        # Container scrollabil îmbunătățit
        scroll_container = QWidget()
        scroll_hbox = QHBoxLayout(scroll_container)
        scroll_hbox.setContentsMargins(0, 0, 0, 0)
        scroll_hbox.setSpacing(8)

        columns_frame = QFrame()
        columns_frame.setStyleSheet("QFrame { border: none; background-color: transparent; padding: 0px; }")
        columns_layout = QHBoxLayout(columns_frame)
        columns_layout.setContentsMargins(0, 0, 0, 0)
        columns_layout.setSpacing(8)

        # Secțiunea Împrumuturi cu design îmbunătățit
        loan_section = QFrame()
        loan_section_layout = QVBoxLayout(loan_section)
        loan_section_layout.setContentsMargins(8, 8, 8, 8)
        loan_section_layout.setSpacing(6)
        loan_section.setStyleSheet(
            """
            QFrame {
                border: 3px solid #e74c3c;
                border-radius: 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fff5f5, stop:1 #ffebee);
            }
            """
        )

        lbl_imprumuturi = QLabel("Situație Împrumuturi")
        lbl_imprumuturi.setAlignment(Qt.AlignCenter)
        lbl_imprumuturi.setStyleSheet(
            """
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
            """
        )
        loan_section_layout.addWidget(lbl_imprumuturi)

        loan_columns_container = QWidget()
        loan_columns_layout = QHBoxLayout(loan_columns_container)
        loan_columns_layout.setContentsMargins(0, 0, 0, 0)
        loan_columns_layout.setSpacing(2)

        self.col_dobanda = self.create_financial_column("Dobândă")
        self.col_impr_deb = self.create_financial_column("Împrumut")
        self.col_impr_cred = self.create_financial_column("Rată Achitată")
        self.col_impr_sold = self.create_financial_column("Sold Împrumut")

        loan_columns_layout.addLayout(self.col_dobanda["layout"])
        loan_columns_layout.addLayout(self.col_impr_deb["layout"])
        loan_columns_layout.addLayout(self.col_impr_cred["layout"])
        loan_columns_layout.addLayout(self.col_impr_sold["layout"])
        loan_section_layout.addWidget(loan_columns_container)

        # Secțiunea Data cu design îmbunătățit
        date_section = QFrame()
        date_section_layout = QVBoxLayout(date_section)
        date_section_layout.setContentsMargins(8, 8, 8, 8)
        date_section_layout.setSpacing(6)
        date_section.setStyleSheet(
            """
            QFrame {
                border: 3px solid #6c757d;
                border-radius: 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
            """
        )

        lbl_data = QLabel("Dată")
        lbl_data.setAlignment(Qt.AlignCenter)
        lbl_data.setFixedHeight(lbl_imprumuturi.sizeHint().height())
        lbl_data.setStyleSheet(
            """
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
            """
        )
        date_section_layout.addWidget(lbl_data)

        luna_an_container = QWidget()
        luna_an_layout = QVBoxLayout(luna_an_container)
        luna_an_layout.setContentsMargins(0, 0, 0, 0)
        luna_an_layout.setSpacing(0)
        self.col_luna_an = self.create_financial_column("Luna-An", add_label=True)
        luna_an_layout.addLayout(self.col_luna_an["layout"], stretch=1)
        date_section_layout.addWidget(luna_an_container)

        # Secțiunea Depuneri cu design îmbunătățit
        deposit_section = QFrame()
        deposit_section_layout = QVBoxLayout(deposit_section)
        deposit_section_layout.setContentsMargins(8, 8, 8, 8)
        deposit_section_layout.setSpacing(6)
        deposit_section.setStyleSheet(
            """
            QFrame {
                border: 3px solid #28a745;
                border-radius: 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8fff8, stop:1 #e8f5e8);
            }
            """
        )

        lbl_depuneri = QLabel("Situație Depuneri")
        lbl_depuneri.setAlignment(Qt.AlignCenter)
        lbl_depuneri.setStyleSheet(
            """
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
            """
        )
        deposit_section_layout.addWidget(lbl_depuneri)

        deposit_columns_container = QWidget()
        deposit_columns_layout = QHBoxLayout(deposit_columns_container)
        deposit_columns_layout.setContentsMargins(0, 0, 0, 0)
        deposit_columns_layout.setSpacing(2)

        self.col_dep_deb = self.create_financial_column("Cotizație")
        self.col_dep_cred = self.create_financial_column("Retragere Fond")
        self.col_dep_sold = self.create_financial_column("Sold Depunere")

        deposit_columns_layout.addLayout(self.col_dep_deb["layout"])
        deposit_columns_layout.addLayout(self.col_dep_cred["layout"])
        deposit_columns_layout.addLayout(self.col_dep_sold["layout"])
        deposit_section_layout.addWidget(deposit_columns_container)

        columns_layout.addWidget(loan_section, stretch=4)
        columns_layout.addWidget(date_section, stretch=1)
        columns_layout.addWidget(deposit_section, stretch=3)

        scroll_hbox.addWidget(columns_frame)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_container)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        main_layout.addWidget(scroll_area, stretch=1)

        self.coloane_financiare = [
            self.col_dobanda["text_edit"], self.col_impr_deb["text_edit"],
            self.col_impr_cred["text_edit"], self.col_impr_sold["text_edit"],
            self.col_luna_an["text_edit"], self.col_dep_deb["text_edit"],
            self.col_dep_cred["text_edit"], self.col_dep_sold["text_edit"]
        ]

        for te in self.coloane_financiare:
            te.siblings = self.coloane_financiare

        self.actions_frame = QFrame()
        self.actions_layout = QHBoxLayout(self.actions_frame)
        self.actions_layout.addStretch(1)
        self.actions_layout.addStretch(1)
        main_layout.addWidget(self.actions_frame)

    def create_financial_column(self, title, add_label=True):
        """Creează o coloană financiară cu titlu opțional și design modern."""
        text_edit = SyncedTextEdit(siblings=[])
        text_edit.setReadOnly(False)  # Facem toate câmpurile editabile inițial
        text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        font = QFont("Consolas", 10)
        if not font.exactMatch(): font = QFont("Courier New", 10)
        text_edit.setFont(font)

        text_edit.setStyleSheet("""
            QTextEdit { 
                border: 2px solid #adb5bd; border-top: none; 
                border-radius: 0px; border-bottom-left-radius: 8px; 
                border-bottom-right-radius: 8px; padding: 6px; 
                background-color: #ffffff; color: #495057; 
                selection-background-color: #b3d1ff;
            }
            QTextEdit:read-only { 
                background-color: #f8f9fa; color: #6c757d; 
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
            label.setStyleSheet("""
                QLabel { 
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f1f3f4, stop:1 #e8eaed);
                    border: 2px solid #adb5bd;
                    border-bottom: none; border-top-left-radius: 8px; 
                    border-top-right-radius: 8px; padding: 6px; 
                    font-weight: bold; font-size: 9pt; color: #2c3e50; 
                    margin-bottom: 0px; 
                }
            """)
            layout.addWidget(label)

        layout.addWidget(text_edit, stretch=1)
        return {"layout": layout, "label": label, "text_edit": text_edit}

    def apply_styles(self):
        """Aplică stilurile pentru interfață cu design modern îmbunătățit."""
        general_styles = """ 
            AdaugareMembruWidget, QWidget { 
                font-family: 'Segoe UI', Arial, sans-serif; 
                font-size: 10pt; 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            } 
            QScrollArea { 
                border: none; 
                background-color: transparent;
            } 
            /* ScrollBar modern */
            QScrollBar:vertical { 
                border: none; background: rgba(0,0,0,0.1); width: 12px; 
                margin: 0; border-radius: 6px; 
            } 
            QScrollBar::handle:vertical { 
                background: rgba(74, 144, 226, 0.7); min-height: 20px; 
                border-radius: 6px; margin: 2px;
            } 
            QScrollBar::handle:vertical:hover { 
                background: rgba(74, 144, 226, 0.9); 
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { 
                border: none; background: none; height: 0px; 
            } 
            QScrollBar:horizontal { 
                border: none; background: rgba(0,0,0,0.1); height: 12px; 
                margin: 0; border-radius: 6px; 
            } 
            QScrollBar::handle:horizontal { 
                background: rgba(74, 144, 226, 0.7); min-width: 20px; 
                border-radius: 6px; margin: 2px;
            } 
            QScrollBar::handle:horizontal:hover { 
                background: rgba(74, 144, 226, 0.9); 
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { 
                border: none; background: none; width: 0px; 
            } 
        """

        header_styles = """ 
            QFrame#header_frame { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8fbff, stop:1 #e7f3ff); 
                border: 2px solid #4a90e2;
                border-radius: 10px; 
                padding: 10px;
            } 
            QFrame#header_frame QLabel { 
                color: #2c3e50; font-weight: bold; padding: 4px; 
                background: transparent; border: none; 
            } 
            QFrame#header_frame QLineEdit { 
                background-color: #ffffff; 
                border: 2px solid #b3d1ff;
                border-radius: 6px; 
                padding: 6px 10px;
                font-size: 10pt;
            } 
            QFrame#header_frame QLineEdit:focus {
                border-color: #4a90e2;
                box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
            }
            QFrame#header_frame QLineEdit:disabled { 
                background-color: #f8f9fa; color: #6c757d;
                border-color: #dee2e6;
            } 
        """

        reset_button_styles = """ 
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
        """

        self.setStyleSheet(general_styles + header_styles + reset_button_styles)
        font = QFont("Segoe UI", 10)
        self.setFont(font)
        self.header_frame.setStyleSheet(header_styles)

    def connect_signals(self):
        """ Conectează semnalele. """
        self.nr_fisa_input.editingFinished.connect(self.verifica_numar_fisa)
        self.reset_button.clicked.connect(lambda: self.reset_form(editabil=False, keep_nr_fisa=False))

    def reset_form(self, editabil=False, keep_nr_fisa=False):
        """
        Resetează formularul la starea inițială.
        :param editabil: Dacă True, câmpurile devin editabile pentru adăugare/modificare
        :param keep_nr_fisa: Dacă True, păstrează nr_fisa curent (pentru modificare)
        """
        print(f"Resetare formular AdaugareMembruWidget (editabil={editabil}, keep_nr_fisa={keep_nr_fisa})...")
        self._loaded_nr_fisa = None
        nr_fisa_curent = self.nr_fisa_input.text() if keep_nr_fisa else ""

        fields_header = [self.nume_input, self.calitate_input, self.adresa_input, self.data_input]
        for field in fields_header:
            field.clear()
            field.setEnabled(editabil)

        if not keep_nr_fisa:
            self.nr_fisa_input.clear()
        else:
            self.nr_fisa_input.setText(nr_fisa_curent)

        self.nr_fisa_input.setEnabled(not editabil and not keep_nr_fisa)

        # Resetează câmpurile financiare - acum se golesc complet
        cols_financiare = self._get_financial_columns_map()
        for col_name, col_dict in cols_financiare.items():
            if col_dict and col_dict.get("text_edit"):
                col_dict["text_edit"].clear()
                col_dict["text_edit"].setReadOnly(not editabil)

                # Dacă este în modul editabil (adaugare membru nou), inițializăm cu 0.00
                if editabil and not keep_nr_fisa:
                    if col_name == 'luna_an':
                        # Auto-completare luna-an curentă
                        now = datetime.now()
                        col_dict["text_edit"].setPlainText(now.strftime('%m-%Y'))
                    elif col_name == 'dep_deb':
                        # Pentru cotizație punem marcaj special
                        col_dict["text_edit"].setHtml('<font color="red"><b>0.00!</b></font>')
                    else:
                        # Celelalte câmpuri cu 0.00
                        col_dict["text_edit"].setPlainText("0.00")

        # Ștergem butonul de salvare dacă există
        self._clear_actions()

        target_widget = self.nume_input if editabil else self.nr_fisa_input
        QtCore.QTimer.singleShot(0, lambda: target_widget.setFocus())

    def showEvent(self, event):
        """Apelat automat de Qt când widget-ul devine vizibil."""
        print("AdaugareMembruWidget afișat. Se setează focusul.")
        target_widget = self.nr_fisa_input if self.nr_fisa_input.isEnabled() else self.nume_input
        QtCore.QTimer.singleShot(0, lambda: target_widget.setFocus())
        super(AdaugareMembruWidget, self).showEvent(event)

    def hideEvent(self, event):
        """Apelat automat de Qt când widget-ul devine invizibil."""
        print("AdaugareMembruWidget ascuns. Se resetează formularul (ne-editabil).")
        self.reset_form(editabil=False, keep_nr_fisa=False)  # Resetare completă
        super(AdaugareMembruWidget, self).hideEvent(event)

    def _add_save_button(self, text):
        """Adaugă butonul de salvare cu design modern."""
        self._clear_actions()
        self.save_button = QPushButton(text)
        self.save_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #28a745, stop:1 #20c997);
                border: 2px solid #28a745;
                border-radius: 8px;
                color: white; 
                font-weight: bold; 
                padding: 8px 16px;
                min-width: 160px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34ce57, stop:1 #28a745);
                border-color: #20c997;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #20c997, stop:1 #28a745);
                transform: translateY(0px);
            }
        """)
        self.save_button.clicked.connect(self._save_data)
        self.actions_layout.insertWidget(1, self.save_button)

    def _set_fields_editable(self, editable):
        """Setează câmpurile de bază ca editabile sau nu."""
        for field in [self.nume_input, self.calitate_input, self.adresa_input, self.data_input]:
            field.setEnabled(editable)
            field.setReadOnly(not editable)
            field.setStyleSheet(field.styleSheet())

    def verifica_numar_fisa(self):
        """Verifică numărul de fișă introdus și încarcă membru dacă există."""
        if self.verificare_activa:
            return

        self.verificare_activa = True
        self._loaded_nr_fisa = None
        nr_fisa_str = self.nr_fisa_input.text().strip()

        if not nr_fisa_str.isdigit():
            afiseaza_warning("Numărul fișei trebuie să conțină doar cifre.", parent=self)
            self.nr_fisa_input.setFocus()
            self.nr_fisa_input.selectAll()
            self.verificare_activa = False
            return

        nr_fisa = int(nr_fisa_str)
        conn_membrii = None
        conn_depcred = None

        try:
            conn_membrii = sqlite3.connect(DB_MEMBRII)
            cursor_membrii = conn_membrii.cursor()
            member_data = self._get_member_data_from_db(nr_fisa)

            if member_data:
                # Membrul există - resetăm formularul și încărcăm datele
                self.reset_form(editabil=False, keep_nr_fisa=True)

                # Completăm câmpurile de bază
                self.nume_input.setText(member_data.get("NUM_PREN", ""))
                self.calitate_input.setText(member_data.get("CALITATEA", ""))
                self.adresa_input.setText(member_data.get("DOMICILIUL", ""))
                self.data_input.setText(member_data.get("DATA_INSCR", ""))
                self.nr_fisa_input.setEnabled(False)
                self._loaded_nr_fisa = nr_fisa

                # Încărcăm TOATE datele financiare cu formatare vizuală avansată
                self._load_complete_member_history(nr_fisa)

                # Facem toate câmpurile financiare read-only pentru membrii existenți
                for col_dict in self._get_financial_columns_map().values():
                    if col_dict and col_dict.get("text_edit"):
                        col_dict["text_edit"].setReadOnly(True)

                if anunta_membru_existent(self, nr_fisa):
                    # Dacă userul vrea să modifice, facem câmpurile de bază editabile
                    # dar păstrăm partea financiară read-only
                    self._set_fields_editable(True)
                    self.nume_input.setFocus()
                    self._add_save_button("Salvează Modificări")
                else:
                    self.reset_form(editabil=False, keep_nr_fisa=False)
            else:
                # Membrul nu există - întrebăm dacă vrea să îl adauge
                if anunta_membru_inexistent(self, nr_fisa):
                    self.reset_form(editabil=True, keep_nr_fisa=True)
                    self.nr_fisa_input.setEnabled(False)

                    # Inițializăm datele financiare pentru membru nou
                    now = datetime.now()
                    luna_an_widget = self._get_financial_columns_map().get('luna_an', {}).get('text_edit')
                    if luna_an_widget:
                        luna_an_widget.setPlainText(now.strftime('%m-%Y'))

                    # Inițializăm toate câmpurile cu 0.00, mai puțin cotizația
                    cols_financiare = self._get_financial_columns_map()
                    for col_name, col_dict in cols_financiare.items():
                        if col_name == 'luna_an':
                            continue  # Am setat deja luna-an
                        if col_dict and col_dict.get("text_edit"):
                            if col_name == 'dep_deb':
                                # Pentru cotizație punem text roșu pentru a atrage atenția
                                col_dict["text_edit"].setHtml('<font color="red"><b>0.00!</b></font>')
                            else:
                                col_dict["text_edit"].setPlainText("0.00")

                    self._add_save_button("Salvează Membru Nou")
                else:
                    self.reset_form(editabil=False, keep_nr_fisa=False)
        except sqlite3.Error as e:
            afiseaza_eroare(f"Eroare la verificarea fișei {nr_fisa}:\n{str(e)}", parent=self)
            logging.error(f"Eroare DB la verificarea fișei {nr_fisa}: {e}", exc_info=True)
        finally:
            if conn_membrii: conn_membrii.close()
            if conn_depcred: conn_depcred.close()
            self.verificare_activa = False

    def _format_istoric_line_advanced(self, row_data, sold_impr_prec, sold_dep_prec, bg_color):
        """
        Formatează un rând de istoric cu aceleași reguli ca în sume_lunare.py

        Structura row_data din depcred:
        (dobanda, impr_deb, impr_cred, impr_sold, luna, anul, dep_deb, dep_cred, dep_sold, prima)
        """
        try:
            # Conversie la Decimal pentru calcule precise
            dobanda = Decimal(str(row_data[0] or '0.00')).quantize(Decimal('0.01'), ROUND_HALF_UP)
            impr_deb = Decimal(str(row_data[1] or '0.00')).quantize(Decimal('0.01'), ROUND_HALF_UP)
            impr_cred = Decimal(str(row_data[2] or '0.00')).quantize(Decimal('0.01'), ROUND_HALF_UP)
            impr_sold = Decimal(str(row_data[3] or '0.00')).quantize(Decimal('0.01'), ROUND_HALF_UP)
            luna = int(row_data[4] or 0)
            anul = int(row_data[5] or 0)
            dep_deb = Decimal(str(row_data[6] or '0.00')).quantize(Decimal('0.01'), ROUND_HALF_UP)
            dep_cred = Decimal(str(row_data[7] or '0.00')).quantize(Decimal('0.01'), ROUND_HALF_UP)
            dep_sold = Decimal(str(row_data[8] or '0.00')).quantize(Decimal('0.01'), ROUND_HALF_UP)

            # Conversie solduri precedente la Decimal
            sold_impr_prec = Decimal(str(sold_impr_prec or '0.00'))
            sold_dep_prec = Decimal(str(sold_dep_prec or '0.00'))

            # Funcție helper pentru formatare cu fundal
            def format_with_bg(value_html, bg_color):
                return f'<div style="background-color:{bg_color}; padding:4px; margin:1px 0;">{value_html}</div>'

            # === FORMATARE DOBÂNDĂ ===
            dobanda_val = format_with_bg(f"{dobanda:.2f}", bg_color)

            # === FORMATARE ÎMPRUMUT NOU (ALBASTRU ÎNGROȘAT) ===
            if impr_deb > Decimal('0.00'):
                impr_deb_val = format_with_bg(f'<font color="blue"><b>{impr_deb:.2f}</b></font>', bg_color)
            else:
                impr_deb_val = format_with_bg(f"{impr_deb:.2f}", bg_color)

            # === FORMATARE RATĂ ACHITATĂ ===
            if impr_cred == Decimal('0.00') and impr_sold > Decimal('0.005'):
                # Verifică dacă s-a acordat împrumut nou în luna curentă
                if impr_deb > Decimal('0.00'):
                    # Luna curentă are împrumut nou - nu se așteaptă plata ratei
                    impr_cred_val = format_with_bg(f"{impr_cred:.2f}", bg_color)
                else:
                    # Nu s-a acordat împrumut nou - verificăm luna anterioară
                    prev_luna = luna - 1 if luna > 1 else 12
                    prev_anul = anul if luna > 1 else anul - 1

                    # Verificăm în DB dacă a existat împrumut în luna anterioară
                    had_loan_prev_month = self._check_loan_in_previous_month(prev_luna, prev_anul)

                    if had_loan_prev_month:
                        # Prima lună după contractare
                        impr_cred_val = format_with_bg('<font color="orange"><b>!NOU!</b></font>', bg_color)
                    else:
                        # Luni ulterioare - neachitat
                        impr_cred_val = format_with_bg('<font color="red"><b>Neachitat!</b></font>', bg_color)
            else:
                impr_cred_val = format_with_bg(f"{impr_cred:.2f}", bg_color)

            # === FORMATARE SOLD ÎMPRUMUT ===
            # REGULA GENERALĂ: Oricând se aplică dobândă = achitare împrumut anterior
            if dobanda > Decimal('0.00'):
                impr_sold_val = format_with_bg('<font color="green"><b>Achitat</b></font>', bg_color)
            elif impr_sold <= Decimal('0.005'):
                # Pentru cazurile fără dobândă, dar cu sold zero
                if impr_deb > Decimal('0.00') and impr_cred > Decimal('0.00'):
                    # Cazul special: achitare și nou împrumut în aceeași lună
                    expected_old_sold = sold_impr_prec - impr_cred
                    if expected_old_sold <= Decimal('0.005'):
                        impr_sold_val = format_with_bg('<font color="green"><b>Achitat</b></font>', bg_color)
                    else:
                        impr_sold_val = format_with_bg('0.00', bg_color)
                elif impr_cred > Decimal('0.00') and sold_impr_prec > Decimal('0.005'):
                    # Achitare normală
                    impr_sold_val = format_with_bg('<font color="green"><b>Achitat</b></font>', bg_color)
                else:
                    impr_sold_val = format_with_bg('0.00', bg_color)
            else:
                impr_sold_val = format_with_bg(f"{impr_sold:.2f}", bg_color)

            # === FORMATARE LUNA-AN ===
            if luna and anul:
                luna_an_val = format_with_bg(f"{luna:02d}-{anul}", bg_color)
            else:
                luna_an_val = format_with_bg("??-????", bg_color)

            # === FORMATARE COTIZAȚIE NEACHITATĂ ===
            if dep_deb == Decimal('0.00') and sold_dep_prec > Decimal('0.005'):
                dep_deb_val = format_with_bg('<font color="red"><b>Neachitat!</b></font>', bg_color)
            else:
                dep_deb_val = format_with_bg(f"{dep_deb:.2f}", bg_color)

            # === FORMATARE RETRAGERE FOND ===
            dep_cred_val = format_with_bg(f"{dep_cred:.2f}", bg_color)

            # === FORMATARE SOLD DEPUNERI ===
            dep_sold_val = format_with_bg(f"{dep_sold:.2f}", bg_color)

            return {
                'dobanda': dobanda_val,
                'impr_deb': impr_deb_val,
                'impr_cred': impr_cred_val,
                'impr_sold': impr_sold_val,
                'luna_an': luna_an_val,
                'dep_deb': dep_deb_val,
                'dep_cred': dep_cred_val,
                'dep_sold': dep_sold_val
            }

        except (InvalidOperation, TypeError, ValueError) as e:
            print(f"Eroare formatare linie istoric: {e}")
            # Returnăm valori de eroare cu fundal
            error_val = format_with_bg('<font color="red">ERR</font>', bg_color)
            return {
                'dobanda': error_val, 'impr_deb': error_val, 'impr_cred': error_val,
                'impr_sold': error_val, 'luna_an': error_val, 'dep_deb': error_val,
                'dep_cred': error_val, 'dep_sold': error_val
            }

    def _check_loan_in_previous_month(self, prev_luna, prev_anul):
        """Verifică dacă a existat acordare de împrumut în luna anterioară."""
        if not self._loaded_nr_fisa or prev_anul <= 0:
            return False

        conn = None
        try:
            conn = sqlite3.connect(DB_DEPCRED)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT impr_deb FROM depcred WHERE nr_fisa = ? AND luna = ? AND anul = ?",
                (self._loaded_nr_fisa, prev_luna, prev_anul)
            )
            row = cursor.fetchone()
            if row and row[0]:
                prev_impr_deb = Decimal(str(row[0]))
                return prev_impr_deb > Decimal('0.00')
            return False
        except sqlite3.Error as e:
            print(f"Eroare verificare împrumut luna anterioară: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def _load_complete_member_history(self, nr_fisa):
        """Încarcă întregul istoric al membrului cu formatare vizuală avansată."""
        conn = None
        try:
            conn = sqlite3.connect(DB_DEPCRED)
            cursor = conn.cursor()

            # Selectăm toate înregistrările pentru membrul respectiv, ordonate cronologic descendent
            cursor.execute("""
                SELECT dobanda, impr_deb, impr_cred, impr_sold, luna, anul, 
                       dep_deb, dep_cred, dep_sold, prima
                FROM depcred 
                WHERE nr_fisa = ? 
                ORDER BY anul DESC, luna DESC
            """, (nr_fisa,))

            rows = cursor.fetchall()

            # Dacă există înregistrări, le procesăm cu formatare vizuală avansată
            if rows:
                # Pregătim structurile pentru fiecare coloană
                lines = {widget: [] for widget in [
                    self.col_dobanda["text_edit"], self.col_impr_deb["text_edit"],
                    self.col_impr_cred["text_edit"], self.col_impr_sold["text_edit"],
                    self.col_luna_an["text_edit"], self.col_dep_deb["text_edit"],
                    self.col_dep_cred["text_edit"], self.col_dep_sold["text_edit"]
                ]}

                # Procesăm datele în ordine pentru a calcula soldurile precedente corect
                sold_impr_prec = Decimal('0.00')
                sold_dep_prec = Decimal('0.00')

                for i, row in enumerate(rows):
                    # Fundaluri alternate îmbunătățite
                    bg_color = "#f8fbff" if i % 2 == 0 else "#f0f7ff"

                    # Pentru calculul soldurilor precedente, avem nevoie să parcurgem în ordine inversă
                    # Pentru moment, folosim soldurile din DB direct
                    if i < len(rows) - 1:
                        next_row = rows[i + 1]
                        sold_impr_prec = Decimal(str(next_row[3] or '0.00'))
                        sold_dep_prec = Decimal(str(next_row[8] or '0.00'))
                    else:
                        # Primul rând (cel mai vechi) - soldurile precedente sunt 0
                        sold_impr_prec = Decimal('0.00')
                        sold_dep_prec = Decimal('0.00')

                    # Aplicăm formatarea avansată
                    formatted_row = self._format_istoric_line_advanced(row, sold_impr_prec, sold_dep_prec, bg_color)

                    # Adăugăm în coloane
                    lines[self.col_dobanda["text_edit"]].append(formatted_row['dobanda'])
                    lines[self.col_impr_deb["text_edit"]].append(formatted_row['impr_deb'])
                    lines[self.col_impr_cred["text_edit"]].append(formatted_row['impr_cred'])
                    lines[self.col_impr_sold["text_edit"]].append(formatted_row['impr_sold'])
                    lines[self.col_luna_an["text_edit"]].append(formatted_row['luna_an'])
                    lines[self.col_dep_deb["text_edit"]].append(formatted_row['dep_deb'])
                    lines[self.col_dep_cred["text_edit"]].append(formatted_row['dep_cred'])
                    lines[self.col_dep_sold["text_edit"]].append(formatted_row['dep_sold'])

                # Setăm conținutul HTML pentru fiecare coloană
                for widget, line_list in lines.items():
                    widget.setHtml("".join(line_list))
                    widget.verticalScrollBar().setValue(widget.verticalScrollBar().minimum())

        except sqlite3.Error as e:
            logging.error(f"Eroare la încărcarea istoricului pentru fișa {nr_fisa}: {e}", exc_info=True)
            afiseaza_eroare(f"Eroare la încărcarea istoricului membrului:\n{e}", parent=self)
        finally:
            if conn:
                conn.close()

    def _populate_financial_inputs(self, db_row, editable=False):
        """Populează câmpurile financiare cu datele din baza de date."""
        try:
            col_map = self._get_financial_columns_map()
            idx_map = {
                0: 'dobanda', 1: 'impr_deb', 2: 'impr_cred', 3: 'impr_sold',
                4: 'luna', 5: 'anul', 6: 'dep_deb', 7: 'dep_cred', 8: 'dep_sold', 9: 'prima'
            }

            for idx, col_name in idx_map.items():
                if col_name in col_map and col_map[col_name] and col_map[col_name].get("text_edit"):
                    widget = col_map[col_name]["text_edit"]
                    value = db_row[idx] if idx < len(db_row) else None

                    if col_name == 'luna':
                        continue
                    if col_name == 'anul':
                        luna_val = db_row[idx - 1]
                        anul_val = value
                        widget_luna_an = col_map['luna_an']["text_edit"]
                        widget_luna_an.setPlainText(f"{luna_val:02d}-{anul_val}" if luna_val and anul_val else "")
                    else:
                        # Pentru toate câmpurile financiare numerice, folosim format număr standard
                        # și marcam vizual valorile neobișnuite
                        val_str = f"{value or 0.0:.2f}"

                        # Verificăm dacă trebuie să marcam vizual valoarea
                        if col_name == 'impr_deb' and value > 0:
                            # Împrumut nou - marcaj albastru
                            widget.setHtml(f'<font color="blue"><b>{val_str}</b></font>')
                        elif col_name == 'impr_sold' and value <= 0.005:
                            # Împrumut achitat - marcaj verde
                            widget.setHtml('<font color="green"><b>Achitat</b></font>')
                        elif col_name == 'dep_deb' and value == 0 and db_row[8] > 0.005:
                            # Cotizație neachitată - marcaj roșu
                            widget.setHtml('<font color="red"><b>Neachitat!</b></font>')
                        elif col_name == 'impr_cred' and value == 0 and db_row[3] > 0.005:
                            # Rată neachitată - marcaj portocaliu
                            widget.setHtml('<font color="orange"><b>!NOU!</b></font>')
                        else:
                            # Valoare normală - fără marcaj special
                            widget.setPlainText(val_str)

                        # Setăm read-only în funcție de parametrul
                        widget.setReadOnly(not editable)
        except Exception as e:
            logging.error(f"Eroare populare date financiare: {e}", exc_info=True)
            afiseaza_eroare(f"Eroare afișare date financiare:\n{e}", parent=self)

    def _save_data(self):
        """Validează datele și le salvează în baza de date."""
        logging.info("Încercare de salvare date...")

        # Verificăm dacă suntem în modul de adăugare sau modificare
        is_update = self._loaded_nr_fisa is not None

        try:
            # Validare câmpuri de bază (se aplică pentru ambele cazuri)
            nr_fisa_str = self.nr_fisa_input.text().strip()
            if not nr_fisa_str.isdigit():
                afiseaza_eroare("Numărul fișei este invalid sau lipsește.", parent=self)
                return

            nr_fisa = int(nr_fisa_str)
            nume = self.nume_input.text().strip()
            adresa = self.adresa_input.text().strip()
            calitate = self.calitate_input.text().strip()
            data_inscr = self.data_input.text().strip()

            campuri_obligatorii_widgets = [self.nume_input, self.adresa_input, self.calitate_input, self.data_input]
            nume_campuri_map = {
                self.nume_input: "Nume Prenume",
                self.adresa_input: "Adresă",
                self.calitate_input: "Calitate",
                self.data_input: "Data înscrierii"
            }

            if not verifica_campuri_completate(self, campuri_obligatorii_widgets, nume_campuri_map):
                return

            if not verifica_format_data(self, self.data_input):
                self.data_input.setFocus()
                return

            # === SEPARAREA LOGICII PENTRU MEMBRU EXISTENT VS MEMBRU NOU ===

            if is_update:
                # === MODIFICARE MEMBRU EXISTENT ===
                # Pentru membri existenți: DOAR salvare date personale, fără validare financiară
                logging.info(f"Modificare date personale pentru membrul existent {nr_fisa}")

                conn_m = None
                try:
                    conn_m = sqlite3.connect(DB_MEMBRII)
                    cursor_m = conn_m.cursor()

                    # Actualizare DOAR date personale (fără cotizația standard)
                    membrii_data = (nume, adresa, calitate, data_inscr, nr_fisa)
                    cursor_m.execute(
                        "UPDATE membrii SET NUM_PREN=?, DOMICILIUL=?, CALITATEA=?, DATA_INSCR=? WHERE NR_FISA=?",
                        membrii_data
                    )

                    if cursor_m.rowcount == 0:
                        afiseaza_eroare(
                            f"Nu s-a putut actualiza membrul cu fișa {nr_fisa}. Verificați dacă există în baza de date.",
                            parent=self)
                        return

                    conn_m.commit()
                    logging.info(f"Actualizare date personale în MEMBRII.db reușită pentru fișa {nr_fisa}")

                    afiseaza_info("Datele personale au fost modificate cu succes!", parent=self)
                    self.reset_form(editabil=False, keep_nr_fisa=False)

                except sqlite3.Error as e:
                    logging.error(f"Eroare SQLite la modificare membru {nr_fisa}: {e}", exc_info=True)
                    afiseaza_eroare(f"Eroare la modificarea datelor personale:\n{e}", parent=self)
                except Exception as e:
                    logging.error(f"Eroare generală la modificare membru {nr_fisa}: {e}", exc_info=True)
                    afiseaza_eroare(f"Eroare neașteptată la modificarea datelor:\n{e}", parent=self)
                finally:
                    if conn_m:
                        conn_m.close()

            else:
                # === ADĂUGARE MEMBRU NOU ===
                # Pentru membri noi: validare completă + salvare în ambele DB-uri
                logging.info(f"Adăugare membru nou cu fișa {nr_fisa}")

                # Validare date financiare (DOAR pentru membri noi)
                financial_data = {}
                financial_widgets = self._get_financial_columns_map()
                financial_numeric_widgets = []
                financial_labels_map = {}

                for name, col_dict in financial_widgets.items():
                    if name != 'luna_an' and col_dict and col_dict.get("text_edit"):
                        financial_numeric_widgets.append(col_dict["text_edit"])
                        label_widget = col_dict.get("label")
                        financial_labels_map[col_dict["text_edit"]] = label_widget.text() if label_widget else name

                if not verifica_numere(self, financial_numeric_widgets, financial_labels_map):
                    return

                # Extragere valori financiare
                for name, col_dict in financial_widgets.items():
                    if name == 'luna_an':
                        continue
                    widget = col_dict.get("text_edit")
                    if widget:
                        text_val = widget.toPlainText().strip().replace(',', '.')
                        financial_data[name] = float(text_val) if text_val else 0.0

                # Extragere luna și anul
                luna_an_widget = financial_widgets.get('luna_an', {}).get("text_edit")
                if not luna_an_widget:
                    afiseaza_eroare("Eroare internă: Nu s-a găsit widget-ul pentru Luna-An.", parent=self)
                    return

                luna_an_str = luna_an_widget.toPlainText().strip()
                if not verifica_format_luna_an(self, luna_an_widget):
                    luna_an_widget.setFocus()
                    return

                luna, anul = map(int, luna_an_str.split('-'))

                # Extragem valoarea cotizației pentru a o salva în MEMBRII.db
                cotizatie_standard = financial_data.get('dep_deb', 0.0)

                # Salvare în ambele baze de date pentru membru nou
                conn_m = None
                conn_d = None

                try:
                    # Salvare în MEMBRII.db
                    conn_m = sqlite3.connect(DB_MEMBRII)
                    cursor_m = conn_m.cursor()

                    # Verificare finală că numărul de fișă nu există
                    cursor_m.execute("SELECT NR_FISA FROM membrii WHERE NR_FISA=?", (nr_fisa,))
                    if cursor_m.fetchone():
                        afiseaza_eroare(f"Numărul de fișă {nr_fisa} există deja în baza de date!", parent=self)
                        return

                    # Inserare membru nou - INCLUDEM COTIZATIE_STANDARD
                    membrii_data = (nume, adresa, calitate, data_inscr, nr_fisa, cotizatie_standard)
                    cursor_m.execute(
                        "INSERT INTO membrii (NUM_PREN, DOMICILIUL, CALITATEA, DATA_INSCR, NR_FISA, COTIZATIE_STANDARD) VALUES (?, ?, ?, ?, ?, ?)",
                        membrii_data
                    )
                    conn_m.commit()
                    logging.info(
                        f"Salvare în MEMBRII.db reușită pentru fișa {nr_fisa}. Cotizație standard: {cotizatie_standard}")

                    # Salvare în DEPCRED.db
                    conn_d = sqlite3.connect(DB_DEPCRED)
                    cursor_d = conn_d.cursor()

                    dobanda = financial_data.get('dobanda', 0.0)
                    impr_deb = financial_data.get('impr_deb', 0.0)
                    impr_cred = financial_data.get('impr_cred', 0.0)
                    dep_deb = financial_data.get('dep_deb', 0.0)
                    dep_cred = financial_data.get('dep_cred', 0.0)

                    # Calculăm soldurile noi
                    impr_sold_nou = impr_deb - impr_cred  # Pentru membru nou, sold anterior e 0
                    dep_sold_nou = dep_deb - dep_cred  # Pentru membru nou, sold anterior e 0
                    prima_flag = 1  # Marcam ca fiind prima înregistrare

                    depcred_data = (
                        nr_fisa, luna, anul, dobanda, impr_deb, impr_cred, impr_sold_nou,
                        dep_deb, dep_cred, dep_sold_nou, prima_flag
                    )

                    logging.info(f"Inserare în DEPCRED (prima linie) pentru fișa {nr_fisa}...")
                    # Ștergem orice înregistrare existentă marcată ca 'prima' pentru această fișă
                    cursor_d.execute("DELETE FROM depcred WHERE nr_fisa=? AND prima=1", (nr_fisa,))
                    cursor_d.execute(
                        "INSERT INTO depcred (nr_fisa, luna, anul, dobanda, impr_deb, impr_cred, impr_sold, dep_deb, dep_cred, dep_sold, prima) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        depcred_data
                    )
                    conn_d.commit()
                    logging.info(f"Salvare în DEPCRED.db reușită pentru fișa {nr_fisa}.")

                    afiseaza_info("Membrul nou a fost adăugat cu succes în ambele baze de date!", parent=self)
                    self.reset_form(editabil=False, keep_nr_fisa=False)

                except sqlite3.IntegrityError as ie:
                    logging.error(f"Eroare Integritate SQLite pentru fișa {nr_fisa}: {ie}", exc_info=True)
                    afiseaza_eroare(f"Eroare: Numărul de fișă {nr_fisa} există deja în una dintre baze de date.",
                                    parent=self)
                except sqlite3.Error as e:
                    logging.error(f"Eroare SQLite la adăugare membru {nr_fisa}: {e}", exc_info=True)
                    afiseaza_eroare(f"Eroare la salvarea în baza de date:\n{e}", parent=self)
                except Exception as e:
                    logging.error(f"Eroare generală la adăugare membru {nr_fisa}: {e}", exc_info=True)
                    afiseaza_eroare(f"Eroare neașteptată la salvare:\n{e}", parent=self)
                finally:
                    if conn_m:
                        conn_m.close()
                    if conn_d:
                        conn_d.close()

        except ValueError as ve:
            afiseaza_eroare(f"Eroare la extragerea datelor numerice/datelor: {ve}", parent=self)
            return
        except Exception as e:
            afiseaza_eroare(f"Eroare la extragerea sau validarea datelor: {e}", parent=self)
            logging.error(f"Eroare extragere/validare date: {e}", exc_info=True)
            return

    @staticmethod
    def _get_member_data_from_db(nr_fisa):
        """Obține datele membre din baza de date."""
        conn = None
        data = None
        try:
            conn = sqlite3.connect(DB_MEMBRII)
            conn.row_factory = sqlite3.Row  # Returnează rânduri ca dicționare
            cur = conn.cursor()
            cur.execute("SELECT * FROM membrii WHERE NR_FISA = ?", (nr_fisa,))
            row = cur.fetchone()
            if row:
                data = dict(row)  # Setăm rezultatul dacă e găsit
        except sqlite3.Error as e:
            logging.error(f"Eroare citire membru {nr_fisa}: {e}")
        finally:
            if conn:
                conn.close()
        return data


# =========================================
# Testare directă
# =========================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if "Fusion" in QtWidgets.QStyleFactory.keys(): app.setStyle("Fusion")

    # Creare DB dummy dacă nu există
    if not os.path.exists(DB_MEMBRII):
        conn = sqlite3.connect(DB_MEMBRII)
        conn.execute("""
            CREATE TABLE membrii (
                NR_FISA INTEGER PRIMARY KEY, 
                NUM_PREN TEXT, 
                DOMICILIUL TEXT, 
                CALITATEA TEXT, 
                DATA_INSCR TEXT,
                COTIZATIE_STANDARD REAL DEFAULT 0.00
            )
        """)
        conn.close()

    if not os.path.exists(DB_DEPCRED):
        conn = sqlite3.connect(DB_DEPCRED)
        conn.execute("""
            CREATE TABLE depcred (
                id INTEGER PRIMARY KEY, 
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
        conn.close()

    window = QMainWindow()
    widget = AdaugareMembruWidget()
    window.setCentralWidget(widget)
    window.setWindowTitle("Test Adăugare Membru - Cu Formatări Vizuale Avansate")
    window.show()
    sys.exit(app.exec_())