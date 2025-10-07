# validari.py
import os
import re
import logging
import sqlite3 # Added import for sqlite3
import glob    # Added import for glob to find db files
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox, QApplication, QPushButton
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
import glob
import sys


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

# Configurare logging (opțional)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Stil comun pentru QMessageBox-uri (încercare de consistență)
DIALOG_STYLESHEET = """
    QMessageBox {
        background-color: #e8f1ff;
        font-family: Arial;
        font-size: 10pt;
    }
    QMessageBox QLabel#qt_msgbox_label { /* Țintește eticheta principală */
        color: #333;
    }
    QMessageBox QPushButton {
        background-color: #cce5ff;
        border: 1px solid #3399ff;
        padding: 8px 16px;
        border-radius: 6px;
        min-width: 80px; /* Lățime minimă butoane */
    }
    QMessageBox QPushButton:hover {
        background-color: #b3daff;
    }
    QMessageBox QPushButton:focus {
        outline: none; /* Elimină conturul la focus */
        border: 1px solid #0056b3; /* Evidențiază focusul subtil */
    }
"""

# --------------- DIALOG PERSONALIZAT (Da/Nu) ---------------


class CustomDialogYesNo(QMessageBox):
    """ Dialog cu două butoane: Da / Nu, stilizat. """
    def __init__(self, title: str, message: str, icon_path: str = None, parent=None):
        super().__init__(parent)
        self.setStyleSheet(DIALOG_STYLESHEET)  # Aplică stilul comun
        self.setWindowTitle(title)
        self.setText(message)
        # Setăm iconița standard pe baza titlului sau implicit Question
        if "confirmare" in title.lower() or "sigur" in message.lower():
            self.setIcon(QMessageBox.Question)
        elif "eroare" in title.lower():
            self.setIcon(QMessageBox.Critical)
        elif "atenție" in title.lower() or "avertisment" in message.lower():
            self.setIcon(QMessageBox.Warning)
        else:
            self.setIcon(QMessageBox.Information)

        # Adăugăm iconiță custom dacă e specificată și validă
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Butoane Da / Nu
        self.da_buton = self.addButton("Da", QMessageBox.YesRole)
        self.nu_buton = self.addButton("Nu", QMessageBox.NoRole)
        self.setDefaultButton(self.nu_buton)
        self.setMinimumWidth(400)


# --------------- FUNCȚII PENTRU AFIȘARE MESAJE ---------------

def _show_message_box(title: str, message: str, icon_type: QMessageBox.Icon, parent=None):
    """ Funcție helper internă pentru a afișa un QMessageBox stilizat. """
    box = QMessageBox(parent)  # Trecem parent aici
    box.setStyleSheet(DIALOG_STYLESHEET)
    box.setIcon(icon_type)
    box.setWindowTitle(title)
    box.setText(message)
    box.setStandardButtons(QMessageBox.Ok)
    box.exec_()


def afiseaza_eroare(mesaj: str, parent=None):
    """ Afișează un mesaj de eroare standard într-o fereastră de dialog. """
    logging.error(f"Eroare afișată utilizatorului: {mesaj}")  # Logăm eroarea
    _show_message_box("Eroare", mesaj, QMessageBox.Critical, parent)


def afiseaza_info(mesaj: str, parent=None):
    """ Afișează un mesaj de informare standard. """
    logging.info(f"Info afișat utilizatorului: {mesaj}")
    _show_message_box("Informație", mesaj, QMessageBox.Information, parent)


def afiseaza_warning(mesaj: str, parent=None):
    """ Afișează un mesaj de avertizare standard. """
    logging.warning(f"Warning afișat utilizatorului: {mesaj}")
    _show_message_box("Atenție", mesaj, QMessageBox.Warning, parent)


# --------------- FUNCȚIA CARE INTEROGHEAZĂ MODIFICAREA ---------------
# **MODIFICAT**: Acum returnează True/False în loc să apeleze direct
def anunta_membru_existent(parent_widget, nr_fisa) -> bool:
    """
    Dacă fișa există, întreabă dacă se dorește modificarea.
    Returnează True dacă utilizatorul alege 'Da', False altfel.
    """
    dialog = CustomDialogYesNo(
        title="Membru existent",
        message=f"Membrul cu fișa {nr_fisa} există deja.\nDoriți modificarea datelor?",
        parent=parent_widget
    )
    result = dialog.exec_()
    return dialog.clickedButton() == dialog.da_buton


# --------------- FUNCȚIA CARE INTEROGHEAZĂ ADĂUGAREA ---------------
# **MODIFICAT**: Acum returnează True/False în loc să apeleze reset_form
def anunta_membru_inexistent(parent_widget, nr_fisa) -> bool:
    """
    Dacă fișa NU există, întreabă dacă se dorește adăugarea.
    Returnează True dacă utilizatorul alege 'Da', False altfel.
    """
    dialog = CustomDialogYesNo(
        title="Fișă inexistentă",
        message=f"Numărul de fișă {nr_fisa} nu există.\nDoriți adăugarea unui membru nou?",
        parent=parent_widget
    )
    result = dialog.exec_()
    return dialog.clickedButton() == dialog.da_buton


# --------------- ALTE FUNCȚII DE VALIDARE (neschimbate) ---------------
def extrage_text(widget):
    """ Extrage textul curățat dintr-un widget QLineEdit sau QTextEdit. """
    if hasattr(widget, "toPlainText"):
        return widget.toPlainText().strip()
    elif hasattr(widget, "text"):
        return widget.text().strip()
    return ""


def verifica_campuri_completate(widget, campuri_obligatorii: list, nume_campuri: dict = None):
    """ Verifică dacă o listă de câmpuri obligatorii sunt completate. """
    for camp in campuri_obligatorii:
        valoare = extrage_text(camp)
        if not valoare:
            nume_afisat = "Necunoscut"
            if nume_campuri and camp in nume_campuri:
                nume_afisat = nume_campuri[camp]
            elif hasattr(camp, 'objectName'):
                nume_afisat = camp.objectName()
            afiseaza_eroare(f"Câmpul '{nume_afisat}' trebuie completat.", parent=widget)
            if hasattr(camp, 'setFocus'):
                camp.setFocus()
            return False
    return True


def valideaza_an(an_str: str, min_an=1900, max_an=2100) -> bool:
    """ Verifică dacă stringul este un an valid (4 cifre în range). """
    return an_str.isdigit() and min_an <= int(an_str) <= max_an


def valideaza_luna(luna_str: str) -> bool:
    """ Verifică dacă stringul este o lună validă (1-12). """
    return luna_str.isdigit() and 1 <= int(luna_str) <= 12


def verifica_format_data(widget, camp_data, silent=False):
    """ Verifică formatul datei în DD-MM-YYYY sau YYYY-MM-DD și validitatea acesteia. """
    data_str = extrage_text(camp_data)

    # Verificăm formatul standard DD-MM-YYYY
    try:
        datetime.strptime(data_str, '%d-%m-%Y')
        return True
    except ValueError:
        # Dacă nu este în formatul standard, verificăm formatul YYYY-MM-DD
        try:
            # Verificăm dacă e în format YYYY-MM-DD
            data_obj = datetime.strptime(data_str, '%Y-%m-%d')

            # Dacă dorim să convertim automat la formatul DD-MM-YYYY (opțional)
            # data_str_convertita = data_obj.strftime('%d-%m-%Y')
            # if hasattr(camp_data, 'setText'):
            #     camp_data.setText(data_str_convertita)

            return True
        except ValueError:
            if not silent:
                afiseaza_warning(
                    f"Data '{data_str}' nu este validă sau nu respectă formatul DD-MM-YYYY sau YYYY-MM-DD.",
                    parent=widget)
            return False


def verifica_format_luna_an(widget, camp_luna_an, silent=False):
    """ Verifică formatul MM-YYYY și validitatea lunii/anului. """
    valoare = extrage_text(camp_luna_an)
    match = re.match(r"^(0[1-9]|1[0-2])-(\d{4})$", valoare)
    if match:
        luna_str, an_str = match.groups()
        if valideaza_an(an_str):
            return True
    if not silent:
        afiseaza_warning(f"Formatul din câmpul Luna-An trebuie să fie LL-AAAA"f"  (ex: 04-2024) .", parent=widget)
    return False


def valideaza_numar_real(valoare_str: str) -> bool:
    """ Verifică dacă un șir poate fi convertit într-un float valid. """
    if not isinstance(valoare_str, str):
        return False
    try:
        float(valoare_str.replace(',', '.'))
        return True
    except ValueError:
        return False


def verifica_numere(widget, campuri: list, nume_campuri: dict = None):
    """ Verifică dacă valorile câmpurilor sunt numere reale valide. """
    for camp in campuri:
        text = extrage_text(camp)
        if text and not valideaza_numar_real(text):
            nume_afisat = "Necunoscut"
            if nume_campuri and camp in nume_campuri:
                nume_afisat = nume_campuri[camp]
            elif hasattr(camp, 'objectName'):
                nume_afisat = camp.objectName()
            afiseaza_eroare(f"Valoarea '{text}' din câmpul '{nume_afisat}' nu este un număr valid.", parent=widget)
            if hasattr(camp, 'setFocus'):
                camp.setFocus()
            return False
    return True


def valideaza_nr_fisa(valoare: str) -> bool:
    """ Validează dacă valoarea este un număr pozitiv întreg. """
    return valoare.isdigit() and int(valoare) > 0




