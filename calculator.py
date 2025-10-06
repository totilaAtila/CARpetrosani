from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLineEdit, QLabel, QFrame, QFileDialog,
    QMessageBox, QTextEdit, QSizePolicy
)
from PyQt5.QtGui import QIcon, QFont, QKeySequence
from PyQt5.QtCore import Qt, QTimer
import math
import subprocess
import sys
import os
from datetime import datetime


class CalculatorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_input = ""
        self.result = 0
        self.operation = ""
        self.stored_number = None
        self.calculation_history = ""
        self.last_operation = None
        self.last_number = None
        self.just_calculated = False
        self._init_ui()
        self._apply_styles()
        self._setup_keyboard_shortcuts()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Header cu titlu și ora
        header_layout = QHBoxLayout()
        title_label = QLabel("Calculator C.A.R.")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignLeft)

        self.time_label = QLabel()
        self.time_label.setObjectName("timeLabel")
        self.time_label.setAlignment(Qt.AlignRight)

        # Timer pentru actualizarea orei
        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        self.update_time()

        header_layout.addWidget(title_label)
        header_layout.addWidget(self.time_label)
        main_layout.addLayout(header_layout)

        # Container pentru layout-ul principal
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)

        # Calculator container (70% width)
        calculator_frame = QFrame()
        calculator_frame.setObjectName("calculatorFrame")
        calculator_layout = QVBoxLayout(calculator_frame)
        calculator_layout.setContentsMargins(10, 10, 10, 10)
        calculator_layout.setSpacing(10)

        # Display cu două niveluri
        display_container = QWidget()
        display_layout = QVBoxLayout(display_container)
        display_layout.setContentsMargins(0, 0, 0, 0)
        display_layout.setSpacing(2)

        # History display (top, text mic)
        self.history_display = QLineEdit()
        self.history_display.setObjectName("historyDisplay")
        self.history_display.setAlignment(Qt.AlignRight)
        self.history_display.setReadOnly(True)
        self.history_display.setFixedHeight(30)
        self.history_display.setPlaceholderText("Istoric operații...")
        display_layout.addWidget(self.history_display)

        # Main display (bottom, text mare)
        self.main_display = QLineEdit()
        self.main_display.setObjectName("mainDisplay")
        self.main_display.setAlignment(Qt.AlignRight)
        self.main_display.setReadOnly(True)
        self.main_display.setFixedHeight(60)
        self.main_display.setText("0")
        display_layout.addWidget(self.main_display)

        calculator_layout.addWidget(display_container)

        # Grid pentru butoane
        buttons_grid = QGridLayout()
        buttons_grid.setSpacing(5)

        # Definirea butoanelor cu poziții specifice
        button_config = [
            # Row 0
            [('C', 0, 0), ('CE', 0, 1), ('⌫', 0, 2), ('/', 0, 3), ('√', 0, 4)],
            # Row 1
            [('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('*', 1, 3), ('x²', 1, 4)],
            # Row 2
            [('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3), ('1/x', 2, 4)],
            # Row 3
            [('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3), ('%', 3, 4)],
            # Row 4
            [('±', 4, 0), ('0', 4, 1), ('.', 4, 2), ('=', 4, 3, 1, 2)]  # = span 2 columns
        ]

        # Crearea butoanelor
        for row_config in button_config:
            for btn_config in row_config:
                text = btn_config[0]
                row = btn_config[1]
                col = btn_config[2]
                row_span = btn_config[3] if len(btn_config) > 3 else 1
                col_span = btn_config[4] if len(btn_config) > 4 else 1

                button = QPushButton(text)
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button.setObjectName("calcButton")
                button.setFixedSize(50, 40)
                button.clicked.connect(self.on_button_click)

                # Stiluri speciale pentru anumite butoane
                if text in ['=']:
                    button.setObjectName("equalsButton")
                elif text in ['C', 'CE', '⌫']:
                    button.setObjectName("clearButton")
                elif text in ['+', '-', '*', '/', '%']:
                    button.setObjectName("operatorButton")
                elif text in ['√', 'x²', '1/x']:
                    button.setObjectName("functionButton")

                buttons_grid.addWidget(button, row, col, row_span, col_span)

        calculator_layout.addLayout(buttons_grid)

        # Notes container (30% width)
        notes_frame = QFrame()
        notes_frame.setObjectName("notesFrame")
        notes_layout = QVBoxLayout(notes_frame)
        notes_layout.setContentsMargins(10, 10, 10, 10)
        notes_layout.setSpacing(10)

        notes_label = QLabel("📝 Istoric Calcule:")
        notes_label.setObjectName("notesLabel")
        notes_layout.addWidget(notes_label)

        self.notes_edit = QTextEdit()
        self.notes_edit.setObjectName("notesEdit")
        self.notes_edit.setPlaceholderText("Toate calculele vor fi salvate aici automat...")
        notes_layout.addWidget(self.notes_edit)

        # Butoane pentru gestionarea istoricului
        buttons_layout = QHBoxLayout()

        clear_btn = QPushButton("🗑️ Curăță")
        clear_btn.setObjectName("clearNotesButton")
        clear_btn.clicked.connect(self.clear_notes)

        save_btn = QPushButton("💾 Salvez")
        save_btn.setObjectName("saveButton")
        save_btn.clicked.connect(self.save_notes)

        buttons_layout.addWidget(clear_btn)
        buttons_layout.addWidget(save_btn)
        notes_layout.addLayout(buttons_layout)

        # Adăugarea frame-urilor la layout-ul principal
        content_layout.addWidget(calculator_frame, 7)  # 70% width
        content_layout.addWidget(notes_frame, 3)  # 30% width
        main_layout.addLayout(content_layout)

    def _apply_styles(self):
        self.setStyleSheet("""
            QLabel#titleLabel {
                font-size: 16pt;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
            }
            QLabel#timeLabel {
                font-size: 12pt;
                color: #7f8c8d;
                margin-bottom: 5px;
            }
            QFrame#calculatorFrame, QFrame#notesFrame {
                border: 2px solid #3498db;
                border-radius: 8px;
                background-color: #ecf0f1;
                padding: 5px;
            }
            QLabel#notesLabel {
                font-weight: bold;
                color: #2c3e50;
                font-size: 12pt;
                margin-bottom: 5px;
            }
            QTextEdit#notesEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
                background-color: #ffffff;
                min-height: 150px;
            }
            QPushButton#calcButton {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14pt;
                font-weight: bold;
                color: #2c3e50;
            }
            QPushButton#calcButton:hover {
                background-color: #d5dbdb;
                border-color: #95a5a6;
            }
            QPushButton#calcButton:pressed {
                background-color: #bdc3c7;
            }
            QPushButton#equalsButton {
                background-color: #3498db;
                color: white;
                border: 1px solid #2980b9;
                font-size: 16pt;
                font-weight: bold;
            }
            QPushButton#equalsButton:hover {
                background-color: #2980b9;
            }
            QPushButton#operatorButton {
                background-color: #e74c3c;
                color: white;
                border: 1px solid #c0392b;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton#operatorButton:hover {
                background-color: #c0392b;
            }
            QPushButton#functionButton {
                background-color: #f39c12;
                color: white;
                border: 1px solid #e67e22;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton#functionButton:hover {
                background-color: #e67e22;
            }
            QPushButton#clearButton {
                background-color: #95a5a6;
                color: white;
                border: 1px solid #7f8c8d;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton#clearButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton#saveButton, QPushButton#clearNotesButton {
                background-color: #27ae60;
                color: white;
                border: 1px solid #229954;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 10pt;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton#saveButton:hover, QPushButton#clearNotesButton:hover {
                background-color: #229954;
            }
            QPushButton#clearNotesButton {
                background-color: #e74c3c;
                border-color: #c0392b;
            }
            QPushButton#clearNotesButton:hover {
                background-color: #c0392b;
            }
            QLineEdit#historyDisplay {
                border: 2px solid #3498db;
                border-bottom: 1px solid #3498db;
                border-radius: 8px 8px 0 0;
                padding: 5px 10px;
                background-color: #ffffff;
                font-size: 12px;
                color: #7f8c8d;
            }
            QLineEdit#mainDisplay {
                border: 2px solid #3498db;
                border-top: 1px solid #3498db;
                border-radius: 0 0 8px 8px;
                padding: 10px;
                background-color: #ffffff;
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)

    def _setup_keyboard_shortcuts(self):
        """Configurează scurtăturile de tastatură"""
        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        """Gestionează input-ul de la tastatură"""
        key = event.key()
        text = event.text()

        if text in '0123456789.':
            self.handle_number_input(text)
        elif text in '+-*/':
            self.handle_operator_input(text)
        elif key == Qt.Key_Return or key == Qt.Key_Enter or key == Qt.Key_Equal:
            self.handle_equals()
        elif key == Qt.Key_Escape or text.upper() == 'C':
            self.handle_clear()
        elif key == Qt.Key_Backspace:
            self.handle_backspace()
        elif key == Qt.Key_Delete:
            self.handle_clear_entry()
        elif text == '%':
            self.handle_percent()

        super().keyPressEvent(event)

    def update_time(self):
        """Actualizează afișajul cu ora curentă"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(f"🕒 {current_time}")

    def on_button_click(self):
        sender = self.sender()
        text = sender.text()

        if text in '0123456789.':
            self.handle_number_input(text)
        elif text in '+-*/':
            self.handle_operator_input(text)
        elif text == '=':
            self.handle_equals()
        elif text == 'C':
            self.handle_clear()
        elif text == 'CE':
            self.handle_clear_entry()
        elif text == '⌫':
            self.handle_backspace()
        elif text == '√':
            self.handle_sqrt()
        elif text == 'x²':
            self.handle_square()
        elif text == '1/x':
            self.handle_reciprocal()
        elif text == '±':
            self.handle_sign_change()
        elif text == '%':
            self.handle_percent()

    def handle_number_input(self, digit):
        """Gestionează input-ul numerelor"""
        if self.just_calculated:
            self.current_input = ""
            self.just_calculated = False

        if digit == '.' and '.' in self.current_input:
            return  # Nu permite puncte duble

        if self.current_input == "0" and digit != '.':
            self.current_input = digit
        else:
            self.current_input += digit

        self.main_display.setText(self.current_input)

    def handle_operator_input(self, op):
        """Gestionează input-ul operatorilor"""
        if self.current_input:
            if self.stored_number is not None and not self.just_calculated:
                self.calculate()
            else:
                self.stored_number = float(self.current_input)

            self.operation = op
            self.calculation_history = f"{self.format_number(self.stored_number)} {op}"
            self.history_display.setText(self.calculation_history)
            self.current_input = ""
        elif self.stored_number is not None:
            # Schimbă operatorul dacă nu s-a introdus un număr nou
            self.operation = op
            self.calculation_history = f"{self.format_number(self.stored_number)} {op}"
            self.history_display.setText(self.calculation_history)

    def handle_equals(self):
        """Gestionează operația de egalitate"""
        if self.current_input and self.stored_number is not None and self.operation:
            self.last_number = float(self.current_input)
            self.last_operation = self.operation
            self.calculate()
        elif self.last_operation and self.last_number is not None:
            # Repetă ultima operație
            self.stored_number = float(self.current_input) if self.current_input else float(self.main_display.text())
            self.operation = self.last_operation
            self.current_input = str(self.last_number)
            self.calculate()

    def handle_clear(self):
        """Curăță toate datele"""
        self.current_input = ""
        self.stored_number = None
        self.operation = None
        self.calculation_history = ""
        self.last_operation = None
        self.last_number = None
        self.just_calculated = False
        self.main_display.setText("0")
        self.history_display.setText("")

    def handle_clear_entry(self):
        """Curăță doar input-ul curent"""
        self.current_input = ""
        self.main_display.setText("0")

    def handle_backspace(self):
        """Șterge ultima cifră"""
        if self.current_input:
            self.current_input = self.current_input[:-1]
            if not self.current_input:
                self.main_display.setText("0")
            else:
                self.main_display.setText(self.current_input)

    def handle_sqrt(self):
        """Calculează radicalul"""
        try:
            current_value = float(self.current_input) if self.current_input else float(self.main_display.text())
            if current_value >= 0:
                result = math.sqrt(current_value)
                self.current_input = self.format_number(result)
                self.main_display.setText(self.current_input)
                self.add_to_history(f"√({self.format_number(current_value)}) = {self.current_input}")
                self.history_display.setText(f"√({self.format_number(current_value)})")
                self.just_calculated = True
            else:
                self.show_error("Nu se poate calcula radicalul unui număr negativ!")
        except:
            self.show_error("Valoare invalidă pentru radical!")

    def handle_square(self):
        """Calculează pătratul"""
        try:
            current_value = float(self.current_input) if self.current_input else float(self.main_display.text())
            result = current_value ** 2
            self.current_input = self.format_number(result)
            self.main_display.setText(self.current_input)
            self.add_to_history(f"({self.format_number(current_value)})² = {self.current_input}")
            self.history_display.setText(f"({self.format_number(current_value)})²")
            self.just_calculated = True
        except:
            self.show_error("Valoare invalidă pentru ridicare la pătrat!")

    def handle_reciprocal(self):
        """Calculează reciproca (1/x)"""
        try:
            current_value = float(self.current_input) if self.current_input else float(self.main_display.text())
            if current_value != 0:
                result = 1 / current_value
                self.current_input = self.format_number(result)
                self.main_display.setText(self.current_input)
                self.add_to_history(f"1/({self.format_number(current_value)}) = {self.current_input}")
                self.history_display.setText(f"1/({self.format_number(current_value)})")
                self.just_calculated = True
            else:
                self.show_error("Nu se poate împărți la zero!")
        except:
            self.show_error("Valoare invalidă pentru reciprocă!")

    def handle_sign_change(self):
        """Schimbă semnul numărului"""
        if self.current_input and self.current_input != "0":
            if self.current_input.startswith('-'):
                self.current_input = self.current_input[1:]
            else:
                self.current_input = '-' + self.current_input
            self.main_display.setText(self.current_input)
        elif not self.current_input:
            current_value = float(self.main_display.text())
            self.current_input = self.format_number(-current_value)
            self.main_display.setText(self.current_input)

    def handle_percent(self):
        """Calculează procentul"""
        try:
            current_value = float(self.current_input) if self.current_input else float(self.main_display.text())
            if self.stored_number is not None:
                # Calculează procentul din numărul stocat
                result = (current_value / 100) * self.stored_number
                self.current_input = self.format_number(result)
                self.main_display.setText(self.current_input)
                self.add_to_history(
                    f"{self.format_number(current_value)}% din {self.format_number(self.stored_number)} = {self.current_input}")
            else:
                # Convertește la procent simplu
                result = current_value / 100
                self.current_input = self.format_number(result)
                self.main_display.setText(self.current_input)
                self.add_to_history(f"{self.format_number(current_value)}% = {self.current_input}")
            self.just_calculated = True
        except:
            self.show_error("Valoare invalidă pentru procent!")

    def calculate(self):
        """Efectuează calculul principal"""
        try:
            second_number = float(self.current_input)
            result = 0

            if self.operation == '+':
                result = self.stored_number + second_number
            elif self.operation == '-':
                result = self.stored_number - second_number
            elif self.operation == '*':
                result = self.stored_number * second_number
            elif self.operation == '/':
                if second_number != 0:
                    result = self.stored_number / second_number
                else:
                    self.show_error("Nu se poate împărți la zero!")
                    return

            result_str = self.format_number(result)
            self.main_display.setText(result_str)

            full_calculation = f"{self.calculation_history} {self.format_number(second_number)} = {result_str}"
            self.add_to_history(full_calculation)
            self.history_display.setText(full_calculation)

            # Resetare pentru următoarea operație
            self.stored_number = result
            self.current_input = result_str
            self.just_calculated = True

        except Exception as e:
            self.show_error(f"Eroare la calcul: {str(e)}")

    def format_number(self, number):
        """Formatează numărul pentru afișare"""
        if number == int(number):
            return str(int(number))
        else:
            # Elimină zerourile finale pentru numerele cu zecimale
            formatted = f"{number:.10f}".rstrip('0').rstrip('.')
            return formatted

    def add_to_history(self, calculation):
        """Adaugă calculul la istoric"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.notes_edit.append(f"[{timestamp}] {calculation}")

    def clear_notes(self):
        """Curăță istoricul"""
        reply = QMessageBox.question(
            self,
            "Confirmare",
            "Sunteți sigur că doriți să ștergeți tot istoricul?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.notes_edit.clear()

    def show_error(self, message):
        """Afișează mesaj de eroare"""
        QMessageBox.warning(self, "Eroare", message)
        self.handle_clear()

    def save_notes(self):
        """Salvează istoricul într-un fișier"""
        notes = self.notes_edit.toPlainText()
        if not notes:
            QMessageBox.warning(self, "Avertisment", "Nu există conținut de salvat!")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"istoric_calcule_{timestamp}.txt"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvează Istoric Calcule",
            default_filename,
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Istoric Calcule - Calculator C.A.R.\n")
                    f.write(f"Generat la: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(notes)
                QMessageBox.information(self, "Succes", f"Istoricul a fost salvat cu succes!\n\nLocație: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Eroare", f"Eroare la salvarea fișierului:\n{e}")


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = CalculatorWidget()
    window.setWindowTitle("Calculator C.A.R. - Test Individual")
    window.resize(600, 500)
    window.show()
    sys.exit(app.exec_())