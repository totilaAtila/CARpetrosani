import sqlite3
import logging
from datetime import datetime

from PyQt5.QtWidgets import QMessageBox, QPushButton
from PyQt5.QtCore import Qt

# Importăm validările
from ui.validari import (
    verifica_campuri_completate,
    verifica_format_data,
    verifica_format_luna_an,
    verifica_numere,
    extrage_text
)


def executa(nr_fisa, parent_widget):
    """
    - Setează nr_fisa_input și îl dezactivează (sau nu, dacă vrei să-l poată schimba)
    - Activează câmpurile (nume, adresă, calitate, data înscrierii)
    - Activează coloanele financiare (readOnly=False)
    - Completează automat col_luna_an cu LL-AAAA (de ex. luna și anul curent)
    - Adaugă buton "Salvează membru nou"
    """
    # 1) Settez nr_fisa și (opțional) îl dezactivez
    parent_widget.nr_fisa_input.setText(nr_fisa)
    parent_widget.nr_fisa_input.setEnabled(False)

    # 2) Activez câmpurile text (header)
    parent_widget.nume_input.setEnabled(True)
    parent_widget.adresa_input.setEnabled(True)
    parent_widget.calitate_input.setEnabled(True)
    parent_widget.data_input.setEnabled(True)

    # Pune data curentă dacă e goală
    if not parent_widget.data_input.text().strip():
        parent_widget.data_input.setText(datetime.now().strftime('%d-%m-%Y'))

    # 3) Activez coloanele financiare (readOnly=False)
    for col_te in parent_widget.coloane_financiare:
        col_te.setReadOnly(False)

    # Completez automat col_luna_an cu data curentă
    # (prima linie)
    current_month = datetime.now().month
    current_year = datetime.now().year
    parent_widget.col_luna_an["text_edit"].setText(f"{current_month:02d}-{current_year}")

    # 4) Creez buton "Salvează membru nou"
    parent_widget.btn_salveaza_nou = QPushButton("Salvează membru nou", parent_widget)
    parent_widget.btn_salveaza_nou.setObjectName("btn_salveaza_nou")
    parent_widget.btn_salveaza_nou.setToolTip("Va adăuga un nou membru în baza de date + date financiare")
    parent_widget.btn_salveaza_nou.setStyleSheet("""
        QPushButton#btn_salveaza_nou {
            background-color: #cce5ff;
            border: 1px solid #3399ff;
            padding: 4px 8px;
            border-radius: 6px;
        }
        QPushButton#btn_salveaza_nou:hover {
            background-color: #b3daff;
        }
    """)

    try:
        header_layout = parent_widget.header_frame.layout()
        # Plasăm butonul la (2,4) sau unde ai tu liber
        header_layout.addWidget(parent_widget.btn_salveaza_nou, 2, 4, Qt.AlignRight | Qt.AlignBottom)
    except AttributeError:
        pass

    # 5) Când se dă click, apelăm finalize_insert
    parent_widget.btn_salveaza_nou.clicked.connect(
        lambda: finalize_insert(nr_fisa, parent_widget)
    )


def finalize_insert(nr_fisa, parent_widget):
    """
    - Face validările
    - Dacă totul e ok, INSERT în MEMBRII.db, apoi INSERT(URI) în DEPCRED.db
    - Afișează mesaj de succes / eroare
    """

    # 1) Colectăm datele din header
    nume = parent_widget.nume_input.text().strip()
    adresa = parent_widget.adresa_input.text().strip()
    calitate = parent_widget.calitate_input.text().strip()
    data_inscr = parent_widget.data_input.text().strip()

    # 2) Validări date personale
    #    -> folosim verificare_campuri, format_data
    if not verifica_campuri_completate(parent_widget, [parent_widget.nume_input,
                                                      parent_widget.adresa_input,
                                                      parent_widget.calitate_input,
                                                      parent_widget.data_input]):
        return  # show deja un mesaj -> oprim

    if not verifica_format_data(parent_widget, parent_widget.data_input):
        return

    # 3) Colectăm datele financiare
    # Observăm că e posibil userul să fi introdus mai multe linii, una sub alta.
    # => Trebuie să parcurgem line-by-line fiecare coloană și să formăm "rânduri".
    # Ca exemplu, luăm textul din fiecare coloană, facem split la newline, și
    # combinăm rând cu rând. Minim, e un singur rând.
    dobanda_lines = parent_widget.col_dobanda["text_edit"].toPlainText().splitlines()
    impr_deb_lines = parent_widget.col_impr_deb["text_edit"].toPlainText().splitlines()
    impr_cred_lines = parent_widget.col_impr_cred["text_edit"].toPlainText().splitlines()
    impr_sold_lines = parent_widget.col_impr_sold["text_edit"].toPlainText().splitlines()
    luna_an_lines = parent_widget.col_luna_an["text_edit"].toPlainText().splitlines()
    dep_deb_lines = parent_widget.col_dep_deb["text_edit"].toPlainText().splitlines()
    dep_cred_lines = parent_widget.col_dep_cred["text_edit"].toPlainText().splitlines()
    dep_sold_lines = parent_widget.col_dep_sold["text_edit"].toPlainText().splitlines()

    # Trebuie să avem același număr de linii în toate aceste coloane, altfel datele nu se potrivesc
    nr_linii = len(luna_an_lines)
    if not all(len(col) == nr_linii for col in [dobanda_lines, impr_deb_lines, impr_cred_lines,
                                                impr_sold_lines, dep_deb_lines, dep_cred_lines, dep_sold_lines]):
        show_stylized_message(parent_widget, "Eroare", "Numărul de linii din coloanele financiare nu coincide.")
        return

    # 4) Validăm fiecare rând
    for i in range(nr_linii):
        # extragem valorile
        val_dobanda = dobanda_lines[i].strip()
        val_impr_deb = impr_deb_lines[i].strip()
        val_impr_cred = impr_cred_lines[i].strip()
        val_impr_sold = impr_sold_lines[i].strip()
        val_luna_an = luna_an_lines[i].strip()
        val_dep_deb = dep_deb_lines[i].strip()
        val_dep_cred = dep_cred_lines[i].strip()
        val_dep_sold = dep_sold_lines[i].strip()

        # Verificăm completate
        # -> put them in dummy QLineEdit to reuse "verifica_campuri_completate" / "verifica_numere"
        #   Sau pur și simplu verificăm direct:
        if not val_luna_an:
            show_stylized_message(parent_widget, "Eroare", "Câmpul 'Luna-An' nu poate fi gol.")
            return

        from PyQt5.QtWidgets import QLineEdit
        e_dobanda = QLineEdit(val_dobanda)
        e_impr_deb = QLineEdit(val_impr_deb)
        e_impr_cred = QLineEdit(val_impr_cred)
        e_impr_sold = QLineEdit(val_impr_sold)
        e_dep_deb = QLineEdit(val_dep_deb)
        e_dep_cred = QLineEdit(val_dep_cred)
        e_dep_sold = QLineEdit(val_dep_sold)

        # Validare numerică
        if not verifica_numere(parent_widget, [e_dobanda, e_impr_deb, e_impr_cred, e_impr_sold, e_dep_deb,
                                               e_dep_cred, e_dep_sold]):
            return

        # Validare format LL-AAAA
        # facem la fel: e_luna_an = QLineEdit(val_luna_an)
        from PyQt5.QtWidgets import QLineEdit
        e_luna_an = QLineEdit(val_luna_an)
        if not verifica_format_luna_an(parent_widget, e_luna_an):
            return

    # Dacă am ajuns aici, datele sunt OK la suprafață.
    # 5) Facem INSERT efectiv
    try:
        conn = sqlite3.connect("MEMBRII.db")
        cursor = conn.cursor()
        # Inserăm noul membru
        cursor.execute("""
            INSERT INTO membrii (NR_FISA, NUM_PREN, DOMICILIUL, CALITATEA, DATA_INSCR)
            VALUES (?, ?, ?, ?, ?)
        """, (nr_fisa, nume, adresa, calitate, data_inscr))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        logging.error(f"Eroare la inserarea noului membru {nr_fisa}: {e}", exc_info=True)
        show_stylized_message(parent_widget, "Eroare", f"Eroare la inserarea noului membru:\n{str(e)}", icon="warning")
        return

    # Apoi inserăm datele financiare în DEPCRED.db
    # -> pentru fiecare rând
    try:
        conn_dep = sqlite3.connect("DEPCRED.db")
        c_dep = conn_dep.cursor()
        for i in range(nr_linii):
            val_dobanda = dobanda_lines[i].strip()
            val_impr_deb = impr_deb_lines[i].strip()
            val_impr_cred = impr_cred_lines[i].strip()
            val_impr_sold = impr_sold_lines[i].strip()
            val_luna_an = luna_an_lines[i].strip()
            val_dep_deb = dep_deb_lines[i].strip()
            val_dep_cred = dep_cred_lines[i].strip()
            val_dep_sold = dep_sold_lines[i].strip()

            # separăm LL-AAAA
            luna_str, anul_str = val_luna_an.split("-")  # "03-2025" => "03", "2025"
            luna = int(luna_str)
            anul = int(anul_str)

            # Insert
            c_dep.execute("""
                INSERT INTO depcred (
                    NR_FISA, DOBANDA, IMPR_DEB, IMPR_CRED, IMPR_SOLD,
                    LUNA, ANUL, DEP_DEB, DEP_CRED, DEP_SOLD
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (nr_fisa,
                  float(val_dobanda or 0),
                  float(val_impr_deb or 0),
                  float(val_impr_cred or 0),
                  float(val_impr_sold or 0),
                  luna, anul,
                  float(val_dep_deb or 0),
                  float(val_dep_cred or 0),
                  float(val_dep_sold or 0)))
        conn_dep.commit()
        conn_dep.close()

        # 6) Mesaj final de succes
        show_stylized_message(
            parent_widget,
            "Succes",
            f"Membrul nr_fisa={nr_fisa} a fost adăugat cu succes, inclusiv datele financiare!"
        )

        # După mesaj, scoatem butonul "Salvează membru nou"
        layout = parent_widget.header_frame.layout()
        if hasattr(parent_widget, "btn_salveaza_nou"):
            layout.removeWidget(parent_widget.btn_salveaza_nou)
            parent_widget.btn_salveaza_nou.deleteLater()
            del parent_widget.btn_salveaza_nou

    except sqlite3.Error as e:
        logging.error(f"Eroare la inserarea datelor financiare pentru {nr_fisa}: {e}", exc_info=True)
        show_stylized_message(
            parent_widget,
            "Eroare",
            f"A apărut o eroare la inserarea datelor financiare:\n{str(e)}",
            icon="warning"
        )


def show_stylized_message(parent, title, text, icon="info"):
    """
    MsgBox simplu, stilizat.
    """
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(text)
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
