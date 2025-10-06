# utils.py
import sys
import traceback
import logging
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot, QThreadPool
from PyQt5.QtCore import Qt, QMetaObject, Q_ARG
from PyQt5.QtWidgets import QMessageBox, QDialogButtonBox, QVBoxLayout, QLabel, QDialog, QApplication
from PyQt5.QtGui import QFont, QPixmap
# Adăugare în utils.py
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import Qt, QTimer
from dialog_styles import get_dialog_stylesheet


class ProgressDialog:
    """
    Clasa utilitară pentru gestionarea dialogurilor de progres.
    Folosită pentru a monitoriza operațiile de lungă durată.
    """

    def __init__(self, parent=None, titlu="Progres", mesaj="În lucru...", min_val=0, max_val=100):
        """
        Inițializează un dialog de progres.

        Args:
            parent: Widget-ul părinte
            titlu: Titlul dialogului
            mesaj: Mesajul afișat în dialog
            min_val: Valoarea minimă a barei de progres
            max_val: Valoarea maximă a barei de progres
        """
        self.dialog = QProgressDialog(mesaj, "Anulează", min_val, max_val, parent)
        self.dialog.setWindowTitle(titlu)
        self.dialog.setWindowModality(Qt.WindowModal)
        self.dialog.setMinimumDuration(500)  # Apare după 500ms
        self.dialog.setAutoClose(True)
        self.dialog.setAutoReset(True)

        # Conectăm semnalul canceled pentru a putea gestiona anularea
        self.dialog.canceled.connect(self.on_canceled)

        # Indicator pentru anulare
        self.anulat = False

    def on_canceled(self):
        """Gestionează evenimentul de anulare."""
        self.anulat = True

    def este_anulat(self):
        """Verifică dacă utilizatorul a anulat operația."""
        return self.anulat

    def seteaza_valoare(self, val):
        """
        Setează valoarea curentă a progresului.

        Args:
            val: Valoarea curentă (între min_val și max_val)
        """
        self.dialog.setValue(val)
        QApplication.processEvents()  # Asigură actualizarea UI în timpul procesării

    def seteaza_text(self, text):
        """
        Actualizează textul afișat în dialog.

        Args:
            text: Noul text care va fi afișat
        """
        self.dialog.setLabelText(text)
        QApplication.processEvents()

    def seteaza_interval(self, min_val, max_val):
        """
        Modifică intervalul de valori al barei de progres.

        Args:
            min_val: Noua valoare minimă
            max_val: Noua valoare maximă
        """
        self.dialog.setRange(min_val, max_val)

    def inchide(self):
        """Închide dialogul de progres."""
        self.dialog.close()


class StyledMessageBox(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Folosește stylesheet-ul centralizat complet
        self.setStyleSheet(get_dialog_stylesheet())


def afiseaza_warning(mesaj, parent=None):
    """ Afișează un mesaj de avertisment cu butoane stilizate. """
    if QApplication.instance():
        msg_box = StyledMessageBox(parent)
        msg_box.setWindowTitle("Atenție")
        msg_box.setText(mesaj)
        msg_box.setIcon(QMessageBox.Warning)
        return msg_box.exec_()
    else:
        print(f"WARNING: {mesaj}")
        return QMessageBox.Ok

def afiseaza_eroare(mesaj, parent=None):
    """ Afișează un mesaj de eroare cu butoane stilizate. """
    if QApplication.instance():
        msg_box = StyledMessageBox(parent)
        msg_box.setWindowTitle("Eroare")
        msg_box.setText(mesaj)
        msg_box.setIcon(QMessageBox.Critical)
        return msg_box.exec_()
    else:
        print(f"ERROR: {mesaj}")
        return QMessageBox.Ok

def afiseaza_info(mesaj, parent=None):
    """ Afișează un mesaj informativ cu butoane stilizate. """
    if QApplication.instance():
        msg_box = StyledMessageBox(parent)
        msg_box.setWindowTitle("Informație")
        msg_box.setText(mesaj)
        msg_box.setIcon(QMessageBox.Information)
        return msg_box.exec_()
    else:
        print(f"INFO: {mesaj}")
        return QMessageBox.Ok

def afiseaza_intrebare(mesaj, titlu="Confirmare", parent=None, buton_default=QMessageBox.No):
    """
    Afișează un dialog de confirmare cu butoane stilizate Yes/No.
    Returnează True dacă utilizatorul a apăsat Yes, False altfel.
    """
    if QApplication.instance():
        msg_box = StyledMessageBox(parent)
        msg_box.setWindowTitle(titlu)
        msg_box.setText(mesaj)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(buton_default)
        return msg_box.exec_() == QMessageBox.Yes
    else:
        print(f"QUESTION [{titlu}]: {mesaj}")
        # În mod non-UI, returnăm implicit False (No)
        return False

class QTextEditLogger(logging.Handler):
    def __init__(self, text_edit_widget):
        super().__init__()
        self.widget = text_edit_widget

    def emit(self, record):
        msg = self.format(record)
        # apel thread-safe pentru QTextEdit.append()
        QMetaObject.invokeMethod(
            self.widget,
            "append",
            Qt.QueuedConnection,
            Q_ARG(str, msg)
        )


def attach_qt_logger(text_edit_widget):
    """
    Atașează un handler de logging care va redirecta
    toate mesajele către QTextEdit-ul dat.
    Poți apela asta o singură dată, după crearea widget-ului.
    """
    logger = logging.getLogger()
    # evităm ataşarea duplicată
    if any(isinstance(h, QTextEditLogger) for h in logger.handlers):
        return

    handler = QTextEditLogger(text_edit_widget)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s"
    ))
    logger.addHandler(handler)


class WorkerSignals(QObject):
    """ Definește semnalele standard pentru un worker. """
    finished = pyqtSignal()  # Task terminat (fără erori)
    error = pyqtSignal(tuple)  # A apărut o eroare (tip, valoare, traceback)
    result = pyqtSignal(object)  # Rezultatul funcției (dacă returnează ceva)
    progress = pyqtSignal(str)  # Mesaj de progres (string)


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.setAutoDelete(True)
        self.kwargs['progress_callback'] = self.signals.progress.emit

    @pyqtSlot()
    def run(self):
        import datetime
        func_name = getattr(self.fn, '__name__', repr(self.fn))
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]

        logging.info(f"[{timestamp}] === WORKER START for: {func_name} ===")

        try:
            logging.info(f"[{timestamp}] WORKER: Executing function...")
            result = self.fn(*self.args, **self.kwargs)
            logging.info(f"[{timestamp}] WORKER: Function executed successfully")

            if result is not None:
                logging.info(f"[{timestamp}] WORKER: Emitting result signal")
                self.signals.result.emit(result)
                logging.info(f"[{timestamp}] WORKER: Result signal emitted")

        except Exception as e:
            timestamp_err = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
            logging.error(f"[{timestamp_err}] WORKER ERROR during execution of {func_name}: {e}", exc_info=True)
            exctype, value = sys.exc_info()[:2]
            logging.info(f"[{timestamp_err}] WORKER: Emitting error signal")
            self.signals.error.emit((exctype, value, traceback.format_exc()))
            logging.info(f"[{timestamp_err}] WORKER: Error signal emitted")
        else:
            timestamp_fin = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
            logging.info(f"[{timestamp_fin}] WORKER: Emitting finished signal")
            self.signals.finished.emit()
            logging.info(f"[{timestamp_fin}] WORKER: Finished signal emitted")
        finally:
            timestamp_final = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
            logging.info(f"[{timestamp_final}] === WORKER END for: {func_name} ===")

    @pyqtSlot()
    def run(self):
        """ Execută funcția țintă și emite semnale corespunzătoare. """
        func_name = getattr(self.fn, '__name__', repr(self.fn))
        logging.info(f"Worker started for: {func_name}")
        try:
            result = self.fn(*self.args, **self.kwargs)
            # Emitem rezultatul doar dacă funcția returnează ceva non-None
            # (pentru a nu aglomera dacă funcția nu returnează explicit)
            if result is not None:
                self.signals.result.emit(result)
        except Exception as e:
            logging.error(f"Error during worker execution of {func_name}: {e}", exc_info=True)
            exctype, value = sys.exc_info()[:2]
            # Emitem tuplul de eroare complet pentru debugging
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            # Emitem 'finished' doar dacă nu a apărut nicio excepție
            self.signals.finished.emit()
        finally:
            # Acest semnal este emis indiferent dacă a fost eroare sau nu,
            # util pentru curățenie generală, dar finished/error sunt mai specifice.
            # Poate fi eliminat dacă finished/error acoperă toate nevoile.
            logging.info(f"Worker finished execution for: {func_name}")
            # Nu emitem finished aici dacă a fost eroare


def run_task_in_background(parent_widget, function, *args, on_finish=None, on_error=None, on_progress=None):
    """ Pornește o funcție în background folosind QThreadPool global. """
    # Verificăm dacă sloturile sunt apelabile (funcții/metode)
    if on_finish and not callable(on_finish):
        logging.error(f"run_task_in_background: on_finish nu este apelabil.")
        return
    if on_error and not callable(on_error):
        logging.error(f"run_task_in_background: on_error nu este apelabil.")
        return
    if on_progress and not callable(on_progress):
        logging.error(f"run_task_in_background: on_progress nu este apelabil.")
        return

    # Creăm worker-ul
    worker = Worker(function, *args)
    worker.setAutoDelete(True)  # Se șterge automat după rulare

    # Conectăm semnalele worker-ului la sloturile primite
    if on_finish:
        worker.signals.finished.connect(on_finish)
    if on_error:
        worker.signals.error.connect(on_error)
    if on_progress:
        worker.signals.progress.connect(on_progress)

    # Pornim worker-ul pe pool-ul global
    try:
        QThreadPool.globalInstance().start(worker)
        func_name = getattr(function, '__name__', repr(function))
        logging.info(f"Task '{func_name}' trimis către QThreadPool.")
    except Exception as e_pool:
        logging.error(f"Eroare la pornirea task-ului în QThreadPool: {e_pool}", exc_info=True)
        # Încercăm să afișăm eroarea în UI dacă e posibil
        if parent_widget and hasattr(parent_widget, 'isVisible') and parent_widget.isVisible():
            try:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(parent_widget, "Eroare Threading", f"Nu s-a putut porni procesul"
                                                                        f" în background:\n{e_pool}")
            except ImportError:
                print("FATAL: QMessageBox nu a putut fi importat pentru a afișa eroarea de threading.")
