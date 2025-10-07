from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class Vizualizari(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Meniu Vizualizări"))
