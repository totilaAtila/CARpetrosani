"""
Aplicație desktop cu interfață prietenoasă pentru:
 - Selectarea unui director cu fișiere .db
 - Afișarea listei de fișiere .db găsite
 - Crearea indexurilor (Optimizează indexuri)
 - Listarea indexurilor existente (Listează indexuri)
 - Operațiuni de întreținere (VACUUM, ANALYZE)

Versiune modernizată cu PyQt5 și styling consistent cu modulul Chitanțe CAR.
Suport complet pentru bazele clonate EUR și procesare inteligentă.
"""
import os
import glob
import sqlite3
import sys
from datetime import date
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFileDialog, QFrame, QProgressBar,
    QGroupBox, QGridLayout, QListWidget, QTextEdit, QSplitter
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QTimer, QTime, QThread, pyqtSignal


class DatabaseIndexer(QThread):
    """Thread pentru operațiuni de indexare în background"""
    progress_updated = pyqtSignal(int, str)
    operation_completed = pyqtSignal(str, dict)
    log_message = pyqtSignal(str)

    def __init__(self, operation, databases, parent=None):
        super().__init__(parent)
        self.operation = operation
        self.databases = databases
        self.cancelled = False

    def run(self):
        try:
            if self.operation == "optimize":
                self._optimize_indexes()
            elif self.operation == "list":
                self._list_indexes()
            elif self.operation == "maintenance":
                self._perform_maintenance()
        except Exception as e:
            self.log_message.emit(f"❌ Eroare generală: {str(e)}")

    def cancel_operation(self):
        self.cancelled = True

    def _optimize_indexes(self):
        """Optimizează indexurile pentru bazele de date selectate"""
        rezultate = {}
        total_dbs = len(self.databases)

        self.progress_updated.emit(5, "Inițializare optimizare indexuri...")

        for i, baza in enumerate(self.databases):
            if self.cancelled:
                return

            key = os.path.basename(baza)
            self.log_message.emit(f"🔧 Procesare: {key}")

            # Obține indexurile specifice pentru această bază
            comenzi = self._get_database_indexes(baza)

            if not comenzi:
                self.log_message.emit(f"ℹ️ [{key}] Niciun index de creat")
                rezultate[key] = "Niciun index de creat"
                continue

            try:
                conn = sqlite3.connect(baza, timeout=30.0)
                cur = conn.cursor()

                for j, sql in enumerate(comenzi):
                    if self.cancelled:
                        conn.close()
                        return

                    cur.execute(sql)
                    self.log_message.emit(f"✅ [{key}] Executat: {sql}")

                    # Update progres
                    progress = 10 + int(
                        ((i * len(comenzi) + j + 1) / (total_dbs * max(len(c) for c in [comenzi] if c))) * 80)
                    self.progress_updated.emit(progress, f"Indexare {key}: {j + 1}/{len(comenzi)}")

                conn.commit()
                conn.close()
                rezultate[key] = "Indexuri create/verificate cu succes"
                self.log_message.emit(f"🎯 [{key}] Optimizare completă")

            except Exception as e:
                self.log_message.emit(f"❌ [{key}] Eroare: {e}")
                rezultate[key] = f"Eroare: {e}"

        # Raportează rezultatele
        self.progress_updated.emit(100, "Optimizare completă!")
        self._log_summary(rezultate, "optimizare")
        self.operation_completed.emit("optimize", rezultate)

    def _list_indexes(self):
        """Listează indexurile existente"""
        rezultate = {}
        total_dbs = len(self.databases)

        self.progress_updated.emit(10, "Inițializare listare indexuri...")

        for i, baza in enumerate(self.databases):
            if self.cancelled:
                return

            key = os.path.basename(baza)
            self.log_message.emit(f"📊 Analizare: {key}")

            try:
                conn = sqlite3.connect(baza, timeout=30.0)
                cursor = conn.cursor()
                cursor.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index';")
                indexuri = cursor.fetchall()
                conn.close()

                self.log_message.emit(f"\n📋 Indexuri în {key}:")
                if indexuri:
                    for name, tabel, sql in indexuri:
                        if sql:  # Ignoră indexurile automate
                            self.log_message.emit(f"  🔹 {name} (tabel: {tabel})")
                            self.log_message.emit(f"     SQL: {sql}")
                        else:
                            self.log_message.emit(f"  🔸 {name} (tabel: {tabel}) - index automat")
                else:
                    self.log_message.emit("  ❌ (niciun index definit)")

                rezultate[key] = indexuri

                # Update progres
                progress = 20 + int((i + 1) / total_dbs * 70)
                self.progress_updated.emit(progress, f"Analizat: {key}")

            except Exception as e:
                self.log_message.emit(f"❌ [{key}] Eroare la listare: {e}")
                rezultate[key] = []

        self.progress_updated.emit(100, "Listare completă!")
        self.operation_completed.emit("list", rezultate)

    def _perform_maintenance(self):
        """Efectuează operațiuni de întreținere"""
        rezultate = {}
        total_dbs = len(self.databases)

        self.progress_updated.emit(5, "Inițializare întreținere...")

        for i, baza in enumerate(self.databases):
            if self.cancelled:
                return

            key = os.path.basename(baza)
            self.log_message.emit(f"🧹 Întreținere: {key}")

            try:
                conn = sqlite3.connect(baza, timeout=30.0)
                cur = conn.cursor()

                # VACUUM
                self.progress_updated.emit(10 + int(i / total_dbs * 40), f"VACUUM pe {key}...")
                cur.execute("VACUUM;")
                self.log_message.emit(f"✅ [{key}] VACUUM executat")

                if self.cancelled:
                    conn.close()
                    return

                # ANALYZE
                self.progress_updated.emit(50 + int(i / total_dbs * 40), f"ANALYZE pe {key}...")
                cur.execute("ANALYZE;")
                self.log_message.emit(f"✅ [{key}] ANALYZE executat")

                conn.commit()
                conn.close()
                rezultate[key] = "VACUUM și ANALYZE executate cu succes"
                self.log_message.emit(f"🎯 [{key}] Întreținere completă")

            except Exception as e:
                self.log_message.emit(f"❌ [{key}] Eroare la întreținere: {e}")
                rezultate[key] = f"Eroare: {e}"

        # Raportează rezultatele
        self.progress_updated.emit(100, "Întreținere completă!")
        self._log_summary(rezultate, "întreținere")
        self.operation_completed.emit("maintenance", rezultate)

    def _log_summary(self, rezultate, operation_name):
        """Loghează un sumar al rezultatelor"""
        self.log_message.emit(f"\n📊 Rezumat {operation_name}:")
        for key, result in rezultate.items():
            status = "✅" if "succes" in str(result).lower() else "❌"
            self.log_message.emit(f"{status} {key}: {result}")

    def _get_database_indexes(self, db_path):
        """Determină indexurile pentru o bază de date specifică - versiune hibridă"""
        filename = os.path.basename(db_path).lower()

        # Normalizează numele pentru bazele EUR (elimină sufixul EUR)
        base_name = filename.replace('eur.db', '.db')

        # Configurații specifice cunoscute
        specific_configs = {
            "membrii.db": [
                "CREATE INDEX IF NOT EXISTS idx_fisa ON MEMBRII(NR_FISA);",
                "CREATE INDEX IF NOT EXISTS idx_nume ON MEMBRII(NUM_PREN);"
            ],
            "depcred.db": [
                "CREATE INDEX IF NOT EXISTS idx_depcred_compound ON DEPCRED(NR_FISA, ANUL, LUNA);",
                "CREATE INDEX IF NOT EXISTS idx_depcred_fisa ON DEPCRED(NR_FISA);",
                "CREATE INDEX IF NOT EXISTS idx_depcred_perioada ON DEPCRED(ANUL, LUNA);"
            ],
            "depcredm.db": [
                "CREATE INDEX IF NOT EXISTS idx_depcredm_compound ON DEPCREDM(NR_FISA, ANUL, LUNA);",
                "CREATE INDEX IF NOT EXISTS idx_depcredm_fisa ON DEPCREDM(NR_FISA);"
            ],
            "activi.db": [
                "CREATE INDEX IF NOT EXISTS idx_activi_numpren ON ACTIVI(NUM_PREN);",
                "CREATE INDEX IF NOT EXISTS idx_activi_depsold ON ACTIVI(DEP_SOLD);",
                "CREATE INDEX IF NOT EXISTS idx_activi_fisa ON ACTIVI(NR_FISA);"
            ],
            "inactivi.db": [
                "CREATE INDEX IF NOT EXISTS idx_inactivi_fisa ON INACTIVI(NR_FISA);",
                "CREATE INDEX IF NOT EXISTS idx_inactivi_nume ON INACTIVI(NUM_PREN);"
            ],
            "lichidati.db": [
                "CREATE INDEX IF NOT EXISTS idx_lichidati_fisa ON LICHIDATI(NR_FISA);",
                "CREATE INDEX IF NOT EXISTS idx_lichidati_data ON LICHIDATI(data_lichidare);"
            ],
        }

        # Returnează configurația specifică dacă există
        if base_name in specific_configs:
            self.log_message.emit(f"🎯 [{filename}] Folosesc configurația specifică pentru {base_name}")
            return specific_configs[base_name]

        # Pentru baze necunoscute, generează indexuri generice
        self.log_message.emit(f"🔍 [{filename}] Generez indexuri generice prin analiză")
        return self._generate_generic_indexes(db_path)

    def _generate_generic_indexes(self, db_path):
        """Generează indexuri generice prin analizarea structurii"""
        try:
            conn = sqlite3.connect(db_path, timeout=30.0)
            cursor = conn.cursor()

            # Detectează tabelele și coloanele
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            indexes = []
            for (table_name,) in tables:
                # Detectează coloanele potențial importante
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()

                for col in columns:
                    col_name = col[1]
                    # Creează indexuri pentru coloane uzuale
                    if any(keyword in col_name.upper() for keyword in
                           ['NR_FISA', 'ANUL', 'LUNA', 'ID', 'FISA', 'DATA', 'NUM_PREN']):
                        index_name = f"idx_{table_name.lower()}_{col_name.lower()}"
                        indexes.append(
                            f"CREATE INDEX IF NOT EXISTS {index_name} "
                            f"ON {table_name}({col_name});"
                        )

                # Încearcă să creeze un index compus pentru coloane importante
                important_cols = []
                for col in columns:
                    col_name = col[1]
                    if col_name.upper() in ['NR_FISA', 'ANUL', 'LUNA']:
                        important_cols.append(col_name)

                if len(important_cols) >= 2:
                    compound_cols = ', '.join(important_cols)
                    index_name = f"idx_{table_name.lower()}_compound"
                    indexes.append(
                        f"CREATE INDEX IF NOT EXISTS {index_name} "
                        f"ON {table_name}({compound_cols});"
                    )

            conn.close()
            return indexes

        except Exception as e:
            self.log_message.emit(f"❌ Eroare la generarea indexurilor generice: {e}")
            return []


class OptimizareIndexWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.database_directory = self._get_database_directory()
        self.indexer_thread = None

        # Watchdog anti-înghețare
        self.last_activity = QTime.currentTime()
        self.watchdog_timer = QTimer(self)
        self.watchdog_timer.timeout.connect(self._watchdog_check)
        self.watchdog_timer.start(3000)

        self._init_ui()
        self._apply_styles()
        self._update_file_list()
        self._log_message("✅ Manager Indexuri SQLite inițializat")
        self._log_message("🛡️ Sistem anti-înghețare activ")
        self._log_message("🔄 Suport complet pentru baze EUR clonate")

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
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Layout principal cu splitter
        splitter = QSplitter(Qt.Horizontal)

        # Panoul stâng - configurare
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(6)

        # Grupa director
        dir_group = QGroupBox("📁 Director Baze de Date")
        dir_group.setObjectName("dirGroup")
        dir_layout = QVBoxLayout(dir_group)

        # Linia pentru director
        dir_input_layout = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_input.setObjectName("dirInput")
        self.dir_input.setText(self.database_directory)
        self.dir_input.setPlaceholderText("Selectați directorul cu fișierele .db...")
        dir_input_layout.addWidget(self.dir_input)

        self.btn_browse = QPushButton("📂 Răsfoiește")
        self.btn_browse.setObjectName("browseButton")
        self.btn_browse.clicked.connect(self._browse_directory)
        dir_input_layout.addWidget(self.btn_browse)

        self.btn_refresh = QPushButton("🔄")
        self.btn_refresh.setObjectName("refreshButton")
        self.btn_refresh.clicked.connect(self._update_file_list)
        self.btn_refresh.setMaximumWidth(35)
        dir_input_layout.addWidget(self.btn_refresh)

        dir_layout.addLayout(dir_input_layout)
        left_layout.addWidget(dir_group)

        # Grupa liste fișiere
        files_group = QGroupBox("📋 Fișiere .db Găsite")
        files_group.setObjectName("filesGroup")
        files_layout = QVBoxLayout(files_group)

        self.file_list = QListWidget()
        self.file_list.setObjectName("fileList")
        self.file_list.setSelectionMode(QListWidget.MultiSelection)
        files_layout.addWidget(self.file_list)

        # Info label
        self.info_label = QLabel("💡 Selectați fișiere sau lăsați gol pentru toate")
        self.info_label.setObjectName("infoLabel")
        self.info_label.setWordWrap(True)
        files_layout.addWidget(self.info_label)

        left_layout.addWidget(files_group)

        # Grupa acțiuni
        actions_group = QGroupBox("⚡ Operații")
        actions_group.setObjectName("actionsGroup")
        actions_layout = QGridLayout(actions_group)
        actions_layout.setSpacing(8)

        self.btn_optimize = QPushButton("🚀 Optimizează Indexuri")
        self.btn_optimize.setObjectName("optimizeButton")
        self.btn_optimize.clicked.connect(self._optimize_indexes)
        actions_layout.addWidget(self.btn_optimize, 0, 0)

        self.btn_list = QPushButton("📊 Listează Indexuri")
        self.btn_list.setObjectName("listButton")
        self.btn_list.clicked.connect(self._list_indexes)
        actions_layout.addWidget(self.btn_list, 0, 1)

        self.btn_maintenance = QPushButton("🧹 Întreținere DB")
        self.btn_maintenance.setObjectName("maintenanceButton")
        self.btn_maintenance.clicked.connect(self._perform_maintenance)
        actions_layout.addWidget(self.btn_maintenance, 1, 0, 1, 2)

        left_layout.addWidget(actions_group)

        # Bara de progres
        progress_group = QGroupBox("📈 Progres Operații")
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

        left_layout.addWidget(progress_group)
        left_layout.addStretch()

        # Panoul drept - jurnal
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        log_group = QGroupBox("📝 Jurnal Operații")
        log_group.setObjectName("logGroup")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setObjectName("logText")
        self.log_text.setPlaceholderText("Activitatea va fi înregistrată aici...")
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)

        # Butoane log
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
        right_layout.addWidget(log_group)

        # Adaugă widget-urile la splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([350, 450])  # Proporția 35:45

        main_layout.addWidget(splitter)

        # Conectăm semnalele
        self.dir_input.textChanged.connect(self._on_directory_changed)

    def _apply_styles(self):
        self.setStyleSheet("""
            QLabel#titleLabel {
                font-size: 14pt;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
                padding: 5px;
            }
            QLabel#infoLabel {
                font-size: 9pt;
                color: #7f8c8d;
                font-style: italic;
                padding: 4px;
            }
            QLabel#progressLabel {
                font-size: 9pt;
                color: #2c3e50;
                font-weight: bold;
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
            QLineEdit#dirInput {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 6px;
                font-size: 9pt;
                background-color: white;
            }
            QLineEdit#dirInput:focus {
                border-color: #3498db;
            }
            QListWidget#fileList {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #ffffff;
                font-size: 9pt;
                selection-background-color: #3498db;
                selection-color: white;
                alternate-background-color: #f8f9fa;
            }
            QListWidget#fileList::item {
                padding: 4px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget#fileList::item:selected {
                background-color: #3498db;
                color: white;
            }
            QPushButton#browseButton {
                background-color: #95a5a6;
                color: white;
                border: 1px solid #7f8c8d;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 9pt;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton#browseButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton#refreshButton {
                background-color: #3498db;
                color: white;
                border: 1px solid #2980b9;
                border-radius: 4px;
                padding: 6px;
                font-size: 9pt;
                font-weight: bold;
            }
            QPushButton#refreshButton:hover {
                background-color: #2980b9;
            }
            QPushButton#optimizeButton {
                background-color: #27ae60;
                color: white;
                border: 1px solid #229954;
                border-radius: 6px;
                padding: 10px;
                font-size: 10pt;
                font-weight: bold;
                min-height: 15px;
            }
            QPushButton#optimizeButton:hover {
                background-color: #229954;
            }
            QPushButton#optimizeButton:disabled {
                background-color: #95a5a6;
                border-color: #7f8c8d;
            }
            QPushButton#listButton {
                background-color: #f39c12;
                color: white;
                border: 1px solid #e67e22;
                border-radius: 6px;
                padding: 10px;
                font-size: 10pt;
                font-weight: bold;
                min-height: 15px;
            }
            QPushButton#listButton:hover {
                background-color: #e67e22;
            }
            QPushButton#listButton:disabled {
                background-color: #95a5a6;
                border-color: #7f8c8d;
            }
            QPushButton#maintenanceButton {
                background-color: #9b59b6;
                color: white;
                border: 1px solid #8e44ad;
                border-radius: 6px;
                padding: 10px;
                font-size: 10pt;
                font-weight: bold;
                min-height: 15px;
            }
            QPushButton#maintenanceButton:hover {
                background-color: #8e44ad;
            }
            QPushButton#maintenanceButton:disabled {
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
                background-color: #27ae60;
                border-radius: 3px;
            }
            QSplitter::handle {
                background-color: #bdc3c7;
                width: 3px;
            }
            QSplitter::handle:hover {
                background-color: #3498db;
            }
        """)

    def _log_message(self, message):
        """Adaugă un mesaj în jurnal"""
        timestamp = QTime.currentTime().toString("hh:mm:ss")
        formatted_message = f"[{timestamp}] {message}"
        self.log_text.append(formatted_message)
        self.last_activity = QTime.currentTime()

    def _watchdog_check(self):
        """Verifică starea aplicației"""
        try:
            QApplication.processEvents()

            # Auto-recovery pentru butoane blocate
            if self.indexer_thread and not self.indexer_thread.isRunning():
                self._reset_ui_state()

        except Exception as e:
            self._log_message(f"❌ Eroare watchdog: {e}")

    def _browse_directory(self):
        """Deschide dialog pentru selectarea directorului"""
        directory = QFileDialog.getExistingDirectory(
            self, "Selectați directorul cu bazele de date", self.dir_input.text()
        )
        if directory:
            self.dir_input.setText(directory)
            self.database_directory = directory
            self._update_file_list()

    def _on_directory_changed(self):
        """Apelat când se schimbă directorul"""
        QTimer.singleShot(500, self._update_file_list)  # Delay pentru a nu actualiza la fiecare caracter

    def _update_file_list(self):
        """Actualizează lista de fișiere .db cu filtrare inteligentă"""
        try:
            directory = self.dir_input.text()
            if not os.path.exists(directory):
                self.file_list.clear()
                self.info_label.setText("❌ Directorul nu există")
                return

            pattern = os.path.join(directory, '*.db')
            all_db_files = glob.glob(pattern)

            # Filtrează bazele de date valide
            valid_db_files = self._filter_valid_databases(all_db_files)

            self.file_list.clear()
            for db_file in sorted(valid_db_files):
                filename = os.path.basename(db_file)
                # Adaugă emojiuri pentru diferitele tipuri
                if 'eur' in filename.lower():
                    icon = "🇪🇺"  # Flag UE pentru bazele EUR
                elif 'chitante' in filename.lower():
                    icon = "📄"  # Chitanțe (excluse automat)
                else:
                    icon = "🗄️"  # Baze normale
                self.file_list.addItem(f"{icon} {filename}")

            count = len(valid_db_files)
            excluded_count = len(all_db_files) - count

            if count > 0:
                info_text = f"📊 Găsite {count} baze procesabile"
                if excluded_count > 0:
                    info_text += f" | Excluse {excluded_count} (chitanțe/temporare)"
                self.info_label.setText(info_text)
                self._log_message(f"🔍 Actualizat: găsite {count} baze valide în {directory}")
                if excluded_count > 0:
                    self._log_message(f"⚠️  Excluse {excluded_count} fișiere (chitanțe sau temporare)")
            else:
                self.info_label.setText("❌ Nu s-au găsit baze de date procesabile")

        except Exception as e:
            self._log_message(f"❌ Eroare actualizare listă: {e}")
            self.info_label.setText(f"❌ Eroare: {e}")

    def _filter_valid_databases(self, all_db_files):
        """Filtrează bazele de date valide pentru procesare"""
        valid_databases = []

        for db_file in all_db_files:
            filename = os.path.basename(db_file).lower()

            # Exclude fișierele temporare/backup
            if any(skip in filename for skip in ['-journal', '-wal', '-shm', '.tmp', '.bak']):
                continue

            # Exclude bazele CHITANTE (nu necesită întreținere)
            if 'chitante' in filename:
                continue

            # Include toate celelalte baze (inclusiv cele EUR)
            valid_databases.append(db_file)

        return valid_databases

    def _get_selected_databases(self):
        """Returnează lista bazelor de date selectate"""
        selected_items = self.file_list.selectedItems()
        directory = self.dir_input.text()

        if not selected_items:
            # Dacă nu e nimic selectat, folosește toate fișierele valide
            pattern = os.path.join(directory, '*.db')
            all_files = glob.glob(pattern)
            return self._filter_valid_databases(all_files)
        else:
            # Folosește doar fișierele selectate
            selected_files = []
            for item in selected_items:
                # Elimină emoji-ul și extrage numele fișierului
                filename = item.text().split(' ', 1)[1] if ' ' in item.text() else item.text()
                filepath = os.path.join(directory, filename)
                selected_files.append(filepath)
            return selected_files

    def _optimize_indexes(self):
        """Pornește optimizarea indexurilor"""
        databases = self._get_selected_databases()
        if not databases:
            self._show_warning("Fără Date", "Nu s-au găsit baze de date pentru procesare!")
            return

        self._log_message(f"🚀 Pornesc optimizarea pentru {len(databases)} baze de date")
        self._log_message("🔄 Includ suport pentru baze EUR clonate")
        self._start_operation("optimize", databases)

    def _list_indexes(self):
        """Pornește listarea indexurilor"""
        databases = self._get_selected_databases()
        if not databases:
            self._show_warning("Fără Date", "Nu s-au găsit baze de date pentru procesare!")
            return

        self._log_message(f"📊 Pornesc listarea indexurilor pentru {len(databases)} baze de date")
        self._start_operation("list", databases)

    def _perform_maintenance(self):
        """Pornește operațiunile de întreținere"""
        databases = self._get_selected_databases()
        if not databases:
            self._show_warning("Fără Date", "Nu s-au găsit baze de date pentru procesare!")
            return

        # Confirmă operația
        reply = QMessageBox.question(
            self, "Confirmare Întreținere",
            f"Efectuați VACUUM și ANALYZE pe {len(databases)} baze de date?\n\n"
            "Această operație poate dura câteva minute pentru baze mari.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self._log_message(f"🧹 Pornesc întreținerea pentru {len(databases)} baze de date")
            self._start_operation("maintenance", databases)

    def _start_operation(self, operation, databases):
        """Pornește o operație în background"""
        if self.indexer_thread and self.indexer_thread.isRunning():
            self._show_warning("Operație în Curs", "O operație este deja în desfășurare!")
            return

        # Creează și configurează thread-ul
        self.indexer_thread = DatabaseIndexer(operation, databases, self)
        self.indexer_thread.progress_updated.connect(self._update_progress)
        self.indexer_thread.operation_completed.connect(self._on_operation_completed)
        self.indexer_thread.log_message.connect(self._log_message)

        # Setează interfața pentru procesare
        self._set_ui_for_processing(True)

        # Pornește thread-ul
        self.indexer_thread.start()

    def _update_progress(self, value, message):
        """Actualizează bara de progres"""
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)
        self.last_activity = QTime.currentTime()

    def _on_operation_completed(self, operation, results):
        """Gestionează finalizarea operației cu detalii complete"""
        self._set_ui_for_processing(False)

        # Analizează rezultatele
        success_list = []
        error_list = []

        for db_key, result in results.items():
            if "succes" in str(result).lower():
                success_list.append(db_key)
            else:
                error_list.append((db_key, str(result)))

        success_count = len(success_list)
        total_count = len(results)

        # Construiește mesajul detaliat
        if operation == "optimize":
            self._show_optimization_results(success_list, error_list, total_count)
            self._log_message(f"🎯 Optimizare completă: {success_count}/{total_count} baze procesate cu succes")

        elif operation == "list":
            self._log_message(f"📋 Listare completă: {total_count} baze analizate")

        elif operation == "maintenance":
            self._show_maintenance_results(success_list, error_list, total_count)
            self._log_message(f"🧹 Întreținere completă: {success_count}/{total_count} baze procesate cu succes")

    def _show_optimization_results(self, success_list, error_list, total_count):
        """Afișează rezultatele optimizării cu detalii complete"""
        message_parts = []

        # Header
        message_parts.append(f"📊 Optimizare Indexuri Finalizată")
        message_parts.append("=" * 50)

        # Statistici generale
        message_parts.append(f"📈 Total procesate: {total_count} baze de date")
        message_parts.append(f"✅ Succese: {len(success_list)}")
        message_parts.append(f"❌ Erori: {len(error_list)}")
        message_parts.append("")

        # Baze procesate cu succes
        if success_list:
            message_parts.append("✅ BAZE OPTIMIZATE CU SUCCES:")
            for db_name in sorted(success_list):
                # Identifică tipul bazei
                if 'eur' in db_name.lower():
                    badge = "🇪🇺 EUR"
                elif any(base in db_name.lower() for base in ['depcred', 'membrii', 'activi']):
                    badge = "🗄️ RON"
                else:
                    badge = "📄"
                message_parts.append(f"   🔹 {db_name} [{badge}]")
            message_parts.append("")

        # Baze cu erori
        if error_list:
            message_parts.append("❌ BAZE CU PROBLEME:")
            for db_name, error in sorted(error_list):
                # Scurtează mesajul de eroare dacă este prea lung
                short_error = error[:60] + "..." if len(error) > 60 else error
                message_parts.append(f"   🔸 {db_name}")
                message_parts.append(f"     Motiv: {short_error}")
            message_parts.append("")

        # Footer
        message_parts.append("💡 Pentru detalii complete consultați jurnalul.")

        # Afișează dialog-ul
        self._show_detailed_dialog(
            "🚀 Rezultate Optimizare",
            "Optimizarea indexurilor s-a finalizat!",
            message_parts
        )

    def _show_maintenance_results(self, success_list, error_list, total_count):
        """Afișează rezultatele întreținerii cu detalii complete"""
        message_parts = []

        # Header
        message_parts.append(f"🧹 Întreținere Baze de Date Finalizată")
        message_parts.append("=" * 50)

        # Statistici generale
        message_parts.append(f"📊 Total procesate: {total_count} baze de date")
        message_parts.append(f"✅ VACUUM + ANALYZE reușite: {len(success_list)}")
        message_parts.append(f"❌ Operațiuni cu erori: {len(error_list)}")
        message_parts.append("")

        # Baze procesate cu succes
        if success_list:
            message_parts.append("✅ BAZE ÎNTREȚINUTE CU SUCCES:")
            for db_name in sorted(success_list):
                if 'eur' in db_name.lower():
                    badge = "🇪🇺 EUR"
                elif any(base in db_name.lower() for base in ['depcred', 'membrii', 'activi']):
                    badge = "🗄️ RON"
                else:
                    badge = "📄"
                message_parts.append(f"   🔹 {db_name} [{badge}] - VACUUM + ANALYZE completate")
            message_parts.append("")

        # Baze cu erori
        if error_list:
            message_parts.append("❌ BAZE CU PROBLEME:")
            for db_name, error in sorted(error_list):
                short_error = error[:60] + "..." if len(error) > 60 else error
                message_parts.append(f"   🔸 {db_name}")
                message_parts.append(f"     Motiv: {short_error}")
            message_parts.append("")

        # Footer
        message_parts.append("💡 Verificați jurnalul pentru informații complete.")

        # Afișează dialog-ul
        self._show_detailed_dialog(
            "🧹 Rezultate Întreținere",
            "Întreținerea bazelor de date s-a finalizat!",
            message_parts
        )

    def _show_detailed_dialog(self, title, summary, message_parts):
        """Afișează un dialog detaliat cu rezultate"""
        full_message = "\n".join(message_parts)

        # Folosește un QMessageBox customizat pentru text mai lung
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(summary)
        msg_box.setDetailedText(full_message)
        msg_box.setIcon(QMessageBox.Information)

        # Setează dimensiunea pentru dialog
        msg_box.setStyleSheet("""
            QMessageBox {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 9pt;
            }
            QMessageBox QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 9pt;
                min-width: 600px;
                min-height: 400px;
            }
        """)

        msg_box.exec_()

    def _cancel_operation(self):
        """Anulează operația curentă"""
        if self.indexer_thread and self.indexer_thread.isRunning():
            self.indexer_thread.cancel_operation()
            self.indexer_thread.wait(3000)  # Așteaptă până la 3 secunde
            if self.indexer_thread.isRunning():
                self.indexer_thread.terminate()

            self._set_ui_for_processing(False)
            self._log_message("🛑 Operație anulată de utilizator")

    def _set_ui_for_processing(self, processing):
        """Setează interfața pentru procesare"""
        # Butoane principale
        self.btn_optimize.setEnabled(not processing)
        self.btn_list.setEnabled(not processing)
        self.btn_maintenance.setEnabled(not processing)
        self.btn_browse.setEnabled(not processing)
        self.btn_refresh.setEnabled(not processing)

        # Controale input
        self.dir_input.setEnabled(not processing)
        self.file_list.setEnabled(not processing)

        # Bara de progres
        self.progress_bar.setVisible(processing)
        self.progress_label.setVisible(processing)
        self.btn_cancel.setVisible(processing)

        if processing:
            self.progress_bar.setValue(0)
            self.progress_label.setText("Inițializare...")

    def _reset_ui_state(self):
        """Resetează starea UI"""
        self._set_ui_for_processing(False)
        self.indexer_thread = None

    def _save_log(self):
        """Salvează jurnalul"""
        if not self.log_text.toPlainText().strip():
            self._show_warning("Jurnal Gol", "Nu există conținut de salvat!")
            return

        timestamp = date.today().strftime("%Y%m%d_%H%M%S")
        default_filename = f"jurnal_indexuri_{timestamp}.txt"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salvează Jurnalul", default_filename, "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Jurnal Manager Indexuri SQLite\n")
                    f.write(f"Generat la: {date.today().strftime('%d/%m/%Y')}\n")
                    f.write(f"Suport baze EUR clonate: DA\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(self.log_text.toPlainText())

                self._show_info("Succes", f"Jurnal salvat!\n\nLocație: {file_path}")
                self._log_message(f"💾 Jurnal salvat: {os.path.basename(file_path)}")

            except Exception as e:
                self._show_error("Eroare", f"Eroare la salvarea jurnalului:\n{e}")

    def _show_warning(self, title, message):
        """Afișează avertisment"""
        QMessageBox.warning(self, title, message)

    def _show_error(self, title, message):
        """Afișează eroare"""
        QMessageBox.critical(self, title, message)

    def _show_info(self, title, message):
        """Afișează informație"""
        QMessageBox.information(self, title, message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OptimizareIndexWidget()
    window.setWindowTitle("🗂️ Manager Indexuri SQLite - CAR (EUR Ready)")
    window.resize(900, 700)
    window.show()
    sys.exit(app.exec_())