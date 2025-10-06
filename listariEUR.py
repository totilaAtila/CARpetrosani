import os
import sqlite3
import subprocess
import platform
from datetime import date
import sys
import tempfile
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFileDialog, QFrame, QProgressBar,
    QSpinBox, QComboBox, QGroupBox, QGridLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QTextEdit, QTableView
)
from PyQt5.QtGui import QFont, QIntValidator, QPixmap, QIcon, QPainter, QColor, QPen, QBrush, QRadialGradient, \
    QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, QRect, QThread, pyqtSignal, QTime, QDate
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
# După liniile cu from PyQt5.QtCore import ...
from utils import afiseaza_warning, afiseaza_eroare, afiseaza_info, afiseaza_intrebare
from dialog_styles import get_dialog_stylesheet


class TimerBasedPDFGenerator:
    """Generarea PDF bazată pe QTimer - NU folosește thread-uri deloc!"""

    def __init__(self, parent_widget, database_dir, luna, an, nr_chitanta_init, chitante_per_pagina):
        self.parent = parent_widget
        self.database_dir = database_dir
        self.luna = luna
        self.an = an
        self.nr_chitanta_init = nr_chitanta_init
        self.chitante_per_pagina = chitante_per_pagina

        # State tracking
        self.chitante_data = []
        self.current_index = 0
        self.pdf_file = ""
        self.pdf_canvas = None
        self.chit_cit = nr_chitanta_init - 1
        self.cancelled = False

        # Timer pentru procesare pas cu pas
        self.process_timer = QTimer()
        self.process_timer.timeout.connect(self._process_next_batch)
        self.process_timer.setSingleShot(True)

        # State machine
        self.current_state = "init"  # init -> fonts -> data -> generate -> totals -> save -> done

    def start_generation(self):
        """Pornește generarea PDF pas cu pas"""
        self.cancelled = False
        self.current_state = "init"
        self._log("🚀 Pornește generarea PDF...")
        self._update_progress(5, "Inițializare...")

        # Primul pas - după 10ms pentru a lăsa UI să se actualizeze
        QTimer.singleShot(10, self._process_next_batch)

    def cancel_generation(self):
        """Anulează generarea"""
        self.cancelled = True
        self.process_timer.stop()
        if self.pdf_canvas:
            try:
                self.pdf_canvas.save()
                del self.pdf_canvas
            except:
                pass
        self._log("🛑 Generare anulată")

    def _process_next_batch(self):
        """Procesează următorul pas din generarea PDF"""
        if self.cancelled:
            return

        try:
            if self.current_state == "init":
                self._step_register_fonts()
            elif self.current_state == "fonts":
                self._step_fetch_data()
            elif self.current_state == "data":
                self._step_init_pdf()
            elif self.current_state == "generate":
                self._step_generate_chitante()
            elif self.current_state == "totals":
                self._step_add_totals()
            elif self.current_state == "save":
                self._step_save_and_finish()

        except Exception as e:
            self._handle_error(f"Eroare la {self.current_state}: {str(e)}")

    def _step_register_fonts(self):
        """Pas 1: Înregistrează fonturile"""
        self._update_progress(10, "Înregistrare fonturi...")

        try:
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            fonts_dir = os.path.join(base_path, "fonts")

            # Înregistrare simplă de fonturi
            font_paths = {
                'Arial': [
                    os.path.join(fonts_dir, "Arial.ttf"),
                    os.path.join(base_path, "Arial.ttf"),
                    "C:/Windows/Fonts/Arial.ttf"
                ],
                'DejaVuBoldSans': [
                    os.path.join(fonts_dir, "DejaVuSans-Bold.ttf"),
                    os.path.join(base_path, "DejaVuSans-Bold.ttf"),
                    "C:/Windows/Fonts/DejaVuSans-Bold.ttf"
                ]
            }

            for font_name, paths in font_paths.items():
                registered = False
                for path in paths:
                    if os.path.exists(path):
                        try:
                            pdfmetrics.registerFont(TTFont(font_name, path))
                            registered = True
                            break
                        except:
                            continue

                if not registered:
                    if font_name == 'Arial':
                        pdfmetrics.registerFont(TTFont('Arial', 'Helvetica'))
                    else:
                        pdfmetrics.registerFont(TTFont('DejaVuBoldSans', 'Helvetica-Bold'))

            self.current_state = "fonts"
            self.process_timer.start(20)  # Continuă după 20ms

        except Exception as e:
            self._handle_error(f"Eroare înregistrare fonturi: {e}")

    def _step_fetch_data(self):
        """Pas 2: Preia datele din DB"""
        self._update_progress(20, "Preluare date din baza de date...")

        try:
            depcred_path = os.path.join(self.database_dir, "DEPCREDEUR.db")
            membrii_path = os.path.join(self.database_dir, "MEMBRIIEUR.db")

            with sqlite3.connect(depcred_path) as conn1, sqlite3.connect(membrii_path) as conn2:
                cursor1 = conn1.cursor()
                cursor2 = conn2.cursor()

                cursor1.execute(
                    'SELECT LUNA, ANUL, DOBANDA, IMPR_CRED, IMPR_SOLD, DEP_DEB, DEP_CRED, DEP_SOLD, NR_FISA '
                    'FROM DEPCRED WHERE LUNA=? AND ANUL=?',
                    (self.luna, self.an)
                )
                depcred_rows = cursor1.fetchall()

                if not depcred_rows:
                    self._handle_error("Nu există chitanțe pentru această lună și an.")
                    return

                for row in depcred_rows:
                    nr_fisa = row[8]
                    cursor2.execute('SELECT NUM_PREN FROM MEMBRII WHERE NR_FISA = ?', (nr_fisa,))
                    nume = cursor2.fetchone()
                    if nume:
                        self.chitante_data.append((*row, nume[0]))

                # Sortează după nume
                self.chitante_data.sort(key=lambda x: x[9])

            self._log(f"📊 Găsite {len(self.chitante_data)} chitanțe")
            self.current_state = "data"
            self.process_timer.start(30)

        except Exception as e:
            self._handle_error(f"Eroare preluare date: {e}")

    def _step_init_pdf(self):
        """Pas 3: Inițializează PDF-ul"""
        self._update_progress(30, "Inițializare PDF...")

        try:
            self.pdf_file = os.path.join(self.database_dir, f"chitante_{self.luna}_{self.an}.pdf")

            # Verifică dacă fișierul există și îl șterge
            if os.path.exists(self.pdf_file):
                try:
                    os.remove(self.pdf_file)
                except OSError:
                    timestamp = date.today().strftime('%Y%m%d_%H%M%S')
                    self.pdf_file = os.path.join(self.database_dir, f"chitante_{self.luna}_{self.an}_{timestamp}.pdf")

            self.pdf_canvas = canvas.Canvas(self.pdf_file, pagesize=A4)
            self.current_index = 0

            self.current_state = "generate"
            self.process_timer.start(50)

        except Exception as e:
            self._handle_error(f"Eroare inițializare PDF: {e}")

    def _step_generate_chitante(self):
        """Pas 4: Generează chitanțele - câte 5 pe batch pentru a nu îngheta UI"""
        if self.current_index >= len(self.chitante_data):
            self.current_state = "totals"
            self.process_timer.start(50)
            return

        try:
            # Procesează până la 5 chitanțe pe batch
            batch_size = min(5, len(self.chitante_data) - self.current_index)
            page_height = A4[1]

            for i in range(batch_size):
                if self.cancelled:
                    return

                data_row = self.chitante_data[self.current_index + i]
                self.chit_cit += 1

                y_position = page_height - 25 - ((self.current_index + i) % self.chitante_per_pagina * 79)
                self._draw_chitanta(y_position, self.chit_cit, data_row)

                if (self.current_index + i + 1) % self.chitante_per_pagina == 0:
                    self.pdf_canvas.showPage()

            self.current_index += batch_size

            # Actualizează progresul
            progress = 30 + int((self.current_index / len(self.chitante_data)) * 50)
            self._update_progress(progress, f"Procesare chitanță {self.current_index}/{len(self.chitante_data)}...")

            # Continuă cu următorul batch după 20ms
            self.process_timer.start(20)

        except Exception as e:
            self._handle_error(f"Eroare generare chitanțe: {e}")

    def _step_add_totals(self):
        """Pas 5: Adaugă pagina de totaluri"""
        self._update_progress(85, "Adăugare pagina de totaluri...")

        try:
            self.pdf_canvas.showPage()
            self._draw_totals_page()

            self.current_state = "save"
            self.process_timer.start(30)

        except Exception as e:
            self._handle_error(f"Eroare pagina totaluri: {e}")

    def _step_save_and_finish(self):
        """Pas 6: Salvează și finalizează"""
        self._update_progress(95, "Salvare fișier PDF...")

        try:
            self.pdf_canvas.save()
            del self.pdf_canvas
            self.pdf_canvas = None

            # Actualizează baza de date CHITANTE
            self._update_chitante_db()

            self._update_progress(100, "Finalizat!")

            # Verifică că fișierul a fost creat
            if os.path.exists(self.pdf_file) and os.path.getsize(self.pdf_file) > 0:
                QTimer.singleShot(100, lambda: self.parent._on_pdf_generation_success(
                    f"PDF generat cu succes: {len(self.chitante_data)} chitanțe", self.pdf_file))
            else:
                self._handle_error("Fișierul PDF nu a fost creat corect")

        except Exception as e:
            self._handle_error(f"Eroare salvare PDF: {e}")

    def _draw_chitanta(self, y_position, chit_cit, data_row):
        """Desenează o chitanță individuală - MUTAT cu 0,5cm dreapta, înălțime 2,5cm"""
        cpdf = self.pdf_canvas

        # Offset pentru mutarea cu 0,5 cm spre dreapta (0,5 cm = ~14 puncte)
        x_offset = 14

        # Noua înălțime: 2,5 cm = ~71 puncte (față de 52 puncte original)
        # Factor de scalare pentru poziții y: 71/52 ≈ 1.365
        new_height = 71

        # Chenarul exterior - MUTAT
        chenar_x1, chenar_x2 = 49 + x_offset, 550 + x_offset  # 63, 564
        chenar_y1, chenar_y2 = y_position - new_height, y_position  # y_position - 71, y_position

        cpdf.setLineWidth(2)
        cpdf.rect(chenar_x1, chenar_y1, chenar_x2 - chenar_x1, chenar_y2 - chenar_y1)

        # Liniile interioare - MUTATE și AJUSTATE la noua înălțime
        cpdf.setLineWidth(1)
        for x_line in [152 + x_offset, 230 + x_offset, 380 + x_offset, 460 + x_offset]:  # 166, 244, 394, 474
            cpdf.line(x_line, y_position - 22, x_line, y_position - 36)  # Ajustat de la -16,-26 la -22,-36
            cpdf.line(x_line, y_position - 57, x_line, y_position - 71)  # Ajustat de la -42,-52 la -57,-71

        # Liniile verticale principale - MUTATE
        cpdf.setLineWidth(2)
        cpdf.line(95 + x_offset, chenar_y1, 95 + x_offset, chenar_y2)  # 109
        cpdf.line(300 + x_offset, chenar_y1, 300 + x_offset, chenar_y2)  # 314

        # Linia orizontală din mijloc - MUTATĂ
        chenar_y = (chenar_y1 + chenar_y2) / 2
        cpdf.setLineWidth(2)
        cpdf.line(50 + x_offset, chenar_y, 550 + x_offset, chenar_y)  # 64, 564

        # Text static - MUTAT și AJUSTAT vertical
        cpdf.setFont('DejaVuBoldSans', 10)
        cpdf.drawString(51 + x_offset, y_position - 16, "Chit.")  # 65, ajustat de la -12 la -16
        cpdf.drawString(130 + x_offset, y_position - 16, "N u m e   ș i   p r e n u m e")  # 144

        cpdf.setFont('Arial', 10)
        cpdf.drawString(340 + x_offset, y_position - 16, "Semnătură casier")  # 354
        cpdf.drawString(51 + x_offset, y_position - 30, "LL-AAAA")  # 65, ajustat de la -22 la -30
        cpdf.drawString(108 + x_offset, y_position - 30, "Dobânda")  # 122
        cpdf.drawString(160 + x_offset, y_position - 30, "Rată împrumut")  # 177
        cpdf.drawString(231 + x_offset, y_position - 30, "Sold împrumut")  # 258
        cpdf.drawString(320 + x_offset, y_position - 30, "Depun. lun.")  # 334
        cpdf.drawString(395 + x_offset, y_position - 30, "Retragere FS")  # 409
        cpdf.drawString(477 + x_offset, y_position - 30, "Sold depuneri")  # 494

        # Date specifice chitanței - MUTATE și AJUSTATE vertical
        cpdf.setFont('DejaVuBoldSans', 10)
        cpdf.drawString(51 + x_offset, y_position - 52, str(chit_cit))  # 65, ajustat de la -38 la -52
        cpdf.drawString(130 + x_offset, y_position - 52, f"{data_row[9]}")  # 144
        cpdf.drawString(340 + x_offset, y_position - 52, "Total de plată =")  # 354

        # Suma totală de plată - MUTATĂ și AJUSTATĂ vertical
        suma_rate_depunere = data_row[2] + data_row[3] + data_row[5]
        cpdf.drawString(434 + x_offset, y_position - 52, f"{suma_rate_depunere:.2f} €")  # 434

        # Restul datelor - MUTATE și AJUSTATE vertical
        cpdf.setFont('Arial', 10)
        cpdf.drawString(51 + x_offset, y_position - 67,
                        f"{data_row[0]:02d} - {data_row[1]}")  # 65, ajustat de la -49 la -67
        cpdf.drawString(120 + x_offset, y_position - 67, f"{data_row[2]:.2f}")  # 134
        cpdf.drawString(180 + x_offset, y_position - 67, f"{data_row[3]:.2f}")  # 194
        cpdf.drawString(250 + x_offset, y_position - 67, f"{data_row[4]:.2f}")  # 264
        cpdf.drawString(330 + x_offset, y_position - 67, f"{data_row[5]:.2f}")  # 344
        cpdf.drawString(395 + x_offset, y_position - 67, f"{data_row[6]:.2f}")  # 409
        cpdf.drawString(485 + x_offset, y_position - 67, f"{data_row[7]:.2f}")  # 499

    def _draw_totals_page(self):
        """Desenează pagina de totaluri"""
        cpdf = self.pdf_canvas
        page_height = A4[1]
        y_position = page_height - 150

        # Titlu
        cpdf.setFont('DejaVuBoldSans', 14)
        cpdf.drawString(180, page_height - 50, f"SITUAȚIE LUNARĂ")
        cpdf.drawString(150, page_height - 80, f"LUNA {self.luna:02d} - ANUL {self.an}")

        # Chenarul pentru totaluri
        cpdf.setLineWidth(2)
        cpdf.rect(100, y_position - 150, 400, 120)

        # Calculează totalurile
        total_dobanda = sum(r[2] for r in self.chitante_data)
        total_imprumut = sum(r[3] for r in self.chitante_data)
        total_depuneri = sum(r[5] for r in self.chitante_data)
        total_retrageri = sum(r[6] for r in self.chitante_data)
        total_general = total_dobanda + total_imprumut + total_depuneri

        # Liniile interioare
        cpdf.line(100, y_position - 90, 500, y_position - 90)
        cpdf.line(300, y_position - 150, 300, y_position - 30)

        # Text și valori
        cpdf.setFont('Arial', 10)
        cpdf.drawString(120, y_position - 60, "Total dobândă:")
        cpdf.drawString(220, y_position - 60, f"{total_dobanda:.2f} €")

        cpdf.drawString(120, y_position - 80, "Total împrumut:")
        cpdf.drawString(220, y_position - 80, f"{total_imprumut:.2f} €")

        cpdf.drawString(320, y_position - 60, "Total depuneri:")
        cpdf.drawString(420, y_position - 60, f"{total_depuneri:.2f} €")

        cpdf.drawString(320, y_position - 80, "Total retrageri:")
        cpdf.drawString(420, y_position - 80, f"{total_retrageri:.2f} €")

        # Total general - CENTRAT
        cpdf.setFont('DejaVuBoldSans', 12)
        cpdf.drawString(150, y_position - 120, f"TOTAL GENERAL:")

        # Calculează poziția centrată pentru sumă în partea dreaptă
        total_text = f"{total_general:.2f} €"
        cpdf.drawString(380, y_position - 120, total_text)

        # Data generării
        cpdf.setFont('Arial', 8)
        cpdf.drawString(100, 30, f"Generat la: {date.today().strftime('%d.%m.%Y')}")
        cpdf.drawString(400, 30, f"Total chitanțe: {len(self.chitante_data)}")

    def _update_chitante_db(self):
        """Versiune cu semantică clară pentru STARTCH_PR"""
        try:
            chitante_path = os.path.join(self.database_dir, "CHITANTE.db")
            with sqlite3.connect(chitante_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ROWID, STARTCH_AC FROM CHITANTE LIMIT 1")
                row = cursor.fetchone()

                if row:
                    row_id, startch_ac_anterior = row

                    # Pentru continuare normală: STARTCH_PR = ultimul număr din sesiunea precedentă
                    # Pentru resetare: STARTCH_PR = 0 (se detectează că nr_chitanta_init = 1)
                    if self.nr_chitanta_init == 1:
                        # Resetare detectată
                        startch_pr = 0
                        self._log(f"📝 Resetare detectată: STARTCH_PR setat la 0")
                    else:
                        # Continuare normală
                        startch_pr = startch_ac_anterior
                        self._log(f"📝 Continuare normală: STARTCH_PR = {startch_pr}")

                    cursor.execute("UPDATE CHITANTE SET STARTCH_PR=?, STARTCH_AC=? WHERE ROWID=?",
                                   (startch_pr, self.chit_cit, row_id))
                else:
                    # Prima înregistrare ever
                    cursor.execute("INSERT INTO CHITANTE (STARTCH_PR, STARTCH_AC) VALUES (?,?)",
                                   (0, self.chit_cit))

                conn.commit()
        except Exception as e:
            self._log(f"⚠️ Eroare actualizare CHITANTE.db: {e}")

    def _update_progress(self, value, message):
        """Actualizează bara de progres și mesajul"""
        self.parent._update_pdf_progress(value, message)

    def _log(self, message):
        """Adaugă mesaj în jurnal"""
        self.parent._log_message(message)

    def _handle_error(self, error_message):
        """Gestionează erorile"""
        self._log(f"❌ {error_message}")
        QTimer.singleShot(100, lambda: self.parent._on_pdf_generation_error(error_message))


class ListariEURWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.database_directory = self._get_database_directory()
        self.pdf_generator = None
        self.generated_file_path = ""

        # 🆕 PROTECȚIE ANTI-ÎNGHEȚARE PENTRU PREVIEW
        self._is_updating_preview = False
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.timeout.connect(self._execute_preview_update)
        self._update_queue_count = 0

        # Watchdog anti-înghețare
        self.last_activity = QTime.currentTime()
        self.watchdog_timer = QTimer(self)
        self.watchdog_timer.timeout.connect(self._watchdog_check)
        self.watchdog_timer.start(3000)  # Verifică la 3 secunde

        self._init_ui()
        self._apply_styles()
        self._initial_load()
        self._log_message("✅ Modul Chitanțe CAR EURO inițializat - Preview manual cu progres")
        self._log_message("🛡️ Sistem anti-înghețare ULTRA activ")

    def _get_database_directory(self):
        """Determină directorul cu bazele de date"""
        try:
            if getattr(sys, 'frozen', False):
                return os.path.dirname(sys.executable)
            else:
                return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        except:
            return os.getcwd()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # Header simplificat - FĂRĂ CEAS
        header_layout = QHBoxLayout()
        title_label = QLabel("📄 Chitanțe CAR - Tipărire Lunară EURO")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)  # Centrat pentru că nu mai avem ceas
        header_layout.addWidget(title_label)
        main_layout.addLayout(header_layout)

        # Layout principal
        content_layout = QHBoxLayout()
        content_layout.setSpacing(8)

        # Panoul de configurare (stânga)
        config_frame = QFrame()
        config_frame.setObjectName("configFrame")
        config_layout = QVBoxLayout(config_frame)
        config_layout.setSpacing(6)

        # Grupa perioada
        period_group = QGroupBox("📅 Perioada Chitanțelor")
        period_group.setObjectName("periodGroup")
        period_layout = QGridLayout(period_group)
        period_layout.setSpacing(5)

        luna_label = QLabel("Luna:")
        luna_label.setObjectName("fieldLabel")
        self.input_luna = QComboBox()
        self.input_luna.setObjectName("lunaCombo")
        luna_options = ["01 - Ianuarie", "02 - Februarie", "03 - Martie",
                        "04 - Aprilie", "05 - Mai", "06 - Iunie",
                        "07 - Iulie", "08 - August", "09 - Septembrie",
                        "10 - Octombrie", "11 - Noiembrie", "12 - Decembrie"]
        self.input_luna.addItems(luna_options)
        self.input_luna.setCurrentIndex(date.today().month - 1)

        an_label = QLabel("Anul:")
        an_label.setObjectName("fieldLabel")
        self.input_an = QSpinBox()
        self.input_an.setObjectName("anSpin")
        self.input_an.setRange(2000, date.today().year + 10)
        self.input_an.setValue(date.today().year)

        period_layout.addWidget(luna_label, 0, 0)
        period_layout.addWidget(self.input_luna, 0, 1)
        period_layout.addWidget(an_label, 1, 0)
        period_layout.addWidget(self.input_an, 1, 1)
        config_layout.addWidget(period_group)

        # Grupa setări tipărire
        setari_group = QGroupBox("⚙️ Setări Tipărire")
        setari_group.setObjectName("setariGroup")
        setari_layout = QGridLayout(setari_group)
        setari_layout.setSpacing(5)

        nr_chitanta_label = QLabel("Nr. chitanță curent:")
        nr_chitanta_label.setObjectName("fieldLabel")
        self.input_nr_chitanta = QLineEdit()
        self.input_nr_chitanta.setObjectName("nrChitantaInput")
        self.input_nr_chitanta.setValidator(QIntValidator(1, 999999999))
        self.input_nr_chitanta.setPlaceholderText("Ex: 1001")

        nr_chitante_label = QLabel("Nr. chitanțe de tipărit:")
        nr_chitante_label.setObjectName("fieldLabel")
        self.input_nr_chitante_tiparit = QLineEdit()
        self.input_nr_chitante_tiparit.setObjectName("nrChitanteInput")
        self.input_nr_chitante_tiparit.setReadOnly(True)
        self.input_nr_chitante_tiparit.setStyleSheet("background-color: #f0f0f0;")

        chitante_per_pagina_label = QLabel("Chitanțe per pagină:")
        chitante_per_pagina_label.setObjectName("fieldLabel")
        self.input_chitante_per_pagina = QSpinBox()
        self.input_chitante_per_pagina.setObjectName("chitantePerPaginaSpin")
        self.input_chitante_per_pagina.setRange(5, 15)
        self.input_chitante_per_pagina.setValue(10)

        setari_layout.addWidget(nr_chitanta_label, 0, 0)
        setari_layout.addWidget(self.input_nr_chitanta, 0, 1)
        setari_layout.addWidget(nr_chitante_label, 1, 0)
        setari_layout.addWidget(self.input_nr_chitante_tiparit, 1, 1)
        setari_layout.addWidget(chitante_per_pagina_label, 2, 0)
        setari_layout.addWidget(self.input_chitante_per_pagina, 2, 1)
        config_layout.addWidget(setari_group)

        # Grupa acțiuni
        actions_group = QGroupBox("⚡ Acțiuni")
        actions_group.setObjectName("actionsGroup")
        actions_layout = QGridLayout(actions_group)
        actions_layout.setSpacing(3)

        self.btn_preview = QPushButton("🔍 Preview")
        self.btn_preview.setObjectName("previewButton")
        self.btn_preview.clicked.connect(self._update_preview)
        actions_layout.addWidget(self.btn_preview, 0, 0)

        self.btn_print = QPushButton("📄 Tipărește PDF")
        self.btn_print.setObjectName("printButton")
        self.btn_print.clicked.connect(self._start_print_process)
        actions_layout.addWidget(self.btn_print, 0, 1)

        self.btn_reset = QPushButton("🔄 Reset")
        self.btn_reset.setObjectName("resetButton")
        self.btn_reset.clicked.connect(self._reset_formular)
        actions_layout.addWidget(self.btn_reset, 1, 0)

        self.btn_open_file = QPushButton("📁 Deschide PDF")
        self.btn_open_file.setObjectName("openFileButton")
        self.btn_open_file.clicked.connect(self._open_generated_file)
        self.btn_open_file.setEnabled(False)
        actions_layout.addWidget(self.btn_open_file, 1, 1)

        config_layout.addWidget(actions_group)

        # Bara de progres UNIFICATĂ pentru toate operațiile
        progress_group = QGroupBox("📊 Progres Operații")
        progress_group.setObjectName("progressGroup")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("")
        self.progress_label.setObjectName("progressLabel")
        self.progress_label.setVisible(False)
        progress_layout.addWidget(self.progress_label)

        self.btn_cancel = QPushButton("🛑 Anulează")
        self.btn_cancel.setObjectName("cancelButton")
        self.btn_cancel.setVisible(False)
        self.btn_cancel.clicked.connect(self._cancel_operation)
        progress_layout.addWidget(self.btn_cancel)

        config_layout.addWidget(progress_group)
        config_layout.addStretch()

        # Panoul de preview (dreapta)
        preview_frame = QFrame()
        preview_frame.setObjectName("previewFrame")
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setSpacing(6)

        # Tabel pentru previzualizarea datelor - OPTIMIZAT cu QTableView și QStandardItemModel
        data_group = QGroupBox("📊 Previzualizare Chitanțe")
        data_group.setObjectName("dataGroup")
        data_layout = QVBoxLayout(data_group)

        self.data_table = QTableView()  # Schimbat din QTableWidget în QTableView
        self.data_table.setObjectName("dataTable")
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(QTableView.SelectRows)

        # Model pentru date - RAPIDĂ POPULARE
        self.table_model = QStandardItemModel()
        self.data_table.setModel(self.table_model)

        data_layout.addWidget(self.data_table)

        self.summary_label = QLabel("💡 Apăsați 'Preview' pentru a încărca datele...")
        self.summary_label.setObjectName("summaryLabel")
        self.summary_label.setWordWrap(True)
        data_layout.addWidget(self.summary_label)
        preview_layout.addWidget(data_group)

        # Zona de log
        log_group = QGroupBox("📝 Jurnal")
        log_group.setObjectName("logGroup")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setObjectName("logText")
        self.log_text.setPlaceholderText("Activitatea va fi înregistrată aici...")
        self.log_text.setMaximumHeight(120)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)

        log_buttons_layout = QHBoxLayout()

        clear_log_btn = QPushButton("🗑️")
        clear_log_btn.setObjectName("clearLogButton")
        clear_log_btn.clicked.connect(self.log_text.clear)
        clear_log_btn.setMaximumWidth(30)
        log_buttons_layout.addWidget(clear_log_btn)

        save_log_btn = QPushButton("💾")
        save_log_btn.setObjectName("saveLogButton")
        save_log_btn.clicked.connect(self._save_log)
        save_log_btn.setMaximumWidth(30)
        log_buttons_layout.addWidget(save_log_btn)

        log_buttons_layout.addStretch()
        log_layout.addLayout(log_buttons_layout)
        preview_layout.addWidget(log_group)

        # Adăugăm frame-urile la layout principal
        content_layout.addWidget(config_frame, 4)
        content_layout.addWidget(preview_frame, 6)
        main_layout.addLayout(content_layout)

        # Conectăm semnalele - FĂRĂ preview automat
        self.input_luna.currentIndexChanged.connect(self._on_period_changed)
        self.input_an.valueChanged.connect(self._on_period_changed)

    def _apply_styles(self):
        self.setStyleSheet("""
            QLabel#titleLabel {
                font-size: 16pt;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 8px;
                padding: 8px;
            }
            QLabel#fieldLabel {
                font-size: 9pt;
                font-weight: bold;
                color: #34495e;
                min-width: 50px;
            }
            QLabel#summaryLabel {
                font-size: 10pt;
                font-weight: bold;
                color: #2c3e50;
                background-color: #e8f4fd;
                padding: 8px;
                border-radius: 5px;
                border: 1px solid #3498db;
            }
            QLabel#progressLabel {
                font-size: 9pt;
                color: #2c3e50;
                font-weight: bold;
            }
            QFrame#configFrame, QFrame#previewFrame {
                border: 2px solid #3498db;
                border-radius: 8px;
                background-color: #f8f9fa;
                padding: 6px;
            }
            QGroupBox {
                font-size: 9pt;
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                margin-top: 4px;
                padding-top: 6px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: #f8f9fa;
            }
            QComboBox#lunaCombo, QSpinBox#anSpin, QSpinBox#chitantePerPaginaSpin {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 4px;
                font-size: 9pt;
                background-color: white;
            }
            QComboBox#lunaCombo:focus, QSpinBox#anSpin:focus, QSpinBox#chitantePerPaginaSpin:focus {
                border-color: #3498db;
            }
            QLineEdit#nrChitantaInput, QLineEdit#nrChitanteInput {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 4px;
                font-size: 9pt;
                background-color: white;
            }
            QLineEdit#nrChitantaInput:focus {
                border-color: #3498db;
            }
            QPushButton#previewButton {
                background-color: #f39c12;
                color: white;
                border: 1px solid #e67e22;
                border-radius: 6px;
                padding: 8px;
                font-size: 10pt;
                font-weight: bold;
                min-height: 12px;
            }
            QPushButton#previewButton:hover {
                background-color: #e67e22;
            }
            QPushButton#previewButton:disabled {
                background-color: #95a5a6;
                border-color: #7f8c8d;
            }
            QPushButton#printButton {
                background-color: #27ae60;
                color: white;
                border: 1px solid #229954;
                border-radius: 6px;
                padding: 8px;
                font-size: 10pt;
                font-weight: bold;
                min-height: 12px;
            }
            QPushButton#printButton:hover {
                background-color: #229954;
            }
            QPushButton#printButton:disabled {
                background-color: #95a5a6;
                border-color: #7f8c8d;
            }
            QPushButton#resetButton {
                background-color: #95a5a6;
                color: white;
                border: 1px solid #7f8c8d;
                border-radius: 6px;
                padding: 6px;
                font-size: 9pt;
                font-weight: bold;
                min-height: 10px;
            }
            QPushButton#resetButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton#openFileButton {
                background-color: #3498db;
                color: white;
                border: 1px solid #2980b9;
                border-radius: 6px;
                padding: 6px;
                font-size: 9pt;
                font-weight: bold;
                min-height: 10px;
            }
            QPushButton#openFileButton:hover {
                background-color: #2980b9;
            }
            QPushButton#openFileButton:disabled {
                background-color: #95a5a6;
                border-color: #7f8c8d;
            }
            QPushButton#cancelButton {
                background-color: #e74c3c;
                color: white;
                border: 1px solid #c0392b;
                border-radius: 6px;
                padding: 6px;
                font-size: 9pt;
                font-weight: bold;
                min-height: 10px;
            }
            QPushButton#cancelButton:hover {
                background-color: #c0392b;
            }
            QPushButton#clearLogButton, QPushButton#saveLogButton {
                background-color: #e74c3c;
                color: white;
                border: 1px solid #c0392b;
                border-radius: 3px;
                padding: 2px;
                font-size: 8pt;
                font-weight: bold;
            }
            QPushButton#clearLogButton:hover, QPushButton#saveLogButton:hover {
                background-color: #c0392b;
            }
            QPushButton#saveLogButton {
                background-color: #27ae60;
                border-color: #229954;
            }
            QPushButton#saveLogButton:hover {
                background-color: #229954;
            }
            QTableView#dataTable {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #ffffff;
                font-size: 8pt;
                gridline-color: #ecf0f1;
                selection-background-color: #3498db;
                selection-color: white;
                alternate-background-color: #f8f9fa;
            }
            QTableView#dataTable::item {
                padding: 3px;
                border-bottom: 1px solid #ecf0f1;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 3px;
                border: 1px solid #2c3e50;
                font-weight: bold;
                font-size: 8pt;
            }
            QTextEdit#logText {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: #ffffff;
                font-family: 'Courier New', monospace;
                font-size: 9pt;
                padding: 4px;
                line-height: 1.3;
            }
            QProgressBar#progressBar {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
                font-size: 9pt;
            }
            QProgressBar#progressBar::chunk {
                background-color: #f39c12;
                border-radius: 3px;
            }
        """)

    def _log_message(self, message):
        """Adaugă un mesaj în jurnalul activității"""
        timestamp = QTime.currentTime().toString("hh:mm:ss")
        formatted_message = f"[{timestamp}] {message}"
        self.log_text.append(formatted_message)
        self.last_activity = QTime.currentTime()  # Marchează activitatea

    def _watchdog_check(self):
        """Verifică starea aplicației și previne înghețările - versiune îmbunătățită"""
        try:
            current_time = QTime.currentTime()

            # Verifică dacă o operație de preview a rămas blocată
            if self._is_updating_preview:
                time_diff = self.last_activity.msecsTo(current_time)
                if time_diff > 25000:  # Mărit timeout la 25 secunde pentru operații mari
                    self._log_message(
                        f"⚠️ Timeout operație preview după {time_diff / 1000:.1f}s - se forțează resetarea")
                    self._force_reset_preview_state()

            # Marchează activitatea și procesează evenimente
            QApplication.processEvents()

            # Auto-recovery dacă sunt butoane blocate fără motiv
            if not self.btn_print.isEnabled() and not self.pdf_generator and not self._is_updating_preview:
                self._log_message("⚠️ Recovery auto: resetare stare butoane")
                self._reset_ui_state()

        except Exception as e:
            self._log_message(f"❌ Eroare watchdog: {e}")

    def _initial_load(self):
        """Încărcare inițială a datelor - FĂRĂ preview automat"""
        QTimer.singleShot(100, self._load_current_receipt_number)
        QTimer.singleShot(200, self._update_receipt_count)
        # Nu mai apelăm _update_preview() automat!

    def _load_current_receipt_number(self):
        """Încarcă numărul chitanței curente din DB"""
        try:
            chitante_path = os.path.join(self.database_directory, "CHITANTE.db")

            if not os.path.exists(chitante_path):
                self.input_nr_chitanta.setText("1")
                return

            with sqlite3.connect(chitante_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT STARTCH_AC FROM CHITANTE LIMIT 1')
                result = cursor.fetchone()
                nr_chitanta = result[0] if result else 1
                self.input_nr_chitanta.setText(str(nr_chitanta))

                # Verificare număr mare
                if len(str(nr_chitanta)) >= 7:
                    self._show_safe_warning("Atenție - Număr chitanță mare",
                                            "Numărul curent al chitanței are 8+ cifre.\n"
                                            "Este recomandat să resetați numărul după această sesiune.")

        except Exception as e:
            self._log_message(f"❌ Eroare încărcare nr. chitanță: {e}")
            self.input_nr_chitanta.setText("1")

    def _on_period_changed(self):
        """Apelat când luna sau anul se schimbă - DOAR actualizează numărul de chitanțe"""
        # Nu mai facem preview automat, doar actualizăm numărul de chitanțe
        QTimer.singleShot(50, self._update_receipt_count)
        self._log_message(f"📅 Perioadă schimbată: {self.input_luna.currentText()} {self.input_an.value()}")

    def _update_receipt_count(self):
        """Actualizează numărul de chitanțe de tipărit"""
        try:
            luna_text = self.input_luna.currentText()[:2]
            luna = int(luna_text)
            an = self.input_an.value()

            depcred_path = os.path.join(self.database_directory, "DEPCREDEUR.db")

            if not os.path.exists(depcred_path):
                self.input_nr_chitante_tiparit.setText("0")
                return

            with sqlite3.connect(depcred_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM DEPCRED WHERE LUNA=? AND ANUL=?', (luna, an))
                result = cursor.fetchone()
                count = result[0] if result else 0
                self.input_nr_chitante_tiparit.setText(str(count))

        except Exception as e:
            self._log_message(f"❌ Eroare numărare chitanțe: {e}")
            self.input_nr_chitante_tiparit.setText("0")

    def _update_preview(self):
        """Actualizează previzualizarea datelor - MANUAL cu bara de progres"""
        # Verificăm dacă o actualizare este deja în curs
        if self._is_updating_preview:
            self._log_message("⚠️ Actualizare preview deja în curs, se ignoră cererea")
            return

        # Pornim actualizarea cu progres
        self._preview_timer.start(50)  # Start rapid pentru feedback imediat

    def _execute_preview_update(self):
        """Execută actualizarea preview-ului cu bara de progres - VERSIUNE ULTRA-OPTIMIZATĂ"""
        if self._is_updating_preview:
            self._log_message("⚠️ Actualizare preview blocată - operație în curs")
            return

        # Setăm flag-ul de protecție
        self._is_updating_preview = True

        try:
            # Afișăm bara de progres
            self._show_progress_ui(True, "Inițializare previzualizare...")
            self._update_progress(5, "Verificare date...")

            # Dezactivăm butoanele pentru a preveni apelurile multiple
            self._set_preview_buttons_enabled(False)

            # Marchează activitatea pentru watchdog
            self._mark_activity()

            luna_text = self.input_luna.currentText()[:2]
            luna = int(luna_text)
            an = self.input_an.value()

            self._log_message(f"🔍 Previzualizare {self.input_luna.currentText()} {an}")

            depcred_path = os.path.join(self.database_directory, "DEPCREDEUR.db")
            membrii_path = os.path.join(self.database_directory, "MEMBRIIEUR.db")

            if not os.path.exists(depcred_path) or not os.path.exists(membrii_path):
                self.summary_label.setText("❌ Nu s-au găsit bazele de date necesare!")
                self.table_model.clear()
                self._log_message("❌ Baze de date lipsă")
                return

            self._update_progress(15, "Conectare la baza de date...")

            # Încărcarea datelor cu progres
            final_rows = self._load_preview_data_safe(depcred_path, membrii_path, luna, an)

            if final_rows is None:
                # Eroare la încărcare
                self.summary_label.setText("❌ Eroare la încărcarea datelor")
                self.table_model.clear()
                return

            if not final_rows:
                self.summary_label.setText(f"ℹ️ Nu s-au găsit date pentru {self.input_luna.currentText()} {an}")
                self.table_model.clear()
                self._log_message(f"ℹ️ Nu există date pentru {luna:02d}-{an}")
                return

            # ALERTĂ pentru seturi mari de date
            if len(final_rows) > 500:
                self._log_message(f"⚠️ Set mare de date: {len(final_rows)} chitanțe - procesare ULTRA-OPTIMIZATĂ")

            self._update_progress(70, f"Populare RAPIDĂ cu {len(final_rows)} chitanțe...")

            # IMPORTANT: Marchează activitatea înainte de popularea tabelului
            self._mark_activity()

            # Actualizează interfața cu datele încărcate - RAPID
            self._populate_preview_table_fast(final_rows)

            # Verifică din nou dacă operația nu a fost anulată
            if not self._is_updating_preview:
                return

            self._update_progress(90, "Calculare totaluri...")

            # Calculuri pentru sumar
            total_dobanda = sum(r[2] for r in final_rows)
            total_imprumut = sum(r[3] for r in final_rows)
            total_depuneri = sum(r[5] for r in final_rows)
            total_retrageri = sum(r[6] for r in final_rows)
            total_general = total_dobanda + total_imprumut + total_depuneri

            # Actualizează sumarul
            summary_text = (
                f"📊 {len(final_rows)} chitanțe | 💰 Total general: {total_general:.2f} EUR\n"
                f"🔹 Dobândă: {total_dobanda:.2f} | Rate: {total_imprumut:.2f} | Depuneri: {total_depuneri:.2f} | Retrageri: {total_retrageri:.2f}"
            )
            self.summary_label.setText(summary_text)

            self._update_progress(100, "Previzualizare completă!")
            QTimer.singleShot(1000, lambda: self._hide_progress_ui())  # Ascunde după 1 secundă

            self._log_message(
                f"✅ Previzualizare ULTRA-RAPIDĂ completă: {len(final_rows)} chitanțe, total {total_general:.2f} EUR")

        except Exception as e:
            error_msg = f"❌ Eroare la încărcarea datelor: {str(e)}"
            self.summary_label.setText(error_msg)
            self.table_model.clear()
            self._log_message(f"❌ Eroare previzualizare: {str(e)}")

        finally:
            # Resetăm flag-ul de protecție și reactivăm butoanele
            self._is_updating_preview = False
            self._set_preview_buttons_enabled(True)
            self._mark_activity()

    def _populate_preview_table_fast(self, final_rows):
        """Populează tabelul ULTRA-RAPID cu QStandardItemModel - optimizat pentru performanță maximă"""
        try:
            self._update_progress(72, "Configurare model date...")

            # Headers
            headers = ["Nr.Fișă", "Nume", "Dobândă", "Rată Împr.", "Sold Împr.", "Dep.Lun.", "Retr.FS", "Sold Dep.",
                       "Total Plată"]

            total_rows = len(final_rows)
            self._log_message(f"📊 Populare ULTRA-RAPIDĂ: {total_rows} rânduri")

            # Configurează modelul - RAPID
            self.table_model.clear()
            self.table_model.setHorizontalHeaderLabels(headers)

            self._update_progress(75, "Preparare date în memorie...")

            # Pentru seturi mari, limitează afișarea pentru performanță
            if total_rows > 1000:
                display_rows = final_rows[:500]  # Afișează doar primele 500
                self._log_message(f"🚀 Set foarte mare: afișez primele 500 din {total_rows} chitanțe pentru performanță")
                summary_suffix = f"\n⚡ Afișare optimizată: prime 500 din {total_rows} chitanțe"
            else:
                display_rows = final_rows
                summary_suffix = ""

            # Pregătește toate items-urile DEODATĂ în memorie
            all_items = []
            for row_index, row_data in enumerate(display_rows):
                if not self._is_updating_preview:
                    return

                total_plata = row_data[2] + row_data[3] + row_data[5]

                # Creează tot rândul deodată
                row_items = [
                    QStandardItem(str(row_data[8])),  # Nr.Fișă
                    QStandardItem(row_data[9]),  # Nume
                    QStandardItem(f"{row_data[2]:.2f}"),  # Dobândă
                    QStandardItem(f"{row_data[3]:.2f}"),  # Rată Împr.
                    QStandardItem(f"{row_data[4]:.2f}"),  # Sold Împr.
                    QStandardItem(f"{row_data[5]:.2f}"),  # Dep.Lun.
                    QStandardItem(f"{row_data[6]:.2f}"),  # Retr.FS
                    QStandardItem(f"{row_data[7]:.2f}"),  # Sold Dep.
                    QStandardItem(f"{total_plata:.2f}")  # Total Plată
                ]
                all_items.append(row_items)

                # Update progres la fiecare 100 de rânduri pentru a nu încetini
                if row_index % 100 == 0:
                    progress = 75 + int((row_index / len(display_rows)) * 10)  # 75% -> 85%
                    self._update_progress(progress, f"Preparare rând {row_index + 1}/{len(display_rows)}...")
                    QApplication.processEvents()
                    self._mark_activity()

            self._update_progress(85, "Încărcare BULK în model...")

            # Setează dimensiunea modelului o singură dată
            self.table_model.setRowCount(len(all_items))
            self.table_model.setColumnCount(len(headers))

            # Încarcă totul RAPID în model - batch de 50 de rânduri
            batch_size = 50
            for batch_start in range(0, len(all_items), batch_size):
                if not self._is_updating_preview:
                    return

                batch_end = min(batch_start + batch_size, len(all_items))

                # Încarcă batch-ul current
                for row_index in range(batch_start, batch_end):
                    row_items = all_items[row_index]
                    # Setează tot rândul deodată - MULT mai rapid
                    for col_index, item in enumerate(row_items):
                        self.table_model.setItem(row_index, col_index, item)

                # Update progres la fiecare batch
                progress = 85 + int((batch_end / len(all_items)) * 10)  # 85% -> 95%
                self._update_progress(progress, f"Încărcare rapid rânduri {batch_end}/{len(all_items)}...")

                # ProcessEvents mai rar pentru performanță
                if batch_start % (batch_size * 4) == 0:  # La fiecare 4 batch-uri
                    QApplication.processEvents()
                    self._mark_activity()

            self._update_progress(95, "Finalizare afișare...")

            # Ajustează coloanele - DUPĂ încărcarea tuturor datelor
            header = self.data_table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.Stretch)  # Numele se întinde

            # Adaugă sufixul pentru seturi mari
            if summary_suffix:
                current_summary = self.summary_label.text()
                if not current_summary.endswith(summary_suffix):
                    self.summary_label.setText(current_summary + summary_suffix)

            self._log_message(f"✅ Tabel populat ULTRA-RAPID: {len(all_items)} rânduri afișate din {total_rows}")

        except Exception as e:
            self._log_message(f"❌ Eroare populare rapidă: {str(e)}")
            raise

    def _load_preview_data_safe(self, depcred_path, membrii_path, luna, an):
        """Încarcă datele pentru preview cu progres și protecție"""
        final_rows = []
        conn1 = None
        conn2 = None

        try:
            self._update_progress(20, "Conectare DEPCREDEUR.db...")

            # Încercare cu timeout pentru conexiuni
            conn1 = sqlite3.connect(f"file:{depcred_path}?mode=ro&timeout=5000", uri=True)
            conn2 = sqlite3.connect(f"file:{membrii_path}?mode=ro&timeout=5000", uri=True)

            cursor1 = conn1.cursor()
            cursor2 = conn2.cursor()

            # Setăm timeout pentru query-uri
            conn1.execute("PRAGMA busy_timeout = 5000")
            conn2.execute("PRAGMA busy_timeout = 5000")

            self._update_progress(30, f"Citire date pentru {luna:02d}-{an}...")

            cursor1.execute(
                'SELECT LUNA, ANUL, DOBANDA, IMPR_CRED, IMPR_SOLD, DEP_DEB, DEP_CRED, DEP_SOLD, NR_FISA '
                'FROM DEPCRED WHERE LUNA=? AND ANUL=?',
                (luna, an)
            )
            depcred_rows = cursor1.fetchall()

            if not depcred_rows:
                return []

            total_rows = len(depcred_rows)
            self._update_progress(40, f"Procesare {total_rows} înregistrări...")

            # Procesează fiecare rând cu progres și verificare de anulare
            for i, row in enumerate(depcred_rows):
                # Verifică dacă operația a fost anulată
                if not self._is_updating_preview:
                    self._log_message("⚠️ Încărcare întreruptă de utilizator")
                    return None

                # Actualizează progresul la fiecare 20% din date pentru a nu încetini
                if i % max(1, total_rows // 5) == 0:
                    progress = 40 + int((i / total_rows) * 25)  # 40% -> 65%
                    self._update_progress(progress, f"Procesare înregistrare {i + 1}/{total_rows}...")
                    QApplication.processEvents()
                    self._mark_activity()

                nr_fisa = row[8]
                cursor2.execute('SELECT NUM_PREN FROM MEMBRII WHERE NR_FISA = ?', (nr_fisa,))
                nume = cursor2.fetchone()
                if nume:
                    final_rows.append((*row, nume[0]))

            self._update_progress(65, "Sortare rezultate...")
            # Sortează rezultatele
            final_rows.sort(key=lambda x: x[9])
            return final_rows

        except sqlite3.OperationalError as e:
            if "database is locked" in str(e).lower():
                self._log_message("❌ Baza de date este blocată - se încearcă din nou")
                self._update_progress(0, "Reîncercare în 1 secundă...")
                QTimer.singleShot(1000, lambda: self._retry_preview_update())
                return None
            else:
                raise

        except Exception as e:
            self._log_message(f"❌ Eroare încărcare date: {str(e)}")
            raise

        finally:
            if conn1:
                conn1.close()
            if conn2:
                conn2.close()

    def _retry_preview_update(self):
        """Reîncearcă actualizarea preview-ului după o eroare de blocare DB"""
        if not self._is_updating_preview:
            self._log_message("🔄 Reîncercare actualizare preview...")
            QTimer.singleShot(100, self._execute_preview_update)

    def _set_preview_buttons_enabled(self, enabled):
        """Activează/dezactivează butoanele care afectează preview-ul"""
        self.btn_preview.setEnabled(enabled)
        self.input_luna.setEnabled(enabled)
        self.input_an.setEnabled(enabled)

        # Actualizează textul butonului preview
        if enabled:
            self.btn_preview.setText("🔍 Preview")
        else:
            self.btn_preview.setText("⏳ Se încarcă...")

    def _force_reset_preview_state(self):
        """Forțează resetarea stării preview-ului în caz de blocare"""
        self._is_updating_preview = False
        self._set_preview_buttons_enabled(True)
        self._preview_timer.stop()
        self._update_queue_count = 0
        self._hide_progress_ui()
        self.summary_label.setText("⚠️ Operație resetată din cauza timeout-ului")
        self._mark_activity()
        self._log_message("🔄 Stare preview resetată forțat")

    def _update_progress(self, value, message):
        """Actualizează bara de progres unificată - cu logging îmbunătățit"""
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)
        self._mark_activity()

        # Log progresul la milestone-uri importante pentru debugging
        if value % 25 == 0 or value >= 95:  # La 0%, 25%, 50%, 75%, 95%+
            self._log_message(f"📊 Progres: {value}% - {message}")

    def _show_progress_ui(self, show, initial_message=""):
        """Afișează/ascunde bara de progres unificată"""
        self.progress_bar.setVisible(show)
        self.progress_label.setVisible(show)
        self.btn_cancel.setVisible(show)

        if show:
            self.progress_bar.setValue(0)
            self.progress_label.setText(initial_message)

    def _hide_progress_ui(self):
        """Ascunde bara de progres"""
        self._show_progress_ui(False)

    def _start_print_process(self):
        """Pornește procesul de tipărire"""
        self._mark_activity()

        # Verificări preliminarii
        if self.table_model.rowCount() == 0:
            self._show_safe_warning("Date Lipsă",
                                    "Nu există date pentru generarea chitanțelor!\n"
                                    "Apăsați 'Preview' pentru a verifica datele disponibile.")
            return

        try:
            nr_chitanta_str = self.input_nr_chitanta.text()
            nr_chitanta = int(nr_chitanta_str)

            if nr_chitanta <= 0:
                raise ValueError("Numărul chitanței trebuie să fie pozitiv")

        except ValueError:
            self._show_safe_warning("Număr Invalid",
                                    "Numărul chitanței curent nu este valid.\n"
                                    "Introduceți un număr întreg pozitiv.")
            return

        # Verificare număr mare
        if len(nr_chitanta_str) >= 8:
            self._show_large_number_dialog()
        else:
            self._show_confirmation_dialog()

    def _show_large_number_dialog(self):
        """Dialog pentru număr mare de chitanță"""
        msgBox = QMessageBox(self)
        msgBox.setStyleSheet(get_dialog_stylesheet())
        msgBox.setWindowTitle("Atenție - Număr chitanță mare")
        msgBox.setText("Numărul curent al chitanței are 7+ cifre.\n\n"
                       "Doriți să continuați sau să resetați la 1?")
        msgBox.setIcon(QMessageBox.Warning)

        continua_btn = msgBox.addButton("Continuă", QMessageBox.YesRole)
        reseteaza_btn = msgBox.addButton("Resetează la 1", QMessageBox.NoRole)
        anuleaza_btn = msgBox.addButton("Anulează", QMessageBox.RejectRole)

        result = msgBox.exec_()

        if msgBox.clickedButton() == reseteaza_btn:
            self._reset_receipt_number_and_continue()
        elif msgBox.clickedButton() == continua_btn:
            self._show_confirmation_dialog()

    def _reset_receipt_number_and_continue(self):
        """Resetează numărul chitanței și continuă"""
        try:
            chitante_path = os.path.join(self.database_directory, "CHITANTE.db")
            with sqlite3.connect(chitante_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ROWID FROM CHITANTE LIMIT 1")
                row_id = cursor.fetchone()
                if row_id:
                    cursor.execute("UPDATE CHITANTE SET STARTCH_AC=1 WHERE ROWID=?", (row_id[0],))
                else:
                    cursor.execute("INSERT INTO CHITANTE (STARTCH_PR, STARTCH_AC) VALUES (0, 1)")
                conn.commit()

            self.input_nr_chitanta.setText("1")
            self._log_message("🔄 Număr chitanță resetat la 1")

            QTimer.singleShot(100, self._show_confirmation_dialog)

        except Exception as e:
            self._show_safe_error("Eroare", f"Nu s-a putut reseta numărul chitanței: {e}")

    def _show_confirmation_dialog(self):
        """Dialog pentru confirmarea tipăririi"""
        luna_text = self.input_luna.currentText()
        an = self.input_an.value()
        nr_chitante = self.input_nr_chitante_tiparit.text()
        nr_chitanta_init = self.input_nr_chitanta.text()

        mesaj = (f"Generați chitanțele pentru {luna_text} {an}?\n\n"
                 f"Număr chitanțe: {nr_chitante}\n"
                 f"Număr chitanță inițial: {nr_chitanta_init}")

        if afiseaza_intrebare(mesaj, titlu="Confirmare Tipărire", parent=self):
            QTimer.singleShot(50, self._start_pdf_generation)

    def _start_pdf_generation(self):
        """Pornește generarea PDF cu sistemul bazat pe QTimer"""
        try:
            luna_text = self.input_luna.currentText()[:2]
            luna = int(luna_text)
            an = self.input_an.value()
            nr_chitanta_init = int(self.input_nr_chitanta.text())
            chitante_per_pagina = self.input_chitante_per_pagina.value()

            # Afișează bara de progres
            self._show_progress_ui(True, "Inițializare generare PDF...")

            # Setează starea pentru procesare
            self._set_ui_for_processing(True)

            # Creează generatorul PDF
            self.pdf_generator = TimerBasedPDFGenerator(
                self, self.database_directory, luna, an, nr_chitanta_init, chitante_per_pagina
            )

            self._log_message(f"🚀 Generare chitanțe pornită pentru {self.input_luna.currentText()} {an}")

            # Pornește generarea
            self.pdf_generator.start_generation()

        except Exception as e:
            self._show_safe_error("Eroare", f"Nu s-a putut porni generarea: {e}")
            self._reset_ui_state()

    def _update_pdf_progress(self, value, message):
        """Actualizează bara de progres pentru PDF (alias pentru metoda unificată)"""
        self._update_progress(value, message)

    def _on_pdf_generation_success(self, message, file_path):
        """Gestionează succesul generării PDF"""
        self._hide_progress_ui()
        self._reset_ui_state()

        self.generated_file_path = file_path
        self.btn_open_file.setEnabled(True)

        self._log_message(f"✅ {message}")
        self._log_message(f"📁 Fișier salvat: {file_path}")

        # Reîncarcă numărul chitanței actualizat
        QTimer.singleShot(100, self._load_current_receipt_number)

        # Întreabă dacă să deschidă fișierul
        msgBox = QMessageBox(self)
        msgBox.setStyleSheet(get_dialog_stylesheet())
        msgBox.setWindowTitle("Generare Reușită")
        msgBox.setText(f"{message}\n\nDoriți să deschideți fișierul PDF?")
        msgBox.setIcon(QMessageBox.Information)

        yes_btn = msgBox.addButton("Da, deschide", QMessageBox.YesRole)
        no_btn = msgBox.addButton("Nu, mulțumesc", QMessageBox.NoRole)

        result = msgBox.exec_()

        if msgBox.clickedButton() == yes_btn:
            QTimer.singleShot(100, self._open_generated_file)

    def _on_pdf_generation_error(self, error_message):
        """Gestionează erorile generării PDF"""
        self._hide_progress_ui()
        self._reset_ui_state()

        self._show_safe_error("Eroare Generare PDF", f"Generarea a eșuat:\n\n{error_message}")

    def _cancel_operation(self):
        """Anulează operația curentă (Preview sau PDF)"""
        if self.pdf_generator:
            self.pdf_generator.cancel_generation()
            self.pdf_generator = None

        # Anulează și operația de preview dacă e activă
        if self._is_updating_preview:
            self._is_updating_preview = False
            self._set_preview_buttons_enabled(True)

        self._hide_progress_ui()
        self._reset_ui_state()
        self._log_message("🛑 Operație anulată de utilizator")

    def _set_ui_for_processing(self, processing):
        """Setează interfața pentru procesare"""
        self.btn_print.setEnabled(not processing)
        self.btn_preview.setEnabled(not processing)
        self.btn_reset.setEnabled(not processing)
        self.input_luna.setEnabled(not processing)
        self.input_an.setEnabled(not processing)
        self.input_nr_chitanta.setEnabled(not processing)
        self.input_chitante_per_pagina.setEnabled(not processing)

    def _reset_ui_state(self):
        """Resetează starea UI"""
        self._set_ui_for_processing(False)
        self.pdf_generator = None

    def _reset_formular(self):
        """Resetează formularul"""
        self.input_luna.setCurrentIndex(date.today().month - 1)
        self.input_an.setValue(date.today().year)
        self.input_chitante_per_pagina.setValue(10)
        self.btn_open_file.setEnabled(False)
        self.generated_file_path = ""

        # Curăță previzualizarea
        self.table_model.clear()
        self.summary_label.setText("💡 Apăsați 'Preview' pentru a încărca datele...")

        self._log_message("🔄 Formular resetat la valorile implicite")

        # Întreabă despre resetarea numărului chitanței
        if afiseaza_intrebare("Resetați și numărul chitanței la 1?",
                              titlu="Resetare număr chitanță",
                              parent=self):
            self._reset_receipt_number()

        # Actualizează numărul de chitanțe
        QTimer.singleShot(100, self._update_receipt_count)

    def _reset_receipt_number(self):
        """Resetează numărul chitanței la 1"""
        try:
            chitante_path = os.path.join(self.database_directory, "CHITANTE.db")
            with sqlite3.connect(chitante_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ROWID FROM CHITANTE LIMIT 1")
                row_id = cursor.fetchone()
                if row_id:
                    cursor.execute("UPDATE CHITANTE SET STARTCH_AC=1 WHERE ROWID=?", (row_id[0],))
                else:
                    cursor.execute("INSERT INTO CHITANTE (STARTCH_PR, STARTCH_AC) VALUES (0, 1)")
                conn.commit()

            self.input_nr_chitanta.setText("1")
            self._log_message("✅ Număr chitanță resetat la 1")

        except Exception as e:
            self._show_safe_error("Eroare", f"Nu s-a putut reseta numărul chitanței: {e}")

    def _open_generated_file(self):
        """Deschide fișierul PDF generat"""
        self._mark_activity()

        if not self.generated_file_path or not os.path.exists(self.generated_file_path):
            self._show_safe_warning("Fișier Inexistent",
                                    "Fișierul PDF nu există sau a fost mutat!")
            self.btn_open_file.setEnabled(False)
            return

        try:
            self._log_message(f"📁 Deschidere fișier: {os.path.basename(self.generated_file_path)}")

            if platform.system() == "Windows":
                subprocess.Popen(['start', '', self.generated_file_path], shell=True)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", self.generated_file_path])
            else:
                subprocess.Popen(["xdg-open", self.generated_file_path])

        except Exception as e:
            self._show_safe_error("Eroare", f"Nu s-a putut deschide fișierul:\n{e}")

    def _save_log(self):
        """Salvează jurnalul"""
        if not self.log_text.toPlainText().strip():
            self._show_safe_warning("Jurnal Gol", "Nu există conținut de salvat!")
            return

        timestamp = date.today().strftime("%Y%m%d_%H%M%S")
        default_filename = f"jurnal_chitante_{timestamp}.txt"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salvează Jurnalul", default_filename, "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Jurnal Chitanțe CAR - Tipărire Lunară EURO\n")
                    f.write(f"Generat la: {date.today().strftime('%d/%m/%Y')}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(self.log_text.toPlainText())

                self._show_safe_info("Succes", f"Jurnal salvat!\n\nLocație: {file_path}")
                self._log_message(f"💾 Jurnal salvat: {os.path.basename(file_path)}")

            except Exception as e:
                self._show_safe_error("Eroare", f"Eroare la salvarea jurnalului:\n{e}")

    def _mark_activity(self):
        """Marchează activitatea pentru watchdog"""
        self.last_activity = QTime.currentTime()

    def _show_safe_warning(self, title, message):
        """Afișează avertisment thread-safe STILIZAT"""
        QTimer.singleShot(0, lambda: afiseaza_warning(message, parent=self))

    def _show_safe_error(self, title, message):
        """Afișează eroare thread-safe STILIZATĂ"""
        QTimer.singleShot(0, lambda: afiseaza_eroare(message, parent=self))

    def _show_safe_info(self, title, message):
        """Afișează informație thread-safe STILIZATĂ"""
        QTimer.singleShot(0, lambda: afiseaza_info(message, parent=self))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ListariEURWidget()
    window.setWindowTitle("Chitanțe CAR - Tipărire Lunară EURO")
    window.resize(950, 700)
    window.show()
    sys.exit(app.exec_())
