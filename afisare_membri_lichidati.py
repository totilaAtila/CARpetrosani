import sys
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QMessageBox, QAbstractItemView, QApplication, QHeaderView, QProgressDialog
)
from PyQt5.QtCore import Qt
import sqlite3
from datetime import datetime


class MembriLichidatiWidget(QWidget):
    """Widget pentru afișarea membrilor cu date incomplete (lipsesc din luna anterioară ultimei luni procesate)."""

    def __init__(self):
        super().__init__()
        # Stocare date initiale
        self.all_missing_members_data = []
        self.ultima_luna = 0
        self.ultimul_an = 0
        self.init_ui()
        self.incarca_date()  # Incarca si afiseaza datele initiale

    def init_ui(self):
        self.setWindowTitle("Membri cu Date Incomplete")
        self.setGeometry(100, 100, 850, 550)  # Dimensiune initiala ajustata
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f8ff; /* AliceBlue */
                font-family: Segoe UI, Arial, sans-serif;
            }
            QLabel#titleLabel {
                font-size: 18px;
                font-weight: bold;
                color: #005a9e; /* Dark blue */
                padding: 10px;
                border-bottom: 1px solid #d0d0d0;
                text-align: center; /* Aliniere text titlu */
            }
            QLabel#infoLabel {
                font-size: 10pt;
                color: #555; /* Gri inchis */
                padding: 5px 10px;
                font-style: italic;
                text-align: center; /* Aliniere text info */
            }
            QTableWidget {
                border: 1px solid #d0d0d0;
                gridline-color: #e0e0e0;
                alternate-background-color: #e7f2ff; /* Light blue alternating */
                selection-background-color: #a6d8ff; /* Blue selection */
                selection-color: black;
                font-size: 11pt; /* Marime font tabel */
            }
            QHeaderView::section {
                background-color: #0078d4; /* Standard blue */
                color: white;
                padding: 6px;
                font-weight: bold;
                border: 1px solid #005a9e;
            }
            QPushButton#deleteButton {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                               stop: 0 #ffaa00, stop: 1 #ff8c00); /* Orange gradient */
                border: 1px solid #e67e22; /* Darker orange border */
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11pt;
                min-width: 200px; /* Latime minima buton */
            }
            QPushButton#deleteButton:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                               stop: 0 #ffc14d, stop: 1 #ffa500); /* Lighter orange gradient on hover */
                border: 1px solid #d35400;
            }
            QPushButton#deleteButton:pressed {
                background-color: #d35400; /* Dark orange when pressed */
                border: 1px solid #a04000;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)  # Spatiu intre widgeturi
        main_layout.setContentsMargins(15, 15, 15, 15)  # Margini fereastra

        # --- Titlu ---
        label_titlu = QLabel("Membri cu Date Incomplete (lipsesc din luna sursă pentru generarea următoarei luni)")
        label_titlu.setObjectName("titleLabel")  # Pentru CSS specific
        label_titlu.setAlignment(Qt.AlignCenter)
        label_titlu.setWordWrap(True)  # Permite trecerea pe rand nou daca textul e prea lung
        main_layout.addWidget(label_titlu)

        # --- Eticheta Informativa Sortare ---
        label_info_sortare = QLabel("ℹ️ Apăsați pe antetul unei coloane pentru a sorta tabelul.")
        label_info_sortare.setObjectName("infoLabel")
        label_info_sortare.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(label_info_sortare)

        # --- Tabel Membri ---
        self.tabel = QTableWidget()
        self.tabel.setColumnCount(6)
        # Numele coloanelor modificate conform noii cerințe
        self.tabel.setHorizontalHeaderLabels([
            "Nr. fișă", "Nume", "Ultima Lună Disponibilă",
            "Sold Împrumut", "Sold Depunere", "Ultima lună cu date"
        ])
        self.tabel.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabel.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabel.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tabel.setAlternatingRowColors(True)
        self.tabel.verticalHeader().setVisible(False)
        self.tabel.setSortingEnabled(True)
        # Ajustare latime coloane
        header = self.tabel.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Nume
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Nr. fișă
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Ultima Lună Disponibilă
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Sold Împrumut
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Sold Depunere
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Ultima lună cu date

        # Setam sortarea initiala implicita (dupa data ultimei luni, Descrescator)
        self.tabel.sortByColumn(5, Qt.DescendingOrder)

        main_layout.addWidget(self.tabel, 1)

        # --- Buton Stergere ---
        buton_sterge = QPushButton("Șterge Definitiv Membrii Selectați")
        buton_sterge.setObjectName("deleteButton")
        buton_sterge.setCursor(Qt.PointingHandCursor)
        buton_sterge.clicked.connect(self.sterge_selectati)

        # Aliniere buton la centru jos
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(buton_sterge)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def identifica_membri_lipsa(self):
        """
        Identifică membrii care ar genera un mesaj "lipsă date sursă" în procesul de generare lună.
        Aceștia sunt membri care există în MEMBRII.db dar nu au date în luna anterioară
        celei mai recente luni procesate din DEPCRED.db.
        """
        membri_lipsa = []

        # Inițializăm dialogul de progres
        progress_dialog = QProgressDialog("Se identifică membrii cu date incomplete...", "Anulează", 0, 100, self)
        progress_dialog.setWindowTitle("Progres")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setMinimumDuration(500)  # Apare după 500ms
        progress_dialog.setValue(0)
        progress_dialog.show()

        try:
            # 1. Determinăm ultima lună procesată din DEPCRED.db
            progress_dialog.setValue(10)
            QApplication.processEvents()

            conn_dep = sqlite3.connect("DEPCRED.db")
            cursor_dep = conn_dep.cursor()

            cursor_dep.execute("""
                SELECT anul, luna FROM depcred
                ORDER BY anul DESC, luna DESC
                LIMIT 1
            """)

            result = cursor_dep.fetchone()
            if not result:
                QMessageBox.warning(self, "Nicio Lună Procesată",
                                    "Nu s-au găsit luni procesate în DEPCRED.db.")
                conn_dep.close()
                progress_dialog.close()
                return []

            self.ultimul_an, self.ultima_luna = result

            # 2. Calculăm luna anterioară (luna sursă pentru generarea unei luni noi)
            luna_sursa = self.ultima_luna - 1 if self.ultima_luna > 1 else 12
            an_sursa = self.ultimul_an if self.ultima_luna > 1 else self.ultimul_an - 1

            progress_dialog.setValue(20)
            QApplication.processEvents()

            # 3. Preluăm toți membrii din MEMBRII.db
            conn_membri = sqlite3.connect("MEMBRII.db")
            cursor_m = conn_membri.cursor()

            cursor_m.execute("SELECT nr_fisa, num_pren FROM membrii WHERE nr_fisa IS NOT NULL")
            toti_membrii = cursor_m.fetchall()

            if not toti_membrii:
                QMessageBox.warning(self, "Niciun Membru",
                                    "Nu s-au găsit membri în MEMBRII.db.")
                conn_dep.close()
                conn_membri.close()
                progress_dialog.close()
                return []

            progress_dialog.setValue(30)
            QApplication.processEvents()

            # 4. Pentru fiecare membru, verificăm dacă are date în luna sursă
            total_membri = len(toti_membrii)
            for i, (nr_fisa, nume) in enumerate(toti_membrii):
                # Actualizăm bara de progres
                progress_value = 30 + int((i / total_membri) * 60)
                progress_dialog.setValue(progress_value)
                progress_dialog.setLabelText(f"Se verifică membrul {i + 1}/{total_membri}...")
                QApplication.processEvents()

                if progress_dialog.wasCanceled():
                    conn_dep.close()
                    conn_membri.close()
                    return []

                # Verificăm dacă membrul există în luna sursă
                cursor_dep.execute("""
                    SELECT 1 FROM depcred 
                    WHERE nr_fisa = ? AND anul = ? AND luna = ?
                """, (nr_fisa, an_sursa, luna_sursa))

                if not cursor_dep.fetchone():
                    # Membrul lipsește din luna sursă - ar genera "lipsă date sursă"
                    # Găsim ultima lună în care membrul are date
                    cursor_dep.execute("""
                        SELECT anul, luna, impr_sold, dep_sold 
                        FROM depcred 
                        WHERE nr_fisa = ? 
                        ORDER BY anul DESC, luna DESC
                        LIMIT 1
                    """, (nr_fisa,))

                    ultima_data = cursor_dep.fetchone()

                    if ultima_data:
                        an_ultima, luna_ultima, impr_sold, dep_sold = ultima_data
                        ultima_luna_formatata = f"{luna_ultima:02d}-{an_ultima}"

                        # Preluăm soldurile
                        impr_sold = float(impr_sold) if impr_sold is not None else 0.0
                        dep_sold = float(dep_sold) if dep_sold is not None else 0.0
                    else:
                        # Membrul nu are date deloc în DEPCRED.db
                        ultima_luna_formatata = "Niciodată"
                        impr_sold = 0.0
                        dep_sold = 0.0

                    # Adăugăm membrul la lista celor care lipsesc
                    membri_lipsa.append({
                        'nr_fisa': nr_fisa,
                        'nume': nume,
                        'ultima_luna_disponibila': f"{self.ultima_luna:02d}-{self.ultimul_an}",
                        'luna_sursa': f"{luna_sursa:02d}-{an_sursa}",
                        'impr_sold': impr_sold,
                        'dep_sold': dep_sold,
                        'ultima_luna_cu_date': ultima_luna_formatata
                    })

            progress_dialog.setValue(95)
            QApplication.processEvents()

            conn_dep.close()
            conn_membri.close()

            progress_dialog.setValue(100)
            progress_dialog.close()

            return membri_lipsa

        except sqlite3.Error as e:
            progress_dialog.close()
            QMessageBox.critical(self, "Eroare Baza de Date", f"Eroare la interogarea bazelor de date:\n{e}")
            return []
        except Exception as e:
            progress_dialog.close()
            QMessageBox.critical(self, "Eroare Generală", f"A apărut o eroare neașteptată:\n{e}")
            return []

    def incarca_date(self):
        """Identifică membrii cu date incomplete și îi afișează în tabel."""
        self.all_missing_members_data = self.identifica_membri_lipsa()
        self.populeaza_tabel(self.all_missing_members_data)

    def populeaza_tabel(self, date_membri):
        """Populeaza tabelul QTableWidget cu datele furnizate."""
        self.tabel.setSortingEnabled(False)
        self.tabel.setRowCount(0)

        for i, membru in enumerate(date_membri):
            self.tabel.insertRow(i)

            # Nr. Fisa
            item_nr_fisa = QTableWidgetItem()
            item_nr_fisa.setData(Qt.DisplayRole, membru['nr_fisa'])
            item_nr_fisa.setData(Qt.UserRole, membru['nr_fisa'])
            item_nr_fisa.setTextAlignment(Qt.AlignCenter)
            item_nr_fisa.setFlags(item_nr_fisa.flags() ^ Qt.ItemIsEditable)

            # Nume
            item_nume = QTableWidgetItem(membru['nume'])
            item_nume.setFlags(item_nume.flags() ^ Qt.ItemIsEditable)

            # Ultima Luna Disponibila (include acum info despre luna sursă)
            item_ultima_disp = QTableWidgetItem(f"{membru['ultima_luna_disponibila']} (sursa: {membru['luna_sursa']})")
            item_ultima_disp.setTextAlignment(Qt.AlignCenter)
            item_ultima_disp.setFlags(item_ultima_disp.flags() ^ Qt.ItemIsEditable)

            # Sold Împrumut
            item_impr_sold = QTableWidgetItem(f"{membru['impr_sold']:.2f}")
            item_impr_sold.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_impr_sold.setFlags(item_impr_sold.flags() ^ Qt.ItemIsEditable)

            # Sold Depunere
            item_dep_sold = QTableWidgetItem(f"{membru['dep_sold']:.2f}")
            item_dep_sold.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_dep_sold.setFlags(item_dep_sold.flags() ^ Qt.ItemIsEditable)

            # Ultima Luna cu Date
            item_ultima = QTableWidgetItem(membru['ultima_luna_cu_date'])
            item_ultima.setTextAlignment(Qt.AlignCenter)
            item_ultima.setFlags(item_ultima.flags() ^ Qt.ItemIsEditable)

            self.tabel.setItem(i, 0, item_nr_fisa)
            self.tabel.setItem(i, 1, item_nume)
            self.tabel.setItem(i, 2, item_ultima_disp)
            self.tabel.setItem(i, 3, item_impr_sold)
            self.tabel.setItem(i, 4, item_dep_sold)
            self.tabel.setItem(i, 5, item_ultima)

        self.tabel.setSortingEnabled(True)
        # Sortăm inițial descrescător după ultima lună cu date
        self.tabel.sortByColumn(5, Qt.DescendingOrder)

    def sterge_selectati(self):
        """Sterge membrii selectati din tabel din toate bazele de date relevante."""
        randuri_selectate = self.tabel.selectionModel().selectedRows()

        if not randuri_selectate:
            QMessageBox.information(self, "Nicio Selecție",
                                    "Vă rugăm să selectați cel puțin un membru din tabel pentru a-l șterge.")
            return

        nr_fise_de_sters = []
        nume_membri_stersi = []
        for index in randuri_selectate:
            item_nr_fisa = self.tabel.item(index.row(), 0)
            item_nume = self.tabel.item(index.row(), 1)
            if item_nr_fisa:
                nr_fisa = item_nr_fisa.data(Qt.UserRole)
                if nr_fisa is not None:
                    nr_fise_de_sters.append(str(nr_fisa))
                    nume_membri_stersi.append(item_nume.text() if item_nume else "Necunoscut")
                else:
                    print(f"Warning: Could not retrieve nr_fisa from UserRole for row {index.row()}")
            else:
                print(f"Warning: Could not retrieve item for nr_fisa at row {index.row()}")

        if not nr_fise_de_sters:
            QMessageBox.warning(self, "Eroare Selecție",
                                "Nu s-a putut identifica Nr. Fișă pentru rândurile selectate. Încercați din nou.")
            return

        # Simplificăm dialogul de confirmare eliminând lista de nume
        mesaj = f"Sunteți absolut sigur că doriți să ștergeți definitiv {len(nr_fise_de_sters)} membri selectați?\n\n"
        mesaj += "Această acțiune este ireversibilă!"

        confirm = QMessageBox.warning(
            self,
            "Confirmare Ștergere Permanentă",
            mesaj,
            QMessageBox.Yes | QMessageBox.Cancel,
            QMessageBox.Cancel
        )

        if confirm == QMessageBox.Cancel:
            return

        # Afișăm un dialog de progres pentru ștergere
        progress_dialog = QProgressDialog("Se șterg membrii selectați...", "Anulează", 0, len(nr_fise_de_sters), self)
        progress_dialog.setWindowTitle("Progres Ștergere")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setMinimumDuration(500)
        progress_dialog.setValue(0)
        progress_dialog.show()

        erori_stergere = []
        succes_count = 0
        try:
            # Stergem din MEMBRII.db si DEPCRED.db
            baze_de_sters = [("MEMBRII.db", "membrii"), ("DEPCRED.db", "depcred")]

            for i, nr_fisa in enumerate(nr_fise_de_sters):
                if progress_dialog.wasCanceled():
                    break

                progress_dialog.setValue(i)
                progress_dialog.setLabelText(f"Se șterge membrul {i + 1}/{len(nr_fise_de_sters)}...")
                QApplication.processEvents()

                nr_fisa_int = int(nr_fisa)  # Convertim la int pentru query
                try:
                    for baza, tabel_db in baze_de_sters:
                        conn = sqlite3.connect(baza)
                        cursor = conn.cursor()
                        cursor.execute(f"DELETE FROM {tabel_db} WHERE nr_fisa = ?", (nr_fisa_int,))
                        conn.commit()
                        conn.close()
                    succes_count += 1
                except sqlite3.Error as e:
                    erori_stergere.append(f"Eroare DB la ștergerea fișei {nr_fisa}: {e}")
                except Exception as e_gen:
                    erori_stergere.append(f"Eroare generală la ștergerea fișei {nr_fisa}: {e_gen}")

            progress_dialog.setValue(len(nr_fise_de_sters))
            progress_dialog.close()

            if not erori_stergere:
                QMessageBox.information(self, "Succes", f"{succes_count} membri au fost șterși definitiv.")
            else:
                QMessageBox.warning(self, "Operație Finalizată cu Erori",
                                    f"{succes_count} membri șterși cu succes.\n\n"
                                    f"Au apărut {len(erori_stergere)} erori:\n" + "\n".join(erori_stergere))

            self.incarca_date()

        except Exception as e:
            progress_dialog.close()
            QMessageBox.critical(self, "Eroare Critică la Ștergere",
                                 f"A apărut o eroare majoră în timpul procesului de ștergere:\n{e}")
            self.incarca_date()


# --- Bloc pentru rulare directa ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MembriLichidatiWidget()
    widget.show()
    sys.exit(app.exec_())