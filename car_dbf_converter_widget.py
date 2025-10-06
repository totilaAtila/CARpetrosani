#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAR DBF Converter Widget - Pentru integrare în aplicația principală CAR
Convertește bazele de date ale aplicației CAR din SQLite în DBF cu indexuri
VERSIUNE WIDGET - pentru main_ui.py
"""

import sys
import os
import json
import sqlite3
import shutil
import hashlib
import re
import subprocess
import random
import string
from datetime import datetime, date
from pathlib import Path
from decimal import Decimal, InvalidOperation

# PyQt imports
try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *

    PYQT_AVAILABLE = True
except ImportError:
    try:
        from PyQt6.QtWidgets import *
        from PyQt6.QtCore import *
        from PyQt6.QtGui import *

        PYQT_AVAILABLE = True
    except ImportError:
        PYQT_AVAILABLE = False

# DBF library
try:
    import dbf

    DBF_AVAILABLE = True
except ImportError:
    DBF_AVAILABLE = False


class MatrixOverlay(QWidget):
    """Overlay Matrix TRANSPARENT - doar caractere, fără fundal negru"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # TRANSPARENT - fără fundal negru!
        self.setStyleSheet("background-color: transparent;")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)  # Nu blochează mouse-ul
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # Fundal transparent

        # Lista de coloane cu caractere care cad
        self.columns = []
        self.column_width = 25  # Puțin mai mare pentru vizibilitate
        self.char_height = 25  # Puțin mai mare pentru vizibilitate

        # Timer pentru animație
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)

        # Caractere Matrix authentice
        self.matrix_chars = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜｦﾝ"
        self.regular_chars = string.ascii_uppercase + string.digits + "0123456789"

        self.init_columns()

    def init_columns(self):
        """Inițializează coloanele de caractere."""
        current_width = max(self.width(), 800)
        if current_width > 0:
            num_columns = current_width // self.column_width
            self.columns = []

            for i in range(num_columns):
                column = {
                    'x': i * self.column_width,
                    'chars': [],
                    'speed': random.randint(5, 13),  # Viteza ajustată
                    'next_char_time': random.randint(0, 50),
                    'density': random.uniform(0.2, 0.6)  # Densitate optimă pentru transparență
                }
                self.columns.append(column)

    def start_effect(self):
        """Pornește efectul Matrix transparent."""
        if self.parent():
            parent_size = self.parent().size()
            self.resize(parent_size)
            self.move(0, 0)
            print(f"🎬 Matrix TRANSPARENT overlay: {parent_size.width()}x{parent_size.height()}")

        self.show()
        self.raise_()
        self.init_columns()
        self.timer.start(57)  # Timer ajustat

    def stop_effect(self):
        """Oprește efectul Matrix."""
        self.timer.stop()
        self.hide()

    def update_animation(self):
        """Actualizează animația Matrix transparent."""
        current_height = max(self.height(), 600)

        for column in self.columns:
            # Actualizează caracterele existente
            new_chars = []
            for char in column['chars']:
                char['y'] += column['speed']
                char['age'] += 1

                # PERMITE căderea COMPLETĂ fără restricții!
                if char['y'] < current_height + 200:  # Buffer foarte mare
                    new_chars.append(char)

            column['chars'] = new_chars

            # Adaugă caractere noi
            column['next_char_time'] -= 1
            if column['next_char_time'] <= 0:
                if len(column['chars']) < 30 and random.random() < column['density']:
                    # 80% caractere Matrix, 20% normale
                    char_set = self.matrix_chars if random.random() < 0.8 else self.regular_chars

                    new_char = {
                        'char': random.choice(char_set),
                        'y': -self.char_height * 3,  # Începe de sus
                        'age': 0,
                        'is_matrix': char_set == self.matrix_chars
                    }
                    column['chars'].append(new_char)

                column['next_char_time'] = random.randint(30, 120)

        self.update()

    def paintEvent(self, event):
        """Desenează DOAR caracterele Matrix - FĂRĂ fundal."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Font Matrix optimizat
        font = QFont("Consolas", 18)
        font.setBold(True)
        painter.setFont(font)

        for column in self.columns:
            for char in column['chars']:
                # Gradient de culoare Matrix cu transparență
                age = char['age']

                if age < 2:
                    color = QColor(255, 255, 255, 255)
                elif age < 4:
                    color = QColor(100, 255, 100, 240)
                elif age < 8:
                    alpha = max(180, 255 - (age - 4) * 20)
                    color = QColor(0, 220, 0, alpha)
                elif age < 15:
                    alpha = max(120, 200 - (age - 8) * 15)
                    color = QColor(0, 180, 0, alpha)
                elif age < 25:
                    alpha = max(60, 140 - (age - 15) * 10)
                    color = QColor(0, 140, 0, alpha)
                elif age < 35:
                    alpha = max(20, 80 - (age - 25) * 8)
                    color = QColor(0, 100, 0, alpha)
                else:
                    alpha = max(5, 30 - (age - 35))
                    color = QColor(0, 80, 0, alpha)

                painter.setPen(color)
                painter.drawText(column['x'], char['y'], char['char'])

    def resizeEvent(self, event):
        """Reinițializează la redimensionare."""
        super().resizeEvent(event)
        if self.isVisible():
            self.init_columns()


class WorkerThread(QThread):
    """Thread pentru operații în background."""
    progress = pyqtSignal(str)
    finished_with_result = pyqtSignal(bool, str)

    def __init__(self, operation, work_dir):
        super().__init__()
        self.operation = operation
        self.work_dir = Path(work_dir)
        self.fingerprint = None

    def run(self):
        try:
            if self.operation == "create_fingerprint":
                self.create_fingerprint()
            elif self.operation == "apply_fingerprint":
                self.apply_fingerprint()
        except Exception as e:
            self.finished_with_result.emit(False, f"Eroare: {str(e)}")

    def create_fingerprint(self):
        """Creează amprenta digitală."""
        self.progress.emit("🔬 Creez amprenta digitală...")

        try:
            # Verifică fișierele DBF
            required_dbfs = ["MEMBRII.dbf", "DEPCRED.dbf"]
            missing_dbfs = []

            for dbf_file in required_dbfs:
                if not (self.work_dir / dbf_file).exists():
                    missing_dbfs.append(dbf_file)

            if missing_dbfs:
                self.finished_with_result.emit(False, f"Fișiere DBF lipsă: {', '.join(missing_dbfs)}")
                return

            # Creează amprenta
            fingerprint = self.create_hybrid_fingerprint()

            if fingerprint:
                # Salvează amprenta
                fingerprint_path = self.work_dir / "structure_fingerprint.json"
                with open(fingerprint_path, 'w', encoding='utf-8') as f:
                    json.dump(fingerprint, f, indent=2, ensure_ascii=False)

                self.progress.emit("✅ Amprentă salvată cu succes!")
                self.finished_with_result.emit(True, "Amprenta digitală creată cu succes!")
            else:
                self.finished_with_result.emit(False, "Eroare la crearea amprentei!")

        except Exception as e:
            self.finished_with_result.emit(False, f"Eroare: {str(e)}")

    def apply_fingerprint(self):
        """Aplică amprenta digitală."""
        self.progress.emit("📊 Aplic amprenta și convertesc...")

        try:
            # Încarcă amprenta
            fingerprint_path = self.work_dir / "structure_fingerprint.json"
            if not fingerprint_path.exists():
                self.finished_with_result.emit(False, "Amprenta nu există!")
                return

            with open(fingerprint_path, 'r', encoding='utf-8') as f:
                self.fingerprint = json.load(f)

            # Verifică bazele SQLite
            sqlite_files = ['MEMBRII.db', 'DEPCRED.db']
            existing_dbs = [db for db in sqlite_files if (self.work_dir / db).exists()]

            if not existing_dbs:
                self.finished_with_result.emit(False, "Nu există baze SQLite!")
                return

            # Backup
            self.progress.emit("💾 Creez backup...")
            backup_dir = self.work_dir / "backup_old_files"
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            backup_dir.mkdir()

            # Conversie
            conversions = [('MEMBRII.db', 'MEMBRII'), ('DEPCRED.db', 'DEPCRED')]
            total_records = 0

            for sqlite_file, table_name in conversions:
                if sqlite_file in existing_dbs:
                    self.progress.emit(f"📊 Convertesc {table_name}...")
                    success, records = self.convert_sqlite_to_dbf(sqlite_file, table_name)
                    if success:
                        total_records += records
                        self.progress.emit(f"✅ {table_name}: {records:,} înregistrări")
                    else:
                        self.finished_with_result.emit(False, f"Eroare conversie {table_name}")
                        return

            # Script-uri
            self.progress.emit("📝 Creez script-uri FoxPro...")
            self.create_foxpro_scripts()

            self.finished_with_result.emit(True, f"Conversie completă! {total_records:,} înregistrări procesate.")

        except Exception as e:
            self.finished_with_result.emit(False, f"Eroare: {str(e)}")

    def create_hybrid_fingerprint(self):
        """Creează amprenta hibridă."""
        fingerprint = {
            'version': '3.2_widget',
            'created': datetime.now().isoformat(),
            'tables': {},
            'indexes': {},
            'metadata': {}
        }

        # Structuri manuale
        manual_structures = {
            'MEMBRII': {
                'filename': 'MEMBRII.dbf',
                'detected_codepage': 'cp852',
                'fields': [
                    {'name': 'NR_FISA', 'type': 'N', 'length': 6, 'decimal_count': 0},
                    {'name': 'NUM_PREN', 'type': 'C', 'length': 30, 'decimal_count': 0},
                    {'name': 'CALITATEA', 'type': 'C', 'length': 55, 'decimal_count': 0},
                    {'name': 'DOMICILIUL', 'type': 'C', 'length': 55, 'decimal_count': 0},
                    {'name': 'DATA_INSCR', 'type': 'D', 'length': 8, 'decimal_count': 0},
                ]
            },
            'DEPCRED': {
                'filename': 'DEPCRED.dbf',
                'detected_codepage': 'cp852',
                'fields': [
                    {'name': 'NR_FISA', 'type': 'N', 'length': 6, 'decimal_count': 0},
                    {'name': 'DOBANDA', 'type': 'N', 'length': 10, 'decimal_count': 2},
                    {'name': 'IMPR_DEB', 'type': 'N', 'length': 12, 'decimal_count': 2},
                    {'name': 'IMPR_CRED', 'type': 'N', 'length': 12, 'decimal_count': 2},
                    {'name': 'IMPR_SOLD', 'type': 'N', 'length': 12, 'decimal_count': 2},
                    {'name': 'LUNA', 'type': 'N', 'length': 2, 'decimal_count': 0},
                    {'name': 'ANUL', 'type': 'N', 'length': 4, 'decimal_count': 0},
                    {'name': 'DEP_DEB', 'type': 'N', 'length': 12, 'decimal_count': 2},
                    {'name': 'DEP_CRED', 'type': 'N', 'length': 12, 'decimal_count': 2},
                    {'name': 'DEP_SOLD', 'type': 'N', 'length': 12, 'decimal_count': 2},
                    {'name': 'PRIMA', 'type': 'L', 'length': 1, 'decimal_count': 0},
                ]
            }
        }

        # Procesează structurile
        for table_name, table_info in manual_structures.items():
            # Calculează numărul de înregistrări
            dbf_path = self.work_dir / table_info['filename']
            record_count = 0
            if dbf_path.exists():
                try:
                    with dbf.Table(str(dbf_path)) as table:
                        record_count = len(table)
                except:
                    pass

            dbf_structure = self.build_dbf_structure_string(table_info['fields'])

            fingerprint_entry = {
                'filename': table_info['filename'],
                'record_count': record_count,
                'field_count': len(table_info['fields']),
                'detected_codepage': table_info['detected_codepage'],
                'fields': table_info['fields'],
                'dbf_structure_string': dbf_structure,
                'analysis_quality': 'MANUAL_PERFECT'
            }

            fingerprint['tables'][table_name] = fingerprint_entry
            self.progress.emit(f"✓ {table_name}: {len(table_info['fields'])} câmpuri, {record_count:,} înregistrări")

        # Analizează indexurile
        idx_files = ['FISA.idx', 'NUME.idx', 'LINII.idx']
        for idx_file in idx_files:
            idx_path = self.work_dir / idx_file
            if idx_path.exists():
                analysis = self.analyze_idx_advanced(idx_path)
                if analysis:
                    index_name = idx_path.stem.upper()
                    fingerprint['indexes'][index_name] = analysis

        # Metadata
        fingerprint['metadata'] = {
            'total_tables': len(fingerprint['tables']),
            'total_indexes': len(fingerprint['indexes']),
            'generator_version': '3.2_widget'
        }

        return fingerprint

    def build_dbf_structure_string(self, fields):
        """Construiește string-ul de structură DBF."""
        dbf_parts = []
        for field in fields:
            name = field['name']
            ftype = field['type']
            length = field['length']
            decimals = field['decimal_count']

            if ftype in ['C', 'M']:
                dbf_def = f"{name} {ftype}({length})"
            elif ftype == 'N':
                if decimals > 0:
                    dbf_def = f"{name} {ftype}({length},{decimals})"
                else:
                    dbf_def = f"{name} {ftype}({length})"
            elif ftype == 'D':
                dbf_def = f"{name} {ftype}(8)"
            elif ftype == 'L':
                dbf_def = f"{name} {ftype}(1)"
            else:
                dbf_def = f"{name} {ftype}({length})"

            dbf_parts.append(dbf_def)

        return '; '.join(dbf_parts)

    def analyze_idx_advanced(self, idx_path):
        """Analizează un fișier IDX."""
        try:
            file_size = idx_path.stat().st_size
            index_info = {
                'filename': idx_path.name,
                'file_size': file_size
            }

            filename_lower = idx_path.name.lower()
            if 'fisa' in filename_lower:
                index_info['probable_formula'] = 'NR_FISA'
                index_info['formula_type'] = 'simple_numeric'
            elif 'nume' in filename_lower:
                index_info['probable_formula'] = 'UPPER(NUM_PREN)'
                index_info['formula_type'] = 'upper_string'
            elif 'linii' in filename_lower:
                index_info['probable_formula'] = 'STR(NR_FISA,6)+STR(ANUL,4)+STR(LUNA,2)'
                index_info['formula_type'] = 'composite_string'

            return index_info
        except Exception:
            return None

    def convert_sqlite_to_dbf(self, sqlite_file, table_name):
        """Convertește SQLite la DBF."""
        try:
            if table_name not in self.fingerprint['tables']:
                return False, 0

            table_fingerprint = self.fingerprint['tables'][table_name]

            # Conectare SQLite
            sqlite_path = self.work_dir / sqlite_file
            conn = sqlite3.connect(str(sqlite_path))
            cursor = conn.cursor()

            # Verifică tabela
            table_name_lower = table_name.lower()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            available_tables = [row[0] for row in cursor.fetchall()]

            if table_name_lower not in [t.lower() for t in available_tables]:
                conn.close()
                return False, 0

            # Obține structura
            fields_info = table_fingerprint.get('fields', [])
            detected_codepage = table_fingerprint.get('detected_codepage', 'cp852')

            # Creează DBF-ul
            dbf_filename = self.work_dir / f"{table_name}.dbf"
            if dbf_filename.exists():
                dbf_filename.unlink()

            # Primul câmp
            first_field = fields_info[0]
            first_field_def = self.build_field_definition(first_field)

            # Creez DBF-ul
            table_dbf = dbf.Table(str(dbf_filename), first_field_def, codepage=detected_codepage)
            table_dbf.open(mode=dbf.READ_WRITE)

            # Adaug câmpurile rămase
            for i in range(1, len(fields_info)):
                field = fields_info[i]
                field_def = self.build_field_definition(field)
                table_dbf.add_fields(field_def)

            # Populez tabela
            record_count = self.populate_table_from_sqlite(table_dbf, cursor, table_name_lower, fields_info,
                                                           table_fingerprint)

            table_dbf.close()
            conn.close()

            return True, record_count

        except Exception as e:
            self.progress.emit(f"Eroare conversie {table_name}: {str(e)}")
            return False, 0

    def build_field_definition(self, field):
        """Construiește definiția unui câmp."""
        field_name = field['name']
        field_type = field['type']
        field_length = field['length']
        decimal_count = field.get('decimal_count', 0)

        if field_type == 'C':
            return f"{field_name} C({field_length})"
        elif field_type == 'N':
            return f"{field_name} N({field_length},{decimal_count})"
        elif field_type == 'D':
            return f"{field_name} D"
        elif field_type == 'L':
            return f"{field_name} L"
        else:
            return f"{field_name} C({field_length})"

    def populate_table_from_sqlite(self, table_dbf, cursor, table_name_lower, fields_info, table_fingerprint):
        """Populează tabela DBF cu date din SQLite."""
        try:
            # Obține câmpurile din SQLite
            cursor.execute(f"PRAGMA table_info({table_name_lower})")
            sqlite_fields_info = cursor.fetchall()
            sqlite_field_names = [col[1] for col in sqlite_fields_info]

            # Mapează câmpurile
            dbf_field_names = [field['name'] for field in fields_info]
            field_mapping = []
            for dbf_field in dbf_field_names:
                sqlite_field = None
                for sf in sqlite_field_names:
                    if sf.upper() == dbf_field.upper():
                        sqlite_field = sf
                        break
                field_mapping.append((dbf_field, sqlite_field))

            # Query
            select_fields = [mapping[1] for mapping in field_mapping if mapping[1] is not None]
            if not select_fields:
                return 0

            select_query = f"SELECT {', '.join(select_fields)} FROM {table_name_lower}"
            cursor.execute(select_query)
            rows = cursor.fetchall()

            count = 0
            for row in rows:
                try:
                    converted_row = []
                    select_field_idx = 0

                    for dbf_field_name, sqlite_field_name in field_mapping:
                        field_info = None
                        for f in fields_info:
                            if f['name'] == dbf_field_name:
                                field_info = f
                                break

                        if sqlite_field_name is not None:
                            raw_value = row[select_field_idx]
                            select_field_idx += 1
                        else:
                            raw_value = None

                        converted_value = self.convert_field_value(raw_value, field_info, table_fingerprint)
                        converted_row.append(converted_value)

                    table_dbf.append(tuple(converted_row))
                    count += 1

                except Exception:
                    continue

            return count

        except Exception:
            return 0

    def convert_field_value(self, value, field_info, table_fingerprint):
        """Convertește o valoare conform amprentei."""
        if value is None:
            return self.get_default_value(field_info)

        field_type = field_info['type']
        field_length = field_info['length']
        decimal_count = field_info['decimal_count']

        try:
            if field_type == 'C':
                str_val = str(value)
                return str_val[:field_length]

            elif field_type == 'N':
                if isinstance(value, str):
                    value = value.replace(',', '.').strip()
                    value = re.sub(r'[^\d.-]', '', value)
                    if not value or value == '-' or value == '.':
                        return self.get_default_value(field_info)

                try:
                    if decimal_count > 0:
                        return float(value)
                    else:
                        return int(float(value))
                except:
                    return self.get_default_value(field_info)

            elif field_type == 'L':
                if isinstance(value, str):
                    value_lower = value.lower().strip()
                    return value_lower in ['true', '1', 'yes', 'da', 't', 'y']
                else:
                    return bool(value)

            elif field_type == 'D':
                if isinstance(value, str):
                    date_str = value.strip()
                    date_formats = ['%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d', '%d/%m/%Y']

                    for fmt in date_formats:
                        try:
                            return datetime.strptime(date_str, fmt).date()
                        except ValueError:
                            continue

                    return date.today()
                elif isinstance(value, datetime):
                    return value.date()
                elif isinstance(value, date):
                    return value
                else:
                    return date.today()

            else:
                return str(value)[:field_length]

        except Exception:
            return self.get_default_value(field_info)

    def get_default_value(self, field_info):
        """Returnează valoarea default pentru un tip de câmp."""
        field_type = field_info['type']

        if field_type == 'C':
            return ''
        elif field_type == 'N':
            return 0.0 if field_info['decimal_count'] > 0 else 0
        elif field_type == 'L':
            return False
        elif field_type == 'D':
            return date(1900, 1, 1)
        else:
            return ''

    def create_foxpro_scripts(self):
        """Creează script-urile FoxPro."""
        try:
            main_script = self.work_dir / "CREATE_ALL_INDEXES.PRG"
            main_content = f"""*
* Script pentru crearea indexurilor - CAR DBF Converter
*
SET DEFAULT TO "{str(self.work_dir).replace(chr(92), chr(92) + chr(92))}"

CLEAR
? "========================================================"
? "    CREARE INDEXURI pentru APLICATIA CAR"  
? "========================================================"
? ""

*
* MEMBRII.dbf
*
? "Procesez MEMBRII.dbf..."
USE MEMBRII EXCLUSIVE

IF FILE("FISA.idx")
    DELETE FILE FISA.idx
ENDIF

IF FILE("NUME.idx")
    DELETE FILE NUME.idx
ENDIF

INDEX ON NR_FISA TO FISA COMPACT
? "   V FISA.idx creat"

INDEX ON UPPER(NUM_PREN) TO NUME COMPACT
? "   V NUME.idx creat"

USE
? ""

*
* DEPCRED.dbf  
*
? "Procesez DEPCRED.dbf..."
USE DEPCRED EXCLUSIVE

IF FILE("LINII.idx")
    DELETE FILE LINII.idx
ENDIF

INDEX ON STR(NR_FISA,6)+STR(ANUL,4)+STR(LUNA,2) TO LINII COMPACT
? "   V LINII.idx creat"

USE
? ""

*
* VERIFICARE
*
IF FILE("FISA.idx") AND FILE("NUME.idx") AND FILE("LINII.idx")
    ? "========================================================"
    ? "    SUCCES! Toate indexurile create!"
    ? "    Aplicatia CAR va functiona perfect!"
    ? "========================================================"
ELSE
    ? "    ATENTIE: Unele indexuri lipsesc!"
ENDIF

? ""
WAIT "Apasa orice tasta pentru a inchide..." WINDOW
"""

            instructions = self.work_dir / "INSTRUCTIUNI_FINALE.txt"
            instructions_content = f"""
========================================================
              INSTRUCTIUNI FINALE
           CAR DBF Converter - Versiunea Widget
========================================================

FELICITARI! Conversia a fost finalizata!

URMATORII PASI:

1. Deschide Visual FoxPro 9

2. In Command Window scrie:
   DO CREATE_ALL_INDEXES.PRG

3. Urmareste mesajele si asteapta "SUCCES!"

4. Testeaza aplicatia CAR

========================================================
              FISIERE GENERATE
========================================================

V MEMBRII.dbf     - Tabelul cu membri
V DEPCRED.dbf     - Tabelul cu tranzactii  
V CREATE_ALL_INDEXES.PRG - Script indexuri
V backup_old_files/ - Backup

Data: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
========================================================
"""

            # Salvează cu encoding safe
            with open(main_script, 'w', encoding='cp1252', errors='replace') as f:
                f.write(main_content)

            with open(instructions, 'w', encoding='cp1252', errors='replace') as f:
                f.write(instructions_content)

            return True

        except Exception:
            return False


class CARDBFConverterWidget(QWidget):
    """Widget CAR DBF Converter cu design consistent și simplificat."""

    def __init__(self):
        super().__init__()
        self.work_dir = Path.cwd()
        self.worker = None

        # Watchdog anti-înghețare
        self.last_activity = QTime.currentTime()
        self.watchdog_timer = QTimer(self)
        self.watchdog_timer.timeout.connect(self._watchdog_check)
        self.watchdog_timer.start(3000)

        self.init_ui()
        self.apply_styles()
        self.verify_environment()

    def init_ui(self):
        """Inițializează interfața simplificată."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)

        # Header simplu și compact
        title_label = QLabel("🔄 CAR DBF Converter")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(title_label)

        # Layout principal cu frame-uri (ca în salvari.py)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # === Panoul de Control (Stânga) ===
        control_frame = QFrame()
        control_frame.setObjectName("controlFrame")
        control_layout = QVBoxLayout(control_frame)
        control_layout.setSpacing(15)

        # Grupa director
        dir_group = QGroupBox("📂 Director de Lucru")
        dir_group.setObjectName("dirGroup")
        dir_layout = QVBoxLayout(dir_group)

        self.directory_label = QLabel(str(self.work_dir))
        self.directory_label.setObjectName("directoryLabel")
        self.directory_label.setWordWrap(True)
        dir_layout.addWidget(self.directory_label)

        change_dir_btn = QPushButton("📂 Schimbă Director")
        change_dir_btn.setObjectName("changeDirButton")
        change_dir_btn.clicked.connect(self.change_directory)
        dir_layout.addWidget(change_dir_btn)

        control_layout.addWidget(dir_group)

        # Status fișiere
        files_group = QGroupBox("📋 Status Fișiere")
        files_group.setObjectName("filesGroup")
        files_layout = QVBoxLayout(files_group)

        self.file_status = QLabel()
        self.file_status.setObjectName("fileStatusLabel")
        self.file_status.setWordWrap(True)
        files_layout.addWidget(self.file_status)
        control_layout.addWidget(files_group)

        # Grupa pași
        steps_group = QGroupBox("⚡ Operațiuni Principale")
        steps_group.setObjectName("stepsGroup")
        steps_layout = QGridLayout(steps_group)
        steps_layout.setSpacing(10)

        # Pas 1
        self.step1_btn = QPushButton("1️⃣ Verifică Fișierele")
        self.step1_btn.setObjectName("step1Button")
        self.step1_btn.clicked.connect(self.step1_verify)
        steps_layout.addWidget(self.step1_btn, 0, 0)

        self.step1_status = QLabel("⏳ În așteptare")
        self.step1_status.setObjectName("statusLabel")
        steps_layout.addWidget(self.step1_status, 0, 1)

        # Pas 2
        self.step2_btn = QPushButton("2️⃣ Creează Amprenta")
        self.step2_btn.setObjectName("step2Button")
        self.step2_btn.clicked.connect(self.step2_fingerprint)
        self.step2_btn.setEnabled(False)
        steps_layout.addWidget(self.step2_btn, 1, 0)

        self.step2_status = QLabel("⏳ În așteptare")
        self.step2_status.setObjectName("statusLabel")
        steps_layout.addWidget(self.step2_status, 1, 1)

        # Pas 3
        self.step3_btn = QPushButton("3️⃣ Convertește în DBF")
        self.step3_btn.setObjectName("step3Button")
        self.step3_btn.clicked.connect(self.step3_convert)
        self.step3_btn.setEnabled(False)
        steps_layout.addWidget(self.step3_btn, 2, 0)

        self.step3_status = QLabel("⏳ În așteptare")
        self.step3_status.setObjectName("statusLabel")
        steps_layout.addWidget(self.step3_status, 2, 1)

        # Buton VFP
        self.vfp_btn = QPushButton("🔧 Lansează Visual FoxPro")
        self.vfp_btn.setObjectName("vfpButton")
        self.vfp_btn.clicked.connect(self.launch_visual_foxpro)
        self.vfp_btn.setEnabled(False)
        steps_layout.addWidget(self.vfp_btn, 3, 0)

        self.vfp_status = QLabel("⏳ În așteptare")
        self.vfp_status.setObjectName("statusLabel")
        steps_layout.addWidget(self.vfp_status, 3, 1)

        control_layout.addWidget(steps_group)

        # Acțiuni rapide
        quick_group = QGroupBox("⚡ Acțiuni Rapide")
        quick_group.setObjectName("quickGroup")
        quick_layout = QVBoxLayout(quick_group)

        refresh_btn = QPushButton("🔄 Reîmprospătează Lista")
        refresh_btn.setObjectName("refreshButton")
        refresh_btn.clicked.connect(self.check_files)
        quick_layout.addWidget(refresh_btn)

        control_layout.addWidget(quick_group)
        control_layout.addStretch()

        # === Panoul de Status (Dreapta) ===
        status_frame = QFrame()
        status_frame.setObjectName("statusFrame")
        status_layout = QVBoxLayout(status_frame)
        status_layout.setSpacing(10)

        # Log zone
        log_group = QGroupBox("📝 Jurnalul Operațiilor")
        log_group.setObjectName("logGroup")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setObjectName("logText")
        self.log_text.setPlaceholderText("Activitatea va fi înregistrată aici...")
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)

        # Butoane pentru log
        log_buttons_layout = QHBoxLayout()

        clear_log_btn = QPushButton("🗑️ Curăță Log")
        clear_log_btn.setObjectName("clearLogButton")
        clear_log_btn.clicked.connect(self.clear_log)
        log_buttons_layout.addWidget(clear_log_btn)

        save_log_btn = QPushButton("💾 Salvează Log")
        save_log_btn.setObjectName("saveLogButton")
        save_log_btn.clicked.connect(self.save_log)
        log_buttons_layout.addWidget(save_log_btn)

        log_layout.addLayout(log_buttons_layout)
        status_layout.addWidget(log_group)

        # Adăugăm frame-urile la layout principal
        content_layout.addWidget(control_frame, 4)  # 40% width
        content_layout.addWidget(status_frame, 6)  # 60% width
        main_layout.addLayout(content_layout)

        # Matrix overlay
        self.matrix_overlay = MatrixOverlay(self)
        self.matrix_overlay.hide()

    def apply_styles(self):
        """Aplică stilurile identice cu salvari.py."""
        self.setStyleSheet("""
            QLabel#titleLabel {
                font-size: 16pt;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
            }
            QLabel#directoryLabel {
                font-size: 10pt;
                color: #34495e;
                background-color: #ecf0f1;
                padding: 8px;
                border-radius: 5px;
                border: 1px solid #bdc3c7;
            }
            QLabel#fileStatusLabel {
                font-size: 10pt;
                color: #2c3e50;
                background-color: #e8f4fd;
                padding: 8px;
                border-radius: 5px;
                border: 1px solid #3498db;
            }
            QLabel#statusLabel {
                font-size: 9pt;
                color: #2c3e50;
                font-weight: bold;
                min-width: 120px;
            }
            QFrame#controlFrame, QFrame#statusFrame {
                border: 2px solid #3498db;
                border-radius: 10px;
                background-color: #f8f9fa;
                padding: 10px;
            }
            QGroupBox {
                font-size: 12pt;
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background-color: #f8f9fa;
            }
            QPushButton#step1Button {
                background-color: #f39c12;
                color: white;
                border: 1px solid #e67e22;
                border-radius: 8px;
                padding: 12px;
                font-size: 11pt;
                font-weight: bold;
                min-height: 20px;
            }
            QPushButton#step1Button:hover {
                background-color: #e67e22;
            }
            QPushButton#step1Button:disabled {
                background-color: #95a5a6;
                border-color: #7f8c8d;
            }
            QPushButton#step2Button {
                background-color: #3498db;
                color: white;
                border: 1px solid #2980b9;
                border-radius: 8px;
                padding: 12px;
                font-size: 11pt;
                font-weight: bold;
                min-height: 20px;
            }
            QPushButton#step2Button:hover {
                background-color: #2980b9;
            }
            QPushButton#step2Button:disabled {
                background-color: #95a5a6;
                border-color: #7f8c8d;
            }
            QPushButton#step3Button {
                background-color: #27ae60;
                color: white;
                border: 1px solid #229954;
                border-radius: 8px;
                padding: 12px;
                font-size: 11pt;
                font-weight: bold;
                min-height: 20px;
            }
            QPushButton#step3Button:hover {
                background-color: #229954;
            }
            QPushButton#step3Button:disabled {
                background-color: #95a5a6;
                border-color: #7f8c8d;
            }
            QPushButton#vfpButton {
                background-color: #e74c3c;
                color: white;
                border: 1px solid #c0392b;
                border-radius: 8px;
                padding: 12px;
                font-size: 11pt;
                font-weight: bold;
                min-height: 20px;
            }
            QPushButton#vfpButton:hover {
                background-color: #c0392b;
            }
            QPushButton#vfpButton:disabled {
                background-color: #95a5a6;
                border-color: #7f8c8d;
            }
            QPushButton#changeDirButton, QPushButton#refreshButton {
                background-color: #95a5a6;
                color: white;
                border: 1px solid #7f8c8d;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 10pt;
                font-weight: bold;
                min-height: 15px;
            }
            QPushButton#changeDirButton:hover, QPushButton#refreshButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton#clearLogButton {
                background-color: #e74c3c;
                color: white;
                border: 1px solid #c0392b;
                border-radius: 5px;
                padding: 6px 12px;
                font-size: 9pt;
                font-weight: bold;
            }
            QPushButton#clearLogButton:hover {
                background-color: #c0392b;
            }
            QPushButton#saveLogButton {
                background-color: #27ae60;
                color: white;
                border: 1px solid #229954;
                border-radius: 5px;
                padding: 6px 12px;
                font-size: 9pt;
                font-weight: bold;
            }
            QPushButton#saveLogButton:hover {
                background-color: #229954;
            }
            QTextEdit#logText {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: #ffffff;
                font-family: 'Courier New', monospace;
                font-size: 9pt;
                padding: 8px;
            }
        """)

    def _watchdog_check(self):
        """Verifică starea aplicației."""
        try:
            QApplication.processEvents()
            self.last_activity = QTime.currentTime()
        except Exception as e:
            self.log_message(f"❌ Eroare watchdog: {e}")

    def verify_environment(self):
        """Verifică mediul de lucru."""
        self.log_message("🔍 Verificare mediu...")

        if not PYQT_AVAILABLE:
            self.log_message("❌ PyQt nu este disponibil!")
            return

        if not DBF_AVAILABLE:
            self.log_message("❌ Biblioteca dbf nu este disponibilă!")
            return

        self.log_message("✅ Mediu OK")
        self.check_files()
        self.step1_btn.setEnabled(True)

    def check_files(self):
        """Verifică fișierele."""
        required_files = {
            'DBF': ['MEMBRII.dbf', 'DEPCRED.dbf'],
            'SQLite': ['MEMBRII.db', 'DEPCRED.db']
        }

        status_text = ""
        all_ok = True

        for category, files in required_files.items():
            status_text += f"<b>{category}:</b> "
            category_files = []

            for file in files:
                if (self.work_dir / file).exists():
                    size = (self.work_dir / file).stat().st_size
                    category_files.append(f"✅ {file} ({size // 1024}KB)")
                else:
                    category_files.append(f"❌ {file}")
                    if category == 'DBF':
                        all_ok = False

            status_text += ", ".join(category_files) + "<br/>"

        self.file_status.setText(status_text)
        self.log_message(f"📋 Status fișiere actualizat: {'✅ Toate fișierele OK' if all_ok else '❌ Lipsuri detectate'}")
        return all_ok

    def change_directory(self):
        """Schimbă directorul."""
        new_dir = QFileDialog.getExistingDirectory(self, "Director CAR", str(self.work_dir))
        if new_dir:
            self.work_dir = Path(new_dir)
            self.directory_label.setText(str(self.work_dir))
            self.log_message(f"📂 Director schimbat: {self.work_dir}")
            self.check_files()

    def step1_verify(self):
        """Pasul 1: Verificare."""
        self.log_message("🔍 PASUL 1: Verificare fișiere...")
        self.step1_status.setText("⏳ Verific")

        if self.check_files():
            self.step1_status.setText("✅ Complet")
            self.step1_btn.setEnabled(False)
            self.step2_btn.setEnabled(True)
            self.log_message("✅ Verificare completă - toate fișierele DBF găsite!")
        else:
            self.step1_status.setText("❌ Eroare")
            QMessageBox.warning(self, "Fișiere lipsă", "Nu am găsit fișierele DBF necesare pentru amprentă!")

    def step2_fingerprint(self):
        """Pasul 2: Amprentă."""
        self.log_message("🔬 PASUL 2: Creez amprenta digitală...")
        self.step2_status.setText("⏳ Creez")
        self.step2_btn.setEnabled(False)

        self.worker = WorkerThread("create_fingerprint", self.work_dir)
        self.worker.progress.connect(self.log_message)
        self.worker.finished_with_result.connect(self.on_fingerprint_done)

        # Matrix effect
        self.matrix_overlay.start_effect()
        self.worker.start()

    def on_fingerprint_done(self, success, message):
        """Callback amprentă."""
        self.matrix_overlay.stop_effect()

        if success:
            self.step2_status.setText("✅ Complet")
            self.step3_btn.setEnabled(True)
            self.log_message("✅ Amprentă digitală creată cu succes!")
        else:
            self.step2_status.setText("❌ Eroare")
            self.step2_btn.setEnabled(True)
            self.log_message(f"❌ Eroare la crearea amprentei: {message}")

    def step3_convert(self):
        """Pasul 3: Conversie."""
        reply = QMessageBox.question(self, "Confirmare",
                                     "Convertesc bazele SQLite în DBF?\n\nAceasta va suprascrie fișierele DBF existente.",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.log_message("📊 PASUL 3: Conversie SQLite → DBF...")
            self.step3_status.setText("⏳ Convertesc")
            self.step3_btn.setEnabled(False)

            self.worker = WorkerThread("apply_fingerprint", self.work_dir)
            self.worker.progress.connect(self.log_message)
            self.worker.finished_with_result.connect(self.on_conversion_done)

            self.matrix_overlay.start_effect()
            self.worker.start()

    def on_conversion_done(self, success, message):
        """Callback conversie."""
        self.matrix_overlay.stop_effect()

        if success:
            self.step3_status.setText("✅ Complet")
            self.vfp_btn.setEnabled(True)
            self.log_message("✅ Conversie completă cu succes!")
            QMessageBox.information(self, "Succes!", f"{message}\n\nPoți acum lansa Visual FoxPro pentru indexuri!")
        else:
            self.step3_status.setText("❌ Eroare")
            self.step3_btn.setEnabled(True)
            self.log_message(f"❌ Eroare la conversie: {message}")

    def launch_visual_foxpro(self):
        """Lansează Visual FoxPro."""
        self.log_message("🔧 Lansez Visual FoxPro...")
        self.vfp_status.setText("⏳ Lansez")

        script_file = self.work_dir / "CREATE_ALL_INDEXES.PRG"
        if not script_file.exists():
            self.vfp_status.setText("❌ Script lipsă")
            self.log_message("❌ Script CREATE_ALL_INDEXES.PRG nu există!")
            return

        # Căi VFP
        vfp_paths = [
            r"C:\Program Files (x86)\Microsoft Visual FoxPro 9\VFP9.EXE",
            r"C:\Program Files\Microsoft Visual FoxPro 9\VFP9.EXE",
            r"C:\VFP9\VFP9.EXE",
        ]

        vfp_exe = None
        for path in vfp_paths:
            if Path(path).exists():
                vfp_exe = path
                break

        if not vfp_exe:
            manual_path, _ = QFileDialog.getOpenFileName(self, "Selectează VFP9.EXE", "C:\\", "Executabile (*.exe)")
            if manual_path:
                vfp_exe = manual_path
            else:
                self.vfp_status.setText("❌ Nu găsesc VFP")
                return

        try:
            # Lansează VFP
            vfp_script = self.work_dir / "VFP_LAUNCHER.PRG"
            with open(vfp_script, 'w', encoding='cp1252', errors='replace') as f:
                f.write(f'''SET DEFAULT TO "{str(self.work_dir).replace(chr(92), chr(92) + chr(92))}"
DO CREATE_ALL_INDEXES.PRG
WAIT "Finalizat! Apasa orice tasta..." WINDOW
QUIT''')

            subprocess.Popen([vfp_exe, str(vfp_script)], cwd=str(self.work_dir))

            self.vfp_status.setText("✅ Lansat")
            self.log_message("✅ Visual FoxPro lansat cu succes!")

        except Exception as e:
            self.vfp_status.setText("❌ Eroare")
            self.log_message(f"❌ Eroare lansare VFP: {e}")

    def log_message(self, message):
        """Adaugă mesaj în log."""
        timestamp = QTime.currentTime().toString("hh:mm:ss")
        formatted_message = f"[{timestamp}] {message}"
        self.log_text.append(formatted_message)
        self.last_activity = QTime.currentTime()

        # Auto-scroll
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)

    def clear_log(self):
        """Curăță log-ul."""
        self.log_text.clear()
        self.log_message("🗑️ Jurnal curățat")

    def save_log(self):
        """Salvează log-ul."""
        if not self.log_text.toPlainText().strip():
            QMessageBox.warning(self, "Jurnal Gol", "Nu există conținut de salvat!")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"jurnal_car_dbf_converter_{timestamp}.txt"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salvează Jurnalul", default_filename, "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Jurnal CAR DBF Converter\n")
                    f.write(f"Generat la: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(self.log_text.toPlainText())

                QMessageBox.information(self, "Succes", f"Jurnal salvat!\n\nLocație: {file_path}")
                self.log_message(f"💾 Jurnal salvat: {os.path.basename(file_path)}")

            except Exception as e:
                QMessageBox.critical(self, "Eroare", f"Eroare la salvarea jurnalului:\n{e}")

    def resizeEvent(self, event):
        """Redimensionează overlay-ul Matrix."""
        super().resizeEvent(event)
        if hasattr(self, 'matrix_overlay'):
            self.matrix_overlay.resize(event.size())
            if self.matrix_overlay.isVisible():
                self.matrix_overlay.init_columns()


if __name__ == "__main__":
    # Pentru testare standalone
    app = QApplication(sys.argv)
    window = CARDBFConverterWidget()

    # Wrapper pentru test
    test_window = QMainWindow()
    test_window.setCentralWidget(window)
    test_window.setWindowTitle("CAR DBF Converter - Test Widget")
    test_window.resize(900, 600)
    test_window.show()

    sys.exit(app.exec_())