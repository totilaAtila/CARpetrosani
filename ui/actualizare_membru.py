from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QFrame
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import sqlite3
from datetime import datetime


class ActualizareMembruWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Cadru pentru datele generale
        self.general_frame = QFrame()
        self.general_frame.setStyleSheet("border: 1px solid black; padding: 10px;")
        general_layout = QFormLayout(self.general_frame)

        self.nr_fisa = QLineEdit()
        self.nr_fisa.setPlaceholderText("Număr Fișă")
        self.nr_fisa.textChanged.connect(self.verifica_numar_fisa)

        self.nume_prenume = QLineEdit()
        self.nume_prenume.setPlaceholderText("Nume Prenume")

        self.adresa = QLineEdit()
        self.adresa.setPlaceholderText("Adresă")

        self.calitatea = QLineEdit()
        self.calitatea.setPlaceholderText("Calitate")

        self.data_inscrierii = QLineEdit()
        self.data_inscrierii.setText(datetime.now().strftime("%d-%m-%Y"))
        self.data_inscrierii.setReadOnly(True)

        general_layout.addRow("Număr Fișă:", self.nr_fisa)
        general_layout.addRow("Nume Prenume:", self.nume_prenume)
        general_layout.addRow("Adresă:", self.adresa)
        general_layout.addRow("În calitate de:", self.calitatea)
        general_layout.addRow("Data înscrierii:", self.data_inscrierii)

        layout.addWidget(self.general_frame)

        # Cadru pentru situația împrumuturilor
        self.imprumuturi_frame = QFrame()
        self.imprumuturi_frame.setStyleSheet("border: 1px solid black; padding: 10px;")
        imprumuturi_layout = QFormLayout(self.imprumuturi_frame)

        self.impr_dobanda = QLineEdit()
        self.impr_dobanda.setPlaceholderText("Dobândă")

        self.impr_debit = QLineEdit()
        self.impr_debit.setPlaceholderText("Debit")

        self.impr_credit = QLineEdit()
        self.impr_credit.setPlaceholderText("Credit")

        self.impr_sold = QLineEdit()
        self.impr_sold.setPlaceholderText("Sold")

        imprumuturi_layout.addRow("Dobândă:", self.impr_dobanda)
        imprumuturi_layout.addRow("Debit:", self.impr_debit)
        imprumuturi_layout.addRow("Credit:", self.impr_credit)
        imprumuturi_layout.addRow("Sold:", self.impr_sold)

        layout.addWidget(self.imprumuturi_frame)

        # Cadru pentru situația depunerilor
        self.depuneri_frame = QFrame()
        self.depuneri_frame.setStyleSheet("border: 1px solid black; padding: 10px;")
        depuneri_layout = QFormLayout(self.depuneri_frame)

        self.data_luna_an = QLineEdit()
        self.data_luna_an.setText(datetime.now().strftime("%m-%Y"))
        self.data_luna_an.setReadOnly(True)

        self.dep_credit = QLineEdit()
        self.dep_credit.setPlaceholderText("Credit")

        self.dep_debit = QLineEdit()
        self.dep_debit.setPlaceholderText("Debit")

        self.dep_sold = QLineEdit()
        self.dep_sold.setPlaceholderText("Sold")

        depuneri_layout.addRow("Data (Luna-An):", self.data_luna_an)
        depuneri_layout.addRow("Credit:", self.dep_credit)
        depuneri_layout.addRow("Debit:", self.dep_debit)
        depuneri_layout.addRow("Sold:", self.dep_sold)

        layout.addWidget(self.depuneri_frame)

        # Butoane
        btn_layout = QHBoxLayout()
        self.adauga_btn = QPushButton("Adaugă Membru")
        self.adauga_btn.clicked.connect(self.adauga_membru)

        self.modifica_btn = QPushButton("Modifică Date")
        self.modifica_btn.clicked.connect(self.modifica_membru)

        btn_layout.addWidget(self.adauga_btn)
        btn_layout.addWidget(self.modifica_btn)

        layout.addLayout(btn_layout)

    def verifica_numar_fisa(self):
        """Verifică dacă numărul de fișă există deja în baza de date și preia datele asociate."""
        nr_fisa = self.nr_fisa.text()
        conn = sqlite3.connect("membrii.db", timeout=30.0)
        cursor = conn.cursor()
        cursor.execute("SELECT num_pren, domiciliul, calitatea, data_inscr FROM membrii WHERE nr_fisa=?", (nr_fisa,))
        row = cursor.fetchone()
        conn.close()

        if row:
            self.nume_prenume.setText(row[0])
            self.adresa.setText(row[1])
            self.calitatea.setText(row[2])
            self.data_inscrierii.setText(row[3])
            self.nume_prenume.setEnabled(False)
            self.adresa.setEnabled(False)
            self.calitatea.setEnabled(False)
        else:
            self.nume_prenume.setEnabled(True)
            self.adresa.setEnabled(True)
            self.calitatea.setEnabled(True)

    def adauga_membru(self):
        """Adaugă un membru nou în baza de date."""
        conn = sqlite3.connect("membrii.db", timeout=30.0)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO membrii (nr_fisa, num_pren, domiciliul, calitatea, data_inscr) 
                VALUES (?, ?, ?, ?, ?)""",
                           (self.nr_fisa.text(), self.nume_prenume.text(), self.adresa.text(), self.calitatea.text(),
                            self.data_inscrierii.text())
                           )
            conn.commit()
        finally:
            conn.close()

    def modifica_membru(self):
        """Modifică datele unui membru existent."""
        conn = sqlite3.connect("membrii.db", timeout=30.0)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE membrii SET num_pren=?, domiciliul=?, calitatea=?, data_inscr=?
                WHERE nr_fisa=?""",
                           (self.nume_prenume.text(), self.adresa.text(), self.calitatea.text(),
                            self.data_inscrierii.text(), self.nr_fisa.text())
                           )
            conn.commit()
        finally:
            conn.close()
