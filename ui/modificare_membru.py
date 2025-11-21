import sqlite3
import logging

from PyQt5.QtWidgets import QMessageBox, QPushButton
from PyQt5.QtCore import Qt
import sys
import os

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


def executa(nr_fisa, parent_widget):
    """
    1) Face câmpul 'Număr fișă' inactiv.
    2) Activează câmpurile editabile (nume, adresă, calitate, data înscrierii).
    3) Adaugă un buton 'Actualizează date' lângă butonul 'X' și îl conectează la finalizarea modificării.
    """

    # 1) 'Număr fișă' devine inactiv
    parent_widget.nr_fisa_input.setEnabled(False)

    # 2) Activează câmpurile
    parent_widget.nume_input.setEnabled(True)
    parent_widget.adresa_input.setEnabled(True)
    parent_widget.calitate_input.setEnabled(True)
    parent_widget.data_input.setEnabled(True)

    # 3) Creăm un buton "Actualizează date"
    #    Având în vedere structura din adaugare_membru.py, butonul 'X' era plasat pe randul 0, col 4,
    #    iar grid-ul este stocat în 'header_layout' (dacă l-ai salvat ca atribut).
    #    Dacă layout-ul nu este disponibil direct, creezi un loc unde să așezi butonul.
    #    Mai simplu e să-l așezi lângă reset_button prin cod. Exemplu:
    parent_widget.btn_actualizeaza = QPushButton("Actualizează date", parent_widget)
    parent_widget.btn_actualizeaza.setObjectName("actualizare_button")
    parent_widget.btn_actualizeaza.setToolTip("Salvează modificările în bază de date")

    # Un mic stil, asemănător butoanelor albastre:
    parent_widget.btn_actualizeaza.setStyleSheet("""
        QPushButton#actualizare_button {
            background-color: #cce5ff;
            border: 1px solid #3399ff;
            padding: 4px 8px;
            border-radius: 6px;
        }
        QPushButton#actualizare_button:hover {
            background-color: #b3daff;
        }
    """)

    # Așezăm butonul în același rând cu butonul 'X'.
    # Observăm în adaugare_membru.py că butonul X era adăugat cu
    #   header_layout.addWidget(self.reset_button, 0, 4, Qt.AlignRight | Qt.AlignBottom)
    # Putem pune butonul "Actualizează date" în col 3 sau 4 etc., cum preferi:
    try:
        # dacă ai salvat la init: self.header_frame, self.header_layout = ...
        header_layout = parent_widget.header_frame.layout()
        header_layout.addWidget(parent_widget.btn_actualizeaza, 2, 3, Qt.AlignRight | Qt.AlignBottom)
    except AttributeError:
        # Dacă layout-ul nu e disponibil direct, te asiguri că-l expui (de ex. parent_widget.header_layout).
        pass

    # Asigurăm că, la click, se apelează funcția care finalizează modificarea
    parent_widget.btn_actualizeaza.clicked.connect(
        lambda: finalize_update(nr_fisa, parent_widget)
    )


def finalize_update(nr_fisa, parent_widget):
    """
    4) Colectează datele editate și le scrie în 'MEMBRII.db'.
    5) Afișează un mesaj (stilizat sau nu) că operația a reușit (ori eroare).
    """

    # Colectăm valorile
    nume = parent_widget.nume_input.text().strip()
    adresa = parent_widget.adresa_input.text().strip()
    calitate = parent_widget.calitate_input.text().strip()
    data_inscr = parent_widget.data_input.text().strip()

    try:
        conn = sqlite3.connect("MEMBRII.db", timeout=30.0)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE membrii
               SET NUM_PREN=?,
                   DOMICILIUL=?,
                   CALITATEA=?,
                   DATA_INSCR=?
             WHERE NR_FISA=?
        """, (nume, adresa, calitate, data_inscr, nr_fisa))
        conn.commit()
        conn.close()

        # Afișăm un mesaj de succes
        show_stylized_message(
            parent_widget,
            "Succes",
            "Datele membrului au fost actualizate cu succes!"
        )

        # După mesaj, scoatem butonul "Actualizează date"
        layout = parent_widget.header_frame.layout()
        if hasattr(parent_widget, "btn_actualizeaza"):
            layout.removeWidget(parent_widget.btn_actualizeaza)
            parent_widget.btn_actualizeaza.deleteLater()
            del parent_widget.btn_actualizeaza

    except sqlite3.Error as e:
        logging.error(f"Eroare la actualizarea membrului {nr_fisa}: {e}", exc_info=True)
        show_stylized_message(
            parent_widget,
            "Eroare",
            f"A apărut o eroare la actualizarea datelor:\n{str(e)}",
            icon="warning"
        )


def show_stylized_message(parent, title, text, icon="info"):
    """
    Exemplu de mesaj de tip 'Ok' cu stil apropiat de cel din listari.py.
    Dacă vrei exact un 'CustomDialogOk', îl poți defini la fel cum ai definit 'CustomDialogYesNo'.
    Deocamdată, folosim un QMessageBox cu un stylesheet minimal.
    """
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(text)

    # Stil minimal, copiat din listari.py / validari.py
    msg.setStyleSheet("""
        QMessageBox {
            background-color: #e8f1ff;
            font-family: Arial;
            font-size: 10pt;
        }
        QMessageBox QLabel {
            font-weight: bold;
            color: #333;
        }
        QMessageBox QPushButton {
            background-color: #cce5ff;
            border: 1px solid #3399ff;
            padding: 8px 16px;
            border-radius: 6px;
        }
        QMessageBox QPushButton:hover {
            background-color: #b3daff;
        }
    """)

    if icon == "info":
        msg.setIcon(QMessageBox.Information)
    elif icon == "warning":
        msg.setIcon(QMessageBox.Warning)

    msg.exec_()
