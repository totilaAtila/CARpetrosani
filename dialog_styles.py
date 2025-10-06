# dialog_styles.py
"""
Stiluri centralizate pentru toate dialogurile aplicației CAR Petroșani.
Versiune îmbunătățită cu consistență completă fundal-text.

CARACTERISTICI:
- Fundal dialog: #e8f1ff (albastru deschis)
- Text principal: #2c3e50 (gri închis) - contrast optim
- Fundal text: #ffffff (alb curat) cu chenar bleu
- Butoane: #cce5ff cu efecte hover și pressed
- Padding generos pentru lizibilitate maximă
- Toate culorile sunt definite explicit pentru consistență

MODIFICĂRI FAȚĂ DE VERSIUNEA ANTERIOARĂ:
- Adăugată culoarea textului (#2c3e50) pentru toate containerele principale
- Clarificat fundalul pentru QMessageBox QLabel (transparent, se integrează cu fundalul dialogului)
- Eliminată ambiguitatea prin specificarea explicită a tuturor culorilor
"""

GLOBAL_DIALOG_STYLESHEET = """
/* ==================== QMessageBox ==================== */
QMessageBox {
    background-color: #e8f1ff;
    color: #2c3e50;
    font-family: Arial;
    font-size: 10pt;
    min-width: 420px;
}

/* Zona de text principală - FUNDAL ALB CURAT */
QMessageBox QLabel#qt_msgbox_label {
    background-color: #ffffff;
    color: #2c3e50;
    padding: 14px 18px;
    border: 1px solid #b3d1ff;
    border-radius: 6px;
    font-size: 10pt;
    margin: 4px;
}

/* Label-uri secundare (titluri, informații suplimentare) */
QMessageBox QLabel {
    background-color: transparent;
    color: #2c3e50;
    padding: 6px;
}

/* Butoane - stil validari.py */
QMessageBox QPushButton {
    background-color: #cce5ff;
    color: #2c3e50;
    border: 1px solid #3399ff;
    padding: 8px 16px;
    border-radius: 6px;
    min-width: 80px;
    font-weight: bold;
}

QMessageBox QPushButton:hover {
    background-color: #b3daff;
    border-color: #2680d9;
}

QMessageBox QPushButton:pressed {
    background-color: #99ccff;
    border-color: #1a66b3;
}

QMessageBox QPushButton:focus {
    outline: none;
    border: 2px solid #0056b3;
}

QMessageBox QPushButton:default {
    border: 2px solid #0056b3;
    background-color: #b3daff;
}

/* ==================== QDialog ==================== */
QDialog {
    background-color: #e8f1ff;
    color: #2c3e50;
    font-family: Arial;
    font-size: 10pt;
}

/* Text din dialoguri custom */
QDialog QLabel {
    background-color: #ffffff;
    color: #2c3e50;
    padding: 12px 16px;
    border: 1px solid #b3d1ff;
    border-radius: 6px;
}

QDialog QPushButton {
    background-color: #cce5ff;
    color: #2c3e50;
    border: 1px solid #3399ff;
    padding: 8px 16px;
    border-radius: 6px;
    min-width: 80px;
    font-weight: bold;
}

QDialog QPushButton:hover {
    background-color: #b3daff;
}

QDialog QPushButton:pressed {
    background-color: #99ccff;
}

QDialog QPushButton:focus {
    outline: none;
    border: 2px solid #0056b3;
}

QDialog QPushButton:disabled {
    background-color: #cccccc;
    color: #666666;
    border-color: #999999;
}

/* ==================== QInputDialog ==================== */
QInputDialog {
    background-color: #e8f1ff;
    color: #2c3e50;
    font-family: Arial;
    font-size: 10pt;
}

QInputDialog QLabel {
    background-color: #ffffff;
    color: #2c3e50;
    padding: 10px 14px;
    border: 1px solid #b3d1ff;
    border-radius: 4px;
    margin: 4px;
}

QInputDialog QLineEdit,
QInputDialog QSpinBox,
QInputDialog QComboBox {
    background-color: #ffffff;
    color: #2c3e50;
    border: 2px solid #3399ff;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 10pt;
}

QInputDialog QLineEdit:focus,
QInputDialog QSpinBox:focus,
QInputDialog QComboBox:focus {
    border-color: #0056b3;
}

QInputDialog QPushButton {
    background-color: #cce5ff;
    color: #2c3e50;
    border: 1px solid #3399ff;
    padding: 8px 16px;
    border-radius: 6px;
    min-width: 80px;
    font-weight: bold;
}

QInputDialog QPushButton:hover {
    background-color: #b3daff;
}

/* ==================== QFileDialog ==================== */
QFileDialog {
    background-color: #f8f9fa;
    color: #2c3e50;
}

QFileDialog QPushButton {
    background-color: #cce5ff;
    color: #2c3e50;
    border: 1px solid #3399ff;
    padding: 6px 12px;
    border-radius: 6px;
    min-width: 70px;
    font-weight: bold;
}

QFileDialog QPushButton:hover {
    background-color: #b3daff;
}

QFileDialog QPushButton:pressed {
    background-color: #99ccff;
}

/* ==================== QDialogButtonBox ==================== */
QDialogButtonBox QPushButton {
    background-color: #cce5ff;
    color: #2c3e50;
    border: 1px solid #3399ff;
    padding: 8px 16px;
    border-radius: 6px;
    min-width: 80px;
    font-weight: bold;
}

QDialogButtonBox QPushButton:hover {
    background-color: #b3daff;
}

QDialogButtonBox QPushButton:pressed {
    background-color: #99ccff;
}
"""


def apply_global_dialog_styles(app):
    """
    Aplică stilurile centralizate pentru dialoguri cu consistență completă fundal-text.

    CARACTERISTICI VERSIUNE ÎMBUNĂTĂȚITĂ:
    - Fundal text alb curat cu chenar bleu (#ffffff)
    - Culoare text definită explicit (#2c3e50) pentru toate elementele
    - Butoane stilizate cu hover și pressed (#cce5ff → #b3daff → #99ccff)
    - Padding generos pentru lizibilitate maximă
    - Consistență vizuală 100% în toată aplicația
    - Eliminarea ambiguității prin specificare explicită

    Args:
        app: Instanța QApplication

    Returns:
        bool: True dacă aplicarea a avut succes
    """
    try:
        current_stylesheet = app.styleSheet()

        if current_stylesheet:
            app.setStyleSheet(current_stylesheet + "\n\n" + GLOBAL_DIALOG_STYLESHEET)
        else:
            app.setStyleSheet(GLOBAL_DIALOG_STYLESHEET)

        print("✅ Stiluri globale aplicate: consistență completă fundal-text")
        return True

    except Exception as e:
        print(f"❌ Eroare aplicare stiluri: {e}")
        return False


def get_dialog_stylesheet():
    """Returnează stylesheet-ul pentru utilizare directă."""
    return GLOBAL_DIALOG_STYLESHEET