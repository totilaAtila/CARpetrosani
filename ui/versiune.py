from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class Versiune(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Meniu Versiune"))
