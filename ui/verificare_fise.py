import os
import sqlite3
import sys
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QFrame, QScrollArea, QTextEdit, QSizePolicy, QCompleter,
    QMessageBox, QPushButton
)

if getattr(sys, 'frozen', False):
    # Daca aplicatia este impachetata (ruleaza din executabil)
    # os.path.dirname(sys.executable) va fi directorul care contine executabilul (in onedir mode)
    # Sau directorul temporar in onefile mode (dar onefile e mai complicat pt fisiere externe)
    # Presupunem onedir mode si bazele de date sunt langa exe
    BASE_RESOURCE_PATH = os.path.dirname(sys.executable)
else:
    # Daca ruleaza din scriptul sursa Python (in timpul dezvoltarii)
    # __file__ este calea catre scriptul curent (ex. ui/dividende.py)
    # os.path.dirname(__file__) este directorul scriptului curent (ex. ui)
    # os.path.join(..., "..") urca un nivel (la directorul radacina al proiectului)
    BASE_RESOURCE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# Definim caile catre bazele de date relative la directorul de resurse
DB_MEMBRII = os.path.join(BASE_RESOURCE_PATH, "MEMBRII.db")
DB_DEPCRED = os.path.join(BASE_RESOURCE_PATH, "DEPCRED.db")
DB_ACTIVI = os.path.join(BASE_RESOURCE_PATH, "ACTIVI.db")
DB_INACTIVI = os.path.join(BASE_RESOURCE_PATH, "INACTIVI.db")
DB_CHITANTE = os.path.join(BASE_RESOURCE_PATH, "CHITANTE.db")
DB_LICHIDATI = os.path.join(BASE_RESOURCE_PATH, "LICHIDATI.db")


# --------------------------------------------------------------------
# Subclasa pentru sincronizarea poziției de scroll în QTextEdit-uri
# --------------------------------------------------------------------
class SyncedTextEdit(QTextEdit):
    """
    QTextEdit care, la fiecare eveniment de wheel,
    setează automat aceeași poziție de scroll în celelalte text edit-uri din grup.
    """

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


# --------------------------------------------------------------------
# Widget principal pentru verificarea fișelor
# --------------------------------------------------------------------
class VerificareFiseWidget(QWidget):
    def __init__(self, parent=None):
        super(VerificareFiseWidget, self).__init__(parent)
        self.verificare_activa = False
        self.loaded_nr_fisa = None  # Pentru a ține minte fișa încărcată pentru query-uri DB

        # Layoutul principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)

        self.apply_styles()  # Aplică stilurile generale

        # ================ Header (Date personale) ================
        self.header_frame = QFrame()
        self.header_frame.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8fbff, stop:1 #e7f3ff); 
                border: 2px solid #4a90e2;
                border-radius: 10px; 
                padding: 10px;
            }
            QLabel { 
                color: #2c3e50; 
                font-weight: bold; 
                padding: 4px;
                background: transparent;
                border: none;
            }
            QLineEdit {
                background-color: #ffffff; 
                border: 2px solid #b3d1ff;
                border-radius: 6px; 
                padding: 6px 10px;
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
            """
        )
        self.header_layout = QGridLayout(self.header_frame)
        self.header_layout.setContentsMargins(15, 12, 15, 12)
        self.header_layout.setSpacing(12)

        # Câmpuri din header
        self.lbl_nume = QLabel("Nume Prenume:")
        self.txt_nume = QLineEdit()
        self.txt_nume.setPlaceholderText("Introduceți numele și apăsați Enter sau selectați...")
        self.txt_nume.setToolTip("Introduceți primele litere ale numelui și selectați din listă")

        self.lbl_adresa = QLabel("Adresa:")
        self.txt_adresa = QLineEdit()
        self.txt_adresa.setReadOnly(True)

        self.lbl_calitate = QLabel("Calitatea:")
        self.txt_calitate = QLineEdit()
        self.txt_calitate.setReadOnly(True)

        self.lbl_data_insc = QLabel("Data înscrierii:")
        self.txt_data_insc = QLineEdit()
        self.txt_data_insc.setReadOnly(True)

        self.lbl_nr_fisa = QLabel("Număr Fișă:")
        self.txt_nr_fisa = QLineEdit()
        self.txt_nr_fisa.setReadOnly(True)

        # MODIFICARE 1 & 2: Elimin eticheta "Golește formular" și schimb textul butonului
        self.reset_button = QPushButton("Golește formular")
        self.reset_button.setFixedHeight(35)
        self.reset_button.setObjectName("resetButton")
        self.reset_button.setToolTip("Resetează formularul pentru o nouă căutare")
        self.reset_button.setCursor(Qt.PointingHandCursor)

        # MODIFICARE 3: Rocada între Calitatea și Data înscrierii
        # Noul layout:
        # Rândul 0: Nume Prenume + Data înscrierii
        self.header_layout.addWidget(self.lbl_nume, 0, 0)
        self.header_layout.addWidget(self.txt_nume, 0, 1)
        self.header_layout.addWidget(self.lbl_data_insc, 0, 2)
        self.header_layout.addWidget(self.txt_data_insc, 0, 3)

        # Rândul 1: Adresa + Număr Fișă
        self.header_layout.addWidget(self.lbl_adresa, 1, 0)
        self.header_layout.addWidget(self.txt_adresa, 1, 1)
        self.header_layout.addWidget(self.lbl_nr_fisa, 1, 2)
        self.header_layout.addWidget(self.txt_nr_fisa, 1, 3)

        # Rândul 2: Calitatea + Golește formular (fără eticheta suplimentară)
        self.header_layout.addWidget(self.lbl_calitate, 2, 0)
        self.header_layout.addWidget(self.txt_calitate, 2, 1)
        # Spacer pentru a împinge butonul la dreapta
        self.header_layout.addItem(
            QtWidgets.QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum), 2, 2
        )
        self.header_layout.addWidget(self.reset_button, 2, 3)

        # Ajustare stretching coloane
        self.header_layout.setColumnStretch(1, 2)
        self.header_layout.setColumnStretch(3, 1)

        self.main_layout.addWidget(self.header_frame)

        # ================ Zona scrollabilă pentru secțiunile financiare ================
        scroll_container = QWidget()
        scroll_hbox = QHBoxLayout(scroll_container)
        scroll_hbox.setContentsMargins(0, 0, 0, 0)
        scroll_hbox.setSpacing(8)

        columns_frame = QFrame()
        columns_frame.setStyleSheet(
            "QFrame { border: none; background-color: transparent; padding: 0px; }"
        )
        columns_layout = QHBoxLayout(columns_frame)
        columns_layout.setContentsMargins(0, 0, 0, 0)
        columns_layout.setSpacing(8)

        # Secțiunea Împrumuturi - Stil îmbunătățit
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

        # Secțiunea Data (Luna-An) - Stil îmbunătățit
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
        lbl_data_header = QLabel("Dată")
        lbl_data_header.setAlignment(Qt.AlignCenter)
        lbl_data_header.setFixedHeight(lbl_imprumuturi.sizeHint().height())
        lbl_data_header.setStyleSheet(
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
        date_section_layout.addWidget(lbl_data_header)
        luna_an_container = QWidget()
        luna_an_layout = QVBoxLayout(luna_an_container)
        luna_an_layout.setContentsMargins(0, 0, 0, 0)
        luna_an_layout.setSpacing(0)
        self.col_luna_an = self.create_financial_column("Luna-An", add_label=True)
        luna_an_layout.addLayout(self.col_luna_an["layout"], stretch=1)
        date_section_layout.addWidget(luna_an_container)

        # Secțiunea Depuneri - Stil îmbunătățit
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
        self.col_dep_sold = self.create_financial_column("Sold Depuneri")
        deposit_columns_layout.addLayout(self.col_dep_deb["layout"])
        deposit_columns_layout.addLayout(self.col_dep_cred["layout"])
        deposit_columns_layout.addLayout(self.col_dep_sold["layout"])
        deposit_section_layout.addWidget(deposit_columns_container)

        # Adăugăm secțiunile în containerul principal
        columns_layout.addWidget(loan_section, stretch=4)
        columns_layout.addWidget(date_section, stretch=1)
        columns_layout.addWidget(deposit_section, stretch=3)
        scroll_hbox.addWidget(columns_frame)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(scroll_container)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.main_layout.addWidget(self.scroll_area, stretch=1)

        # Colectăm referințele la coloanele financiare
        self.coloane_financiare = [
            self.col_dobanda["text_edit"], self.col_impr_deb["text_edit"],
            self.col_impr_cred["text_edit"], self.col_impr_sold["text_edit"],
            self.col_luna_an["text_edit"], self.col_dep_deb["text_edit"],
            self.col_dep_cred["text_edit"], self.col_dep_sold["text_edit"]
        ]
        for te in self.coloane_financiare:
            te.siblings = self.coloane_financiare

        # ================= Autocomplete + logica DB =================
        self.update_completer_flag = True
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchStartsWith)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.txt_nume.setCompleter(self.completer)

        self.txt_nume.textChanged.connect(self.update_completer_model)
        self.completer.activated[str].connect(self.auto_populate_fields)
        self.completer.highlighted.connect(
            lambda: setattr(self, 'update_completer_flag', False)
        )
        self.txt_nume.editingFinished.connect(self.handle_nume_editing_finished)
        self.reset_button.clicked.connect(self.reset_form)

        self.txt_nume.setFocus()
        self.reset_form()

    def create_financial_column(self, title, add_label=True):
        """Creează o coloană financiară (Label + SyncedTextEdit) cu stil îmbunătățit."""
        text_edit = SyncedTextEdit(siblings=[])
        text_edit.setReadOnly(True)
        text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        font = QFont("Consolas", 10)
        if not font.exactMatch():
            font = QFont("Courier New", 10)
        text_edit.setFont(font)
        text_edit.setStyleSheet(
            """
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
            QTextEdit:focus {
                border-color: #4a90e2;
                background-color: #fafbfc;
            }
            """
        )

        label = None
        layout = QVBoxLayout()
        layout.setSpacing(0)
        if add_label:
            label = QLabel(title)
            label.setAlignment(Qt.AlignCenter)
            label.setFixedHeight(32)
            label.setStyleSheet(
                """
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
                """
            )
            layout.addWidget(label)
        layout.addWidget(text_edit, stretch=1)
        return {"layout": layout, "label": label, "text_edit": text_edit}

    def apply_styles(self):
        """Aplică stiluri globale widget-ului cu îmbunătățiri vizuale."""
        self.setStyleSheet(
            """
            VerificareFiseWidget, QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
            QScrollArea { 
                border: none; 
                background-color: transparent;
            }
            /* ScrollBar cu stil modern */
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
            /* Stil pentru butonul de resetare îmbunătățit */
            QPushButton#resetButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff6b6b, stop:1 #ee5a52);
                border: 2px solid #e74c3c;
                border-radius: 8px;
                font-size: 10pt;
                font-weight: bold;
                padding: 8px 16px;
                color: white;
                min-width: 120px;
            }
            QPushButton#resetButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff7b7b, stop:1 #ff6b6b);
                border-color: #dc3545;
                transform: translateY(-1px);
            }
            QPushButton#resetButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ee5a52, stop:1 #e74c3c);
                transform: translateY(0px);
            }
            """
        )
        font = QFont("Segoe UI", 10)
        self.setFont(font)

    def hideEvent(self, event):
        """Resetează formularul când widget-ul devine invizibil."""
        print("VerificareFiseWidget ascuns. Se resetează formularul.")
        self.reset_form()
        super(VerificareFiseWidget, self).hideEvent(event)

    def handle_nume_editing_finished(self):
        """Se apelează când utilizatorul termină editarea câmpului Nume."""
        if not self.update_completer_flag:
            self.update_completer_flag = True
            return

        entered_name = self.txt_nume.text().strip()
        if not entered_name:
            self.reset_form()
            return

        current_completion = self.completer.currentCompletion()
        if current_completion and current_completion.upper() == entered_name.upper():
            print(f"Editing Finished: '{entered_name}' corespunde sugestiei '{current_completion}'.")
        else:
            print(f"Editing Finished: '{entered_name}' NU corespunde sugestiei '{current_completion}'.")
        self.update_completer_flag = True

    def update_completer_model(self):
        """Actualizează modelul QCompleter bazat pe textul introdus."""
        if not self.update_completer_flag:
            return

        prefix = self.txt_nume.text().strip()
        if len(prefix) < 2:
            self.completer.setModel(None)
            return

        name_dict = self.get_names_starting_with(prefix)
        all_names = list(name_dict.keys())
        model = QStringListModel(all_names, self.completer)
        self.completer.setModel(model)

        if all_names and self.txt_nume.hasFocus() and not self.completer.popup().isVisible():
            self.completer.complete()

    @staticmethod
    def get_names_starting_with(prefix):
        """Returnează un dicționar {NumePrenume: NR_FISA} pentru membrii ale căror nume încep cu prefix."""
        results = {}
        conn = None
        db_path = DB_MEMBRII
        print(f"[DEBUG] Connecting to MEMBRII DB for names at: {os.path.abspath(db_path)}")
        if not os.path.exists(db_path):
            print(f"[ERROR] Database file NOT FOUND at: {os.path.abspath(db_path)}")
            return results
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT NR_FISA, NUM_PREN FROM membrii WHERE NUM_PREN LIKE ? COLLATE NOCASE ORDER BY NUM_PREN",
                (prefix + '%',)
            )
            results = {row[1]: row[0] for row in cursor.fetchall()}
        except sqlite3.Error as e:
            print(f"Eroare SQLite la get_names_starting_with pentru '{prefix}': {e}")
        finally:
            if conn:
                conn.close()
        return results

    def _format_istoric_line_advanced(self, row_data, sold_impr_prec, sold_dep_prec, bg_color):
        """
        Formatează un rând de istoric cu aceleași reguli ca în sume_lunare.py

        Structura row_data:
        row[0] = NR_FISA, row[1] = DOBANDA, row[2] = IMPR_DEB, row[3] = IMPR_CRED,
        row[4] = IMPR_SOLD, row[5] = LUNA, row[6] = ANUL, row[7] = DEP_DEB,
        row[8] = DEP_CRED, row[9] = DEP_SOLD, row[10] = PRIMA
        """
        try:
            # Conversie la Decimal pentru calcule precise
            dobanda = Decimal(str(row_data[1] or '0.00')).quantize(Decimal('0.01'), ROUND_HALF_UP)
            impr_deb = Decimal(str(row_data[2] or '0.00')).quantize(Decimal('0.01'), ROUND_HALF_UP)
            impr_cred = Decimal(str(row_data[3] or '0.00')).quantize(Decimal('0.01'), ROUND_HALF_UP)
            impr_sold = Decimal(str(row_data[4] or '0.00')).quantize(Decimal('0.01'), ROUND_HALF_UP)
            luna = int(row_data[5] or 0)
            anul = int(row_data[6] or 0)
            dep_deb = Decimal(str(row_data[7] or '0.00')).quantize(Decimal('0.01'), ROUND_HALF_UP)
            dep_cred = Decimal(str(row_data[8] or '0.00')).quantize(Decimal('0.01'), ROUND_HALF_UP)
            dep_sold = Decimal(str(row_data[9] or '0.00')).quantize(Decimal('0.01'), ROUND_HALF_UP)

            # Conversie solduri precedente la Decimal
            sold_impr_prec = Decimal(str(sold_impr_prec or '0.00'))
            sold_dep_prec = Decimal(str(sold_dep_prec or '0.00'))

            # Inițializare valori formatate cu fundal
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
            # Logica complexă pentru rata neachitată/nouă
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
        if not self.loaded_nr_fisa or prev_anul <= 0:
            return False

        conn = None
        try:
            conn = sqlite3.connect(DB_DEPCRED)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT impr_deb FROM depcred WHERE nr_fisa = ? AND luna = ? AND anul = ?",
                (self.loaded_nr_fisa, prev_luna, prev_anul)
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

    def auto_populate_fields(self, selected_name):
        """Populează câmpurile când un nume valid este selectat din completer."""
        if self.verificare_activa:
            return
        self.verificare_activa = True
        self.update_completer_flag = False

        print(f"Completer Activated: Se populează pentru '{selected_name}'")

        if self.txt_nume.text() != selected_name:
            self.txt_nume.setText(selected_name)

        nr_fisa = self.get_nr_fisa_for_name(selected_name)
        if not nr_fisa:
            print(f"EROARE: Membrii '{selected_name}' nu a fost găsit în DB!")
            QMessageBox.critical(
                self, "Eroare Internă",
                f"Membrul '{selected_name}' nu a putut fi găsit."
            )
            self.reset_form()
            self.verificare_activa = False
            self.update_completer_flag = True
            return

        # Salvăm nr_fisa pentru query-uri ulterioare
        self.loaded_nr_fisa = nr_fisa

        print(f"Fișa {nr_fisa} găsită. Se populează datele...")
        member_data = self.get_member_data_from_membrii(nr_fisa)
        if member_data:
            self.txt_calitate.setText(member_data.get("CALITATEA", ""))
            self.txt_adresa.setText(member_data.get("DOMICILIUL", ""))
            self.txt_data_insc.setText(member_data.get("DATA_INSCR", ""))
            self.txt_nr_fisa.setText(str(member_data.get("NR_FISA", "")))
            self.txt_adresa.setToolTip(member_data.get("DOMICILIUL", ""))
            self.txt_calitate.setToolTip(member_data.get("CALITATEA", ""))
            self.txt_data_insc.setToolTip(member_data.get("DATA_INSCR", ""))
            self.txt_nr_fisa.setToolTip(str(member_data.get("NR_FISA", "")))
        else:
            print(f"Nu s-au găsit date în MEMBRII pentru fișa {nr_fisa}")
            self.txt_calitate.clear()
            self.txt_adresa.clear()
            self.txt_data_insc.clear()
            self.txt_nr_fisa.setText(str(nr_fisa))

        depcred_data = self.get_member_details(nr_fisa)
        for text_edit_widget in self.coloane_financiare:
            text_edit_widget.clear()

        if not depcred_data:
            print(f"Nu există intrări DEPCRED pentru fișa {nr_fisa}")
        else:
            # APLICARE FORMATĂRI VIZUALE AVANSATE
            lines = {widget: [] for widget in (
                self.col_dobanda["text_edit"],
                self.col_impr_deb["text_edit"],
                self.col_impr_cred["text_edit"],
                self.col_impr_sold["text_edit"],
                self.col_luna_an["text_edit"],
                self.col_dep_deb["text_edit"],
                self.col_dep_cred["text_edit"],
                self.col_dep_sold["text_edit"]
            )}

            # Procesăm datele în ordine pentru a calcula soldurile precedente corect
            # depcred_data vine sortat DESC (cel mai recent primul)
            sold_impr_prec = Decimal('0.00')
            sold_dep_prec = Decimal('0.00')

            for i, row in enumerate(depcred_data):
                # Fundaluri alternate îmbunătățite
                bg_color = "#f8fbff" if i % 2 == 0 else "#f0f7ff"

                # Pentru calculul soldurilor precedente, avem nevoie să parcurgem în ordine inversă
                # Pentru moment, folosim soldurile din DB direct
                if i < len(depcred_data) - 1:
                    next_row = depcred_data[i + 1]
                    sold_impr_prec = Decimal(str(next_row[4] or '0.00'))
                    sold_dep_prec = Decimal(str(next_row[9] or '0.00'))
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

        self.verificare_activa = False
        self.update_completer_flag = True

    @staticmethod
    def get_nr_fisa_for_name(name):
        """Găsește NR_FISA pentru un nume exact (case-insensitive)."""
        if not name:
            return None
        conn = None
        db_path = DB_MEMBRII
        print(f"[DEBUG] Connecting to MEMBRII DB for NR_FISA at: {os.path.abspath(db_path)}")
        if not os.path.exists(db_path):
            print(f"[ERROR] Database file NOT FOUND at: {os.path.abspath(db_path)}")
            return None
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute(
                "SELECT NR_FISA FROM membrii WHERE NUM_PREN = ? COLLATE NOCASE",
                (name,)
            )
            row = cur.fetchone()
            return row[0] if row else None
        except sqlite3.Error as e:
            print(f"Eroare SQLite la get_nr_fisa_for_name pentru '{name}': {e}")
        finally:
            if conn:
                conn.close()
        return None

    @staticmethod
    def get_member_data_from_membrii(nr_fisa):
        """Obține datele personale ale unui membru după NR_FISA."""
        if not nr_fisa:
            return None
        conn = None
        db_path = DB_MEMBRII
        print(f"[DEBUG] Connecting to MEMBRII DB for member data at: {os.path.abspath(db_path)}")
        if not os.path.exists(db_path):
            print(f"[ERROR] Database file NOT FOUND at: {os.path.abspath(db_path)}")
            return None
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(
                "SELECT NR_FISA, NUM_PREN, CALITATEA, DOMICILIUL, DATA_INSCR "
                "FROM membrii WHERE NR_FISA = ?",
                (nr_fisa,)
            )
            row = cur.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"Eroare SQLite la get_member_data_from_membrii pentru fișa {nr_fisa}: {e}")
        finally:
            if conn:
                conn.close()
        return None

    @staticmethod
    def get_member_details(nr_fisa):
        """
        Returnează toate liniile din DEPCRED pentru un NR_FISA,
        sortate descrescător după an și lună.
        """
        if not nr_fisa:
            return []
        data = []
        conn = None
        db_path = DB_DEPCRED
        print(f"[DEBUG] Connecting to DEPCRED DB for member details at: {os.path.abspath(db_path)}")
        if not os.path.exists(db_path):
            print(f"[ERROR] Database file NOT FOUND at: {os.path.abspath(db_path)}")
            return []
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("""
                SELECT nr_fisa, dobanda, impr_deb, impr_cred, impr_sold,
                       luna, anul, dep_deb, dep_cred, dep_sold, prima
                FROM depcred WHERE nr_fisa = ? ORDER BY anul DESC, luna DESC
            """, (nr_fisa,))
            data = cur.fetchall()
        except sqlite3.Error as e:
            print(f"Eroare SQLite la get_member_details pentru fișa {nr_fisa}: {e}")
        finally:
            if conn:
                conn.close()
        return data

    def reset_form(self):
        """Resetează toate câmpurile la starea inițială."""
        print("Resetare formular VerificareFiseWidget...")
        self.loaded_nr_fisa = None

        self.txt_nume.clear()
        self.txt_adresa.clear()
        self.txt_calitate.clear()
        self.txt_data_insc.clear()
        self.txt_nr_fisa.clear()

        self.txt_nume.setToolTip("Introduceți primele litere ale numelui și selectați din listă")
        self.txt_adresa.setToolTip("")
        self.txt_calitate.setToolTip("")
        self.txt_data_insc.setToolTip("")
        self.txt_nr_fisa.setToolTip("")

        for text_edit_widget in self.coloane_financiare:
            text_edit_widget.clear()

        self.completer.setModel(None)
        self.update_completer_flag = True
        self.verificare_activa = False

        self.txt_nume.setFocus()


if __name__ == "__main__":
    DB_MEMBRII = "MEMBRII.db"
    DB_DEPCRED = "DEPCRED.db"
    if not os.path.exists(DB_MEMBRII):
        QMessageBox.critical(
            None,
            "Eroare Fatală",
            f"Baza de date '{DB_MEMBRII}' nu a fost găsită!"
        )
        sys.exit(1)
    if not os.path.exists(DB_DEPCRED):
        QMessageBox.critical(
            None,
            "Eroare Fatală",
            f"Baza de date '{DB_DEPCRED}' nu a fost găsită!"
        )
        sys.exit(1)

    app = QApplication(sys.argv)
    if "Fusion" in QtWidgets.QStyleFactory.keys():
        app.setStyle("Fusion")

    test_window = QMainWindow()
    test_window.setWindowTitle("Test Verificare Fișe - Cu Formatări Vizuale Avansate")
    widget = VerificareFiseWidget()
    test_window.setCentralWidget(widget)
    test_window.setMinimumSize(820, 550)
    test_window.show()
    sys.exit(app.exec_())