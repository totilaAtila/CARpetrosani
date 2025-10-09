# -*- coding: utf-8 -*-
"""
C.A.R. Petroșani - Interface cu Teme Plastic și Preview Real-Time + Conversie RON->EUR
Versiunea completă cu monkey patching condițional pentru comutare dinamică RON/EUR
VERSIUNEA ALL-IN-ONE READY FOR PRODUCTION cu Protecție Scriere
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QStackedWidget, QLabel, QSplitter, QShortcut, QFrame, QApplication,
    QGraphicsDropShadowEffect, QProgressDialog, QDialog, QListWidget,
    QMessageBox, QToolTip, QListWidgetItem
)
from PyQt5.QtGui import (
    QFont, QIcon, QKeySequence, QPainter, QBrush, QColor, QPen,
    QLinearGradient, QRadialGradient, QPixmap
)
from PyQt5.QtCore import (
    Qt, QTimer, QDateTime, QPropertyAnimation, QEasingCurve, QRect,
    QSequentialAnimationGroup, QParallelAnimationGroup, QSize, QPoint
)

# --- Importuri statice pentru modulele de bază ---
from ui.statistici import StatisticiWidget
from ui.adaugare_membru import AdaugareMembruWidget
from ui.listari import ListariWidget
from ui.listariEUR import ListariEURWidget
from ui.verificare_fise import VerificareFiseWidget
from ui.sume_lunare import SumeLunareWidget
from ui.lichidare_membru import LichidareMembruWidget
from ui.stergere_membru import StergereMembruWidget
from ui.vizualizare_lunara import VizualizareLunaraWidget
from ui.vizualizare_trimestriala import VizualizareTrimestrialaWidget
from ui.vizualizare_anuala import VizualizareAnualaWidget
from ui.generare_luna import GenerareLunaNouaWidget
from ui.afisare_membri_lichidati import MembriLichidatiWidget
from ui.despre import DespreWidget
from ui.calculator import CalculatorWidget
from ui.salvari import OperatiuniSalvareWidget
from ui.optimizare_index import OptimizareIndexWidget
from ui.dividende import DividendeWidget
from ui.imprumuturi_noi import ImprumuturiNoiWidget


# --- Importuri condiționate pentru module opționale ---
try:
    from car_dbf_converter_widget import CARDBFConverterWidget

    CAR_DBF_AVAILABLE = True
except ImportError:
    print("⚠️ CAR DBF Converter widget nu este disponibil")
    CAR_DBF_AVAILABLE = False

try:
    from conversie_widget import ConversieWidget

    CONVERSIE_WIDGET_AVAILABLE = True
except ImportError:
    print("⚠️ Conversie Widget nu este disponibil")
    CONVERSIE_WIDGET_AVAILABLE = False

# --- Importuri standard Python ---
import sqlite3
import subprocess
import sys
import json
import os
import importlib
from pathlib import Path
import inspect

# --- Importuri logica de business separată ---
from currency_logic import CurrencyLogic


class ConversieStatusChecker:
    """Verifică statusul conversiei RON->EUR"""

    def __init__(self):
        self.base_path = Path(__file__).resolve().parent if not getattr(sys, 'frozen', False) else Path(
            sys.executable).parent
        self.config_path = self.base_path / "dual_currency.json"

    def is_conversion_applied(self):
        """Verifică dacă conversia a fost deja aplicată"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('conversie_aplicata', False)
            return False
        except Exception as e:
            print(f"Eroare verificare status conversie: {e}")
            return False

    def has_eur_databases(self):
        """Verifică dacă există bazele de date EUR"""
        eur_dbs = ["DEPCREDEUR.db", "MEMBRIIEUR.db", "activiEUR.db", "INACTIVIEUR.db", "LICHIDATIEUR.db"]
        return any((self.base_path / db).exists() for db in eur_dbs)


class ThemeManager:
    """Manager pentru temele de culori cu efecte glass/transparente și teme plastic"""

    def __init__(self):
        # Fișierul pentru salvarea preferințelor
        if getattr(sys, 'frozen', False):
            self.settings_file = os.path.join(os.path.dirname(sys.executable), "car_settings.json")
        else:
            self.settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "car_settings.json")

        self.current_theme = 0

        # Lista de teme - structura păstrată pentru extensibilitate viitoare
        self.themes = [
            # ===== TEME CLASICE ORIGINALE (0-1) =====
            {
                "name": "Glass Verde Original",
                #"category": "clasic",
                "menu_gradient": ("stop:0 rgba(213, 244, 230, 200), stop:1 rgba(208, 240, 192, 220)",
                                  "stop:0 rgba(232, 248, 237, 180), stop:1 rgba(226, 255, 226, 200)"),
                "menu_active": (
                    "stop:0 rgba(46, 204, 113, 220), stop:1 rgba(39, 174, 96, 240)", "rgba(34, 153, 84, 255)"),
                "menu_border": "rgba(160, 192, 144, 180)",
                "menu_text": "#1e3a1e",
                "submenu_gradient": ("stop:0 rgba(93, 173, 226, 200), stop:1 rgba(52, 152, 219, 220)",
                                     "stop:0 rgba(133, 193, 233, 180), stop:1 rgba(93, 173, 226, 200)"),
                "submenu_active": ("stop:0 rgba(46, 204, 113, 220), stop:1 rgba(39, 174, 96, 240)",
                                   "rgba(34, 153, 84, 255)"),
                "submenu_border": "rgba(41, 128, 185, 180)",
                "submenu_text": "white",
                "background": "stop:0 rgba(248, 249, 250, 240), stop:1 rgba(233, 236, 239, 220)"
            },
            {
                "name": "Glass Albastru Ocean",
                #"category": "clasic",
                "menu_gradient": ("stop:0 rgba(206, 236, 255, 200), stop:1 rgba(173, 216, 245, 220)",
                                  "stop:0 rgba(225, 245, 255, 180), stop:1 rgba(196, 226, 255, 200)"),
                "menu_active": (
                    "stop:0 rgba(52, 152, 219, 220), stop:1 rgba(41, 128, 185, 240)", "rgba(31, 108, 165, 255)"),
                "menu_border": "rgba(144, 192, 220, 180)",
                "menu_text": "#1e2a3a",
                "submenu_gradient": ("stop:0 rgba(93, 173, 226, 200), stop:1 rgba(52, 152, 219, 220)",
                                     "stop:0 rgba(133, 193, 233, 180), stop:1 rgba(93, 173, 226, 200)"),
                "submenu_active": (
                    "stop:0 rgba(52, 152, 219, 220), stop:1 rgba(41, 128, 185, 240)", "rgba(31, 108, 165, 255)"),
                "submenu_border": "rgba(41, 128, 185, 180)",
                "submenu_text": "white",
                "background": "stop:0 rgba(248, 252, 255, 240), stop:1 rgba(233, 246, 255, 220)"
            },
            {
                "name": "Glass Violet Elegant",
                #"category": "clasic",
                "menu_gradient": ("stop:0 rgba(230, 220, 255, 200), stop:1 rgba(210, 195, 245, 220)",
                                  "stop:0 rgba(240, 235, 255, 180), stop:1 rgba(225, 210, 255, 200)"),
                "menu_active": (
                    "stop:0 rgba(155, 89, 182, 220), stop:1 rgba(142, 68, 173, 240)", "rgba(125, 60, 152, 255)"),
                "menu_border": "rgba(180, 160, 220, 180)",
                "menu_text": "#3a1e3a",
                "submenu_gradient": ("stop:0 rgba(175, 122, 197, 200), stop:1 rgba(155, 89, 182, 220)",
                                     "stop:0 rgba(195, 155, 211, 180), stop:1 rgba(175, 122, 197, 200)"),
                "submenu_active": (
                    "stop:0 rgba(155, 89, 182, 220), stop:1 rgba(142, 68, 173, 240)", "rgba(125, 60, 152, 255)"),
                "submenu_border": "rgba(142, 68, 173, 180)",
                "submenu_text": "white",
                "background": "stop:0 rgba(252, 248, 255, 240), stop:1 rgba(246, 233, 255, 220)"
            },
            {
                "name": "Glass Portocaliu Sunset",
                #"category": "clasic",
                "menu_gradient": ("stop:0 rgba(255, 230, 200, 200), stop:1 rgba(245, 210, 175, 220)",
                                  "stop:0 rgba(255, 240, 220, 180), stop:1 rgba(255, 225, 195, 200)"),
                "menu_active": (
                    "stop:0 rgba(243, 156, 18, 220), stop:1 rgba(230, 126, 34, 240)", "rgba(211, 84, 0, 255)"),
                "menu_border": "rgba(220, 180, 140, 180)",
                "menu_text": "#3a2e1e",
                "submenu_gradient": ("stop:0 rgba(250, 177, 160, 200), stop:1 rgba(243, 156, 18, 220)",
                                     "stop:0 rgba(255, 195, 180, 180), stop:1 rgba(250, 177, 160, 200)"),
                "submenu_active": (
                    "stop:0 rgba(243, 156, 18, 220), stop:1 rgba(230, 126, 34, 240)", "rgba(211, 84, 0, 255)"),
                "submenu_border": "rgba(230, 126, 34, 180)",
                "submenu_text": "white",
                "background": "stop:0 rgba(255, 248, 240, 240), stop:1 rgba(255, 233, 210, 220)"
            },
            {
                "name": "Glass Roz Delicat",
                "category": "clasic",
                "menu_gradient": ("stop:0 rgba(255, 220, 240, 200), stop:1 rgba(245, 195, 220, 220)",
                                  "stop:0 rgba(255, 235, 245, 180), stop:1 rgba(255, 210, 235, 200)"),
                "menu_active": (
                    "stop:0 rgba(231, 76, 60, 220), stop:1 rgba(192, 57, 43, 240)", "rgba(169, 50, 38, 255)"),
                "menu_border": "rgba(220, 160, 190, 180)",
                "menu_text": "#3a1e2e",
                "submenu_gradient": ("stop:0 rgba(240, 140, 180, 200), stop:1 rgba(231, 76, 60, 220)",
                                     "stop:0 rgba(250, 170, 200, 180), stop:1 rgba(240, 140, 180, 200)"),
                "submenu_active": (
                    "stop:0 rgba(231, 76, 60, 220), stop:1 rgba(192, 57, 43, 240)", "rgba(169, 50, 38, 255)"),
                "submenu_border": "rgba(192, 57, 43, 180)",
                "submenu_text": "white",
                "background": "stop:0 rgba(255, 248, 252, 240), stop:1 rgba(255, 233, 245, 220)"
            },
            {
                "name": "Glass Turcoaz Marin",
                #"category": "clasic",
                "menu_gradient": ("stop:0 rgba(200, 250, 245, 200), stop:1 rgba(175, 230, 220, 220)",
                                  "stop:0 rgba(220, 255, 250, 180), stop:1 rgba(195, 245, 235, 200)"),
                "menu_active": (
                    "stop:0 rgba(26, 188, 156, 220), stop:1 rgba(22, 160, 133, 240)", "rgba(17, 141, 120, 255)"),
                "menu_border": "rgba(140, 200, 190, 180)",
                "menu_text": "#1e3a35",
                "submenu_gradient": ("stop:0 rgba(120, 220, 200, 200), stop:1 rgba(26, 188, 156, 220)",
                                     "stop:0 rgba(155, 235, 215, 180), stop:1 rgba(120, 220, 200, 200)"),
                "submenu_active": (
                    "stop:0 rgba(26, 188, 156, 220), stop:1 rgba(22, 160, 133, 240)", "rgba(17, 141, 120, 255)"),
                "submenu_border": "rgba(22, 160, 133, 180)",
                "submenu_text": "white",
                "background": "stop:0 rgba(248, 255, 253, 240), stop:1 rgba(233, 250, 245, 220)"
            },

            # ===== TEME PROFESIONALE PENTRU BIROU (6-15) =====
            {
                "name": "💼 Corporate Blue",
                #"category": "profesional",
                "menu_gradient": ("stop:0 rgba(240, 248, 255, 220), stop:1 rgba(220, 235, 250, 240)",
                                  "stop:0 rgba(230, 240, 250, 200), stop:1 rgba(210, 225, 245, 220)"),
                "menu_active": (
                    "stop:0 rgba(41, 98, 155, 240), stop:1 rgba(32, 80, 130, 260)", "rgba(25, 65, 110, 280)"),
                "menu_border": "rgba(180, 200, 220, 180)",
                "menu_text": "#2c3e50",
                "submenu_gradient": ("stop:0 rgba(220, 235, 250, 220), stop:1 rgba(200, 220, 240, 240)",
                                     "stop:0 rgba(235, 245, 255, 200), stop:1 rgba(220, 235, 250, 220)"),
                "submenu_active": (
                    "stop:0 rgba(41, 98, 155, 240), stop:1 rgba(32, 80, 130, 260)", "rgba(25, 65, 110, 280)"),
                "submenu_border": "rgba(160, 180, 200, 180)",
                "submenu_text": "#2c3e50",
                "background": "stop:0 rgba(248, 252, 255, 250), stop:1 rgba(240, 248, 255, 230)"
            },
            {
                "name": "💼 Black Professional",
                #"category": "profesional",
                "menu_gradient": (
                    "stop:0 rgba(34,34,34,220), stop:1 rgba(0,0,0,240)",
                    "stop:0 rgba(25,25,25,200), stop:1 rgba(0,0,0,220)"
                ),
                "menu_active": (
                    "stop:0 rgba(0,0,0,255), stop:1 rgba(30,30,30,255)",
                    "rgba(10,10,10,255)"
                ),
                "menu_border": "rgba(80,80,80,180)",
                "menu_text": "#FFFFFF",
                "submenu_gradient": (
                    "stop:0 rgba(50,50,50,220), stop:1 rgba(20,20,20,240)",
                    "stop:0 rgba(40,40,40,200), stop:1 rgba(0,0,0,220)"
                ),
                "submenu_active": (
                    "stop:0 rgba(0,0,0,255), stop:1 rgba(30,30,30,255)",
                    "rgba(10,10,10,255)"
                ),
                "submenu_border": "rgba(80,80,80,180)",
                "submenu_text": "#FFFFFF",
                "background": "stop:0 rgba(20,20,20,240), stop:1 rgba(0,0,0,230)"
            },
            {
                "name": "💼 Dark Gray Professional",
                #"category": "profesional",
                "menu_gradient": (
                    "stop:0 rgba(66,66,66,220), stop:1 rgba(45,45,45,240)",
                    "stop:0 rgba(55,55,55,200), stop:1 rgba(30,30,30,220)"
                ),
                "menu_active": (
                    "stop:0 rgba(30,30,30,240), stop:1 rgba(10,10,10,255)",
                    "rgba(20,20,20,255)"
                ),
                "menu_border": "rgba(100,100,100,180)",
                "menu_text": "#DDDDDD",
                "submenu_gradient": (
                    "stop:0 rgba(80,80,80,220), stop:1 rgba(60,60,60,240)",
                    "stop:0 rgba(70,70,70,200), stop:1 rgba(40,40,40,220)"
                ),
                "submenu_active": (
                    "stop:0 rgba(30,30,30,240), stop:1 rgba(10,10,10,255)",
                    "rgba(20,20,20,255)"
                ),
                "submenu_border": "rgba(100,100,100,180)",
                "submenu_text": "#DDDDDD",
                "background": "stop:0 rgba(40,40,40,240), stop:1 rgba(20,20,20,230)"
            },
            {
                "name": "💼 Charcoal Professional",
                #"category": "profesional",
                "menu_gradient": (
                    "stop:0 rgba(60,60,60,220), stop:1 rgba(30,30,30,240)",
                    "stop:0 rgba(50,50,50,200), stop:1 rgba(20,20,20,220)"
                ),
                "menu_active": (
                    "stop:0 rgba(20,20,20,255), stop:1 rgba(0,0,0,255)",
                    "rgba(15,15,15,255)"
                ),
                "menu_border": "rgba(90,90,90,180)",
                "menu_text": "#F0F0F0",
                "submenu_gradient": (
                    "stop:0 rgba(70,70,70,220), stop:1 rgba(40,40,40,240)",
                    "stop:0 rgba(60,60,60,200), stop:1 rgba(30,30,30,220)"
                ),
                "submenu_active": (
                    "stop:0 rgba(20,20,20,255), stop:1 rgba(0,0,0,255)",
                    "rgba(15,15,15,255)"
                ),
                "submenu_border": "rgba(90,90,90,180)",
                "submenu_text": "#F0F0F0",
                "background": "stop:0 rgba(30,30,30,240), stop:1 rgba(10,10,10,230)"
            },
            {
                "name": "💼 Slate Professional",
                #"category": "profesional",
                "menu_gradient": (
                    "stop:0 rgba(80,80,90,220), stop:1 rgba(55,55,65,240)",
                    "stop:0 rgba(70,70,80,200), stop:1 rgba(45,45,55,220)"
                ),
                "menu_active": (
                    "stop:0 rgba(40,40,50,255), stop:1 rgba(20,20,30,255)",
                    "rgba(25,25,35,255)"
                ),
                "menu_border": "rgba(110,110,120,180)",
                "menu_text": "#E0E0E0",
                "submenu_gradient": (
                    "stop:0 rgba(90,90,100,220), stop:1 rgba(65,65,75,240)",
                    "stop:0 rgba(80,80,90,200), stop:1 rgba(55,55,65,220)"
                ),
                "submenu_active": (
                    "stop:0 rgba(40,40,50,255), stop:1 rgba(20,20,30,255)",
                    "rgba(25,25,35,255)"
                ),
                "submenu_border": "rgba(110,110,120,180)",
                "submenu_text": "#E0E0E0",
                "background": "stop:0 rgba(45,45,55,240), stop:1 rgba(25,25,35,230)"
            },
            {
                "name": "💼 Executive Gray",
                #"category": "profesional",
                "menu_gradient": ("stop:0 rgba(245, 245, 245, 220), stop:1 rgba(225, 225, 225, 240)",
                                  "stop:0 rgba(235, 235, 235, 200), stop:1 rgba(215, 215, 215, 220)"),
                "menu_active": ("stop:0 rgba(70, 70, 70, 240), stop:1 rgba(50, 50, 50, 260)", "rgba(35, 35, 35, 280)"),
                "menu_border": "rgba(180, 180, 180, 180)",
                "menu_text": "#34495e",
                "submenu_gradient": ("stop:0 rgba(225, 225, 225, 220), stop:1 rgba(205, 205, 205, 240)",
                                     "stop:0 rgba(240, 240, 240, 200), stop:1 rgba(225, 225, 225, 220)"),
                "submenu_active": (
                    "stop:0 rgba(70, 70, 70, 240), stop:1 rgba(50, 50, 50, 260)", "rgba(35, 35, 35, 280)"),
                "submenu_border": "rgba(160, 160, 160, 180)",
                "submenu_text": "#34495e",
                "background": "stop:0 rgba(250, 250, 250, 250), stop:1 rgba(245, 245, 245, 230)"
            },
            {
                "name": "💼 Sage Professional",
                "#category": "profesional",
                "menu_gradient": ("stop:0 rgba(240, 250, 245, 220), stop:1 rgba(220, 235, 225, 240)",
                                  "stop:0 rgba(230, 245, 235, 200), stop:1 rgba(210, 230, 220, 220)"),
                "menu_active": (
                    "stop:0 rgba(95, 158, 160, 240), stop:1 rgba(70, 130, 135, 260)", "rgba(55, 110, 115, 280)"),
                "menu_border": "rgba(170, 200, 185, 180)",
                "menu_text": "#2c3e40",
                "submenu_gradient": ("stop:0 rgba(220, 235, 225, 220), stop:1 rgba(200, 220, 210, 240)",
                                     "stop:0 rgba(235, 245, 235, 200), stop:1 rgba(220, 235, 225, 220)"),
                "submenu_active": (
                    "stop:0 rgba(95, 158, 160, 240), stop:1 rgba(70, 130, 135, 260)", "rgba(55, 110, 115, 280)"),
                "submenu_border": "rgba(150, 180, 165, 180)",
                "submenu_text": "#2c3e40",
                "background": "stop:0 rgba(248, 255, 250, 250), stop:1 rgba(240, 250, 245, 230)"
            },
            {
                "name": "💼 Warm Beige Office",
                "#category": "profesional",
                "menu_gradient": ("stop:0 rgba(250, 245, 235, 220), stop:1 rgba(235, 225, 210, 240)",
                                  "stop:0 rgba(245, 235, 225, 200), stop:1 rgba(225, 215, 200, 220)"),
                "menu_active": (
                    "stop:0 rgba(139, 115, 85, 240), stop:1 rgba(115, 95, 70, 260)", "rgba(95, 80, 60, 280)"),
                "menu_border": "rgba(200, 185, 165, 180)",
                "menu_text": "#3e3225",
                "submenu_gradient": ("stop:0 rgba(235, 225, 210, 220), stop:1 rgba(220, 210, 195, 240)",
                                     "stop:0 rgba(245, 235, 225, 200), stop:1 rgba(235, 225, 210, 220)"),
                "submenu_active": (
                    "stop:0 rgba(139, 115, 85, 240), stop:1 rgba(115, 95, 70, 260)", "rgba(95, 80, 60, 280)"),
                "submenu_border": "rgba(180, 165, 145, 180)",
                "submenu_text": "#3e3225",
                "background": "stop:0 rgba(255, 250, 245, 250), stop:1 rgba(250, 245, 235, 230)"
            },
            {
                "name": "💼 Deep Navy Business",
                "#category": "profesional",
                "menu_gradient": ("stop:0 rgba(240, 245, 255, 220), stop:1 rgba(220, 230, 245, 240)",
                                  "stop:0 rgba(230, 235, 250, 200), stop:1 rgba(210, 220, 240, 220)"),
                "menu_active": ("stop:0 rgba(44, 62, 80, 240), stop:1 rgba(30, 45, 65, 260)", "rgba(20, 35, 50, 280)"),
                "menu_border": "rgba(160, 170, 190, 180)",
                "menu_text": "#2c3e50",
                "submenu_gradient": ("stop:0 rgba(220, 230, 245, 220), stop:1 rgba(200, 215, 235, 240)",
                                     "stop:0 rgba(235, 240, 250, 200), stop:1 rgba(220, 230, 245, 220)"),
                "submenu_active": (
                    "stop:0 rgba(44, 62, 80, 240), stop:1 rgba(30, 45, 65, 260)", "rgba(20, 35, 50, 280)"),
                "submenu_border": "rgba(140, 155, 175, 180)",
                "submenu_text": "#2c3e50",
                "background": "stop:0 rgba(248, 250, 255, 250), stop:1 rgba(240, 245, 255, 230)"
            },
            {
                "name": "💼 Soft Lavender Office",
                "#category": "profesional",
                "menu_gradient": ("stop:0 rgba(248, 245, 255, 220), stop:1 rgba(230, 225, 245, 240)",
                                  "stop:0 rgba(240, 235, 250, 200), stop:1 rgba(220, 215, 240, 220)"),
                "menu_active": (
                    "stop:0 rgba(123, 104, 138, 240), stop:1 rgba(100, 85, 115, 260)", "rgba(80, 70, 95, 280)"),
                "menu_border": "rgba(180, 170, 200, 180)",
                "menu_text": "#3e2c50",
                "submenu_gradient": ("stop:0 rgba(230, 225, 245, 220), stop:1 rgba(215, 210, 235, 240)",
                                     "stop:0 rgba(240, 235, 250, 200), stop:1 rgba(230, 225, 245, 220)"),
                "submenu_active": (
                    "stop:0 rgba(123, 104, 138, 240), stop:1 rgba(100, 85, 115, 260)", "rgba(80, 70, 95, 280)"),
                "submenu_border": "rgba(160, 150, 180, 180)",
                "submenu_text": "#3e2c50",
                "background": "stop:0 rgba(252, 250, 255, 250), stop:1 rgba(248, 245, 255, 230)"
            },
            {
                "name": "💼 Cool Mint Fresh",
                "#category": "profesional",
                "menu_gradient": ("stop:0 rgba(245, 255, 250, 220), stop:1 rgba(225, 245, 235, 240)",
                                  "stop:0 rgba(235, 250, 245, 200), stop:1 rgba(215, 240, 230, 220)"),
                "menu_active": (
                    "stop:0 rgba(72, 201, 176, 240), stop:1 rgba(55, 170, 150, 260)", "rgba(40, 140, 125, 280)"),
                "menu_border": "rgba(170, 210, 195, 180)",
                "menu_text": "#2c4e45",
                "submenu_gradient": ("stop:0 rgba(225, 245, 235, 220), stop:1 rgba(210, 235, 225, 240)",
                                     "stop:0 rgba(235, 250, 245, 200), stop:1 rgba(225, 245, 235, 220)"),
                "submenu_active": (
                    "stop:0 rgba(72, 201, 176, 240), stop:1 rgba(55, 170, 150, 260)", "rgba(40, 140, 125, 280)"),
                "submenu_border": "rgba(150, 190, 175, 180)",
                "submenu_text": "#2c4e45",
                "background": "stop:0 rgba(250, 255, 252, 250), stop:1 rgba(245, 255, 250, 230)"
            },
            {
                "name": "💼 Warm Taupe Comfort",
                "#category": "profesional",
                "menu_gradient": ("stop:0 rgba(248, 245, 240, 220), stop:1 rgba(230, 225, 215, 240)",
                                  "stop:0 rgba(240, 235, 225, 200), stop:1 rgba(220, 215, 205, 220)"),
                "menu_active": (
                    "stop:0 rgba(160, 142, 122, 240), stop:1 rgba(135, 120, 105, 260)", "rgba(115, 100, 90, 280)"),
                "menu_border": "rgba(190, 175, 160, 180)",
                "menu_text": "#4a3e32",
                "submenu_gradient": ("stop:0 rgba(230, 225, 215, 220), stop:1 rgba(215, 210, 200, 240)",
                                     "stop:0 rgba(240, 235, 225, 200), stop:1 rgba(230, 225, 215, 220)"),
                "submenu_active": (
                    "stop:0 rgba(160, 142, 122, 240), stop:1 rgba(135, 120, 105, 260)", "rgba(115, 100, 90, 280)"),
                "submenu_border": "rgba(170, 155, 140, 180)",
                "submenu_text": "#4a3e32",
                "background": "stop:0 rgba(252, 248, 245, 250), stop:1 rgba(248, 245, 240, 230)"
            },
            {
                "name": "💼 Steel Blue Professional",
                "#category": "profesional",
                "menu_gradient": ("stop:0 rgba(240, 248, 252, 220), stop:1 rgba(220, 235, 245, 240)",
                                  "stop:0 rgba(230, 242, 248, 200), stop:1 rgba(210, 228, 240, 220)"),
                "menu_active": ("stop:0 rgba(52, 73, 94, 240), stop:1 rgba(40, 60, 80, 260)", "rgba(30, 50, 70, 280)"),
                "menu_border": "rgba(160, 180, 195, 180)",
                "menu_text": "#34495e",
                "submenu_gradient": ("stop:0 rgba(220, 235, 245, 220), stop:1 rgba(205, 225, 240, 240)",
                                     "stop:0 rgba(230, 242, 248, 200), stop:1 rgba(220, 235, 245, 220)"),
                "submenu_active": (
                    "stop:0 rgba(52, 73, 94, 240), stop:1 rgba(40, 60, 80, 260)", "rgba(30, 50, 70, 280)"),
                "submenu_border": "rgba(140, 160, 175, 180)",
                "submenu_text": "#34495e",
                "background": "stop:0 rgba(248, 252, 255, 250), stop:1 rgba(240, 248, 252, 230)"
            },
            {
                "name": "💼 Soft Cream Elegance",
                "#category": "profesional",
                "menu_gradient": ("stop:0 rgba(255, 252, 245, 220), stop:1 rgba(245, 235, 220, 240)",
                                  "stop:0 rgba(250, 245, 235, 200), stop:1 rgba(235, 225, 210, 220)"),
                "menu_active": (
                    "stop:0 rgba(184, 156, 123, 240), stop:1 rgba(160, 135, 105, 260)", "rgba(140, 115, 90, 280)"),
                "menu_border": "rgba(210, 190, 165, 180)",
                "menu_text": "#5d4e37",
                "submenu_gradient": ("stop:0 rgba(245, 235, 220, 220), stop:1 rgba(230, 220, 205, 240)",
                                     "stop:0 rgba(250, 245, 235, 200), stop:1 rgba(245, 235, 220, 220)"),
                "submenu_active": (
                    "stop:0 rgba(184, 156, 123, 240), stop:1 rgba(160, 135, 105, 260)", "rgba(140, 115, 90, 280)"),
                "submenu_border": "rgba(190, 170, 145, 180)",
                "submenu_text": "#5d4e37",
                "background": "stop:0 rgba(255, 253, 248, 250), stop:1 rgba(255, 252, 245, 230)"
            },

            # ===== TEME OPTIMALE SPECIALIȘTI (16-20) =====
            {
                "name": "🥇 Text Negru pe Off-White",
                "#category": "optim",
                "menu_gradient": ("stop:0 rgba(250, 250, 250, 240), stop:1 rgba(245, 245, 245, 250)",
                                  "stop:0 rgba(240, 240, 240, 220), stop:1 rgba(235, 235, 235, 240)"),
                "menu_active": ("stop:0 rgba(0, 0, 0, 250), stop:1 rgba(51, 51, 51, 260)", "rgba(0, 0, 0, 280)"),
                "menu_border": "rgba(200, 200, 200, 180)",
                "menu_text": "#000000",
                "submenu_gradient": ("stop:0 rgba(235, 235, 235, 240), stop:1 rgba(220, 220, 220, 250)",
                                     "stop:0 rgba(245, 245, 245, 220), stop:1 rgba(235, 235, 235, 240)"),
                "submenu_active": ("stop:0 rgba(0, 0, 0, 250), stop:1 rgba(51, 51, 51, 260)", "rgba(0, 0, 0, 280)"),
                "submenu_border": "rgba(180, 180, 180, 180)",
                "submenu_text": "#000000",
                "background": "stop:0 rgba(250, 250, 250, 250), stop:1 rgba(248, 248, 248, 230)"
            },
            {
                "name": "🥈 Text Gri Închis pe Alb Crem",
                "#category": "optim",
                "menu_gradient": ("stop:0 rgba(248, 248, 248, 240), stop:1 rgba(243, 243, 243, 250)",
                                  "stop:0 rgba(238, 238, 238, 220), stop:1 rgba(233, 233, 233, 240)"),
                "menu_active": ("stop:0 rgba(51, 51, 51, 250), stop:1 rgba(68, 68, 68, 260)", "rgba(51, 51, 51, 280)"),
                "menu_border": "rgba(200, 200, 200, 180)",
                "menu_text": "#333333",
                "submenu_gradient": ("stop:0 rgba(233, 233, 233, 240), stop:1 rgba(218, 218, 218, 250)",
                                     "stop:0 rgba(243, 243, 243, 220), stop:1 rgba(233, 233, 233, 240)"),
                "submenu_active": (
                    "stop:0 rgba(51, 51, 51, 250), stop:1 rgba(68, 68, 68, 260)", "rgba(51, 51, 51, 280)"),
                "submenu_border": "rgba(180, 180, 180, 180)",
                "submenu_text": "#333333",
                "background": "stop:0 rgba(248, 248, 248, 250), stop:1 rgba(246, 246, 246, 230)"
            },
            {
                "name": "🥉 Text Negru pe Gri Foarte Deschis",
                "#category": "optim",
                "menu_gradient": ("stop:0 rgba(243, 243, 243, 240), stop:1 rgba(238, 238, 238, 250)",
                                  "stop:0 rgba(233, 233, 233, 220), stop:1 rgba(228, 228, 228, 240)"),
                "menu_active": ("stop:0 rgba(45, 45, 45, 250), stop:1 rgba(62, 62, 62, 260)", "rgba(45, 45, 45, 280)"),
                "menu_border": "rgba(195, 195, 195, 180)",
                "menu_text": "#2D2D2D",
                "submenu_gradient": ("stop:0 rgba(228, 228, 228, 240), stop:1 rgba(213, 213, 213, 250)",
                                     "stop:0 rgba(238, 238, 238, 220), stop:1 rgba(228, 228, 228, 240)"),
                "submenu_active": (
                    "stop:0 rgba(45, 45, 45, 250), stop:1 rgba(62, 62, 62, 260)", "rgba(45, 45, 45, 280)"),
                "submenu_border": "rgba(175, 175, 175, 180)",
                "submenu_text": "#2D2D2D",
                "background": "stop:0 rgba(243, 243, 243, 250), stop:1 rgba(241, 241, 241, 230)"
            },
            {
                "name": "🏅 Text Gri pe Fundal Crem",
                "#category": "optim",
                "menu_gradient": ("stop:0 rgba(254, 254, 254, 240), stop:1 rgba(249, 249, 249, 250)",
                                  "stop:0 rgba(244, 244, 244, 220), stop:1 rgba(239, 239, 239, 240)"),
                "menu_active": ("stop:0 rgba(74, 74, 74, 250), stop:1 rgba(91, 91, 91, 260)", "rgba(74, 74, 74, 280)"),
                "menu_border": "rgba(205, 205, 205, 180)",
                "menu_text": "#4A4A4A",
                "submenu_gradient": ("stop:0 rgba(239, 239, 239, 240), stop:1 rgba(224, 224, 224, 250)",
                                     "stop:0 rgba(249, 249, 249, 220), stop:1 rgba(239, 239, 239, 240)"),
                "submenu_active": (
                    "stop:0 rgba(74, 74, 74, 250), stop:1 rgba(91, 91, 91, 260)", "rgba(74, 74, 74, 280)"),
                "submenu_border": "rgba(185, 185, 185, 180)",
                "submenu_text": "#4A4A4A",
                "background": "stop:0 rgba(254, 254, 254, 250), stop:1 rgba(252, 252, 252, 230)"
            },
            {
                "name": "🎖️ Schema Gri Monochromă",
                "#category": "optim",
                "menu_gradient": ("stop:0 rgba(238, 238, 238, 240), stop:1 rgba(233, 233, 233, 250)",
                                  "stop:0 rgba(228, 228, 228, 220), stop:1 rgba(223, 223, 223, 240)"),
                "menu_active": ("stop:0 rgba(44, 44, 44, 250), stop:1 rgba(61, 61, 61, 260)", "rgba(44, 44, 44, 280)"),
                "menu_border": "rgba(190, 190, 190, 180)",
                "menu_text": "#2C2C2C",
                "submenu_gradient": ("stop:0 rgba(223, 223, 223, 240), stop:1 rgba(208, 208, 208, 250)",
                                     "stop:0 rgba(233, 233, 233, 220), stop:1 rgba(223, 223, 223, 240)"),
                "submenu_active": (
                    "stop:0 rgba(44, 44, 44, 250), stop:1 rgba(61, 61, 61, 260)", "rgba(44, 44, 44, 280)"),
                "submenu_border": "rgba(170, 170, 170, 180)",
                "submenu_text": "#2C2C2C",
                "background": "stop:0 rgba(238, 238, 238, 250), stop:1 rgba(236, 236, 236, 230)"
            }
            # ===== LOCUL PENTRU TEME ADIȚIONALE =====
            # Structura păstrată pentru adăugarea ușoară de noi teme
        ]

        # Încarcă setările
        self.load_settings()

    def load_settings(self):
        """Încarcă setările din fișierul JSON"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.current_theme = settings.get('current_theme', 0)

                    # Validează tema încărcată
                    if self.current_theme < 0 or self.current_theme >= len(self.themes):
                        self.current_theme = 0
                        self.save_settings()

                    print(f"🎨 Tema încărcată: '{self.get_theme_name()}'")
            else:
                print("🎨 Prima pornire - folosesc tema implicită")
                self.save_settings()
        except Exception as e:
            print(f"⚠️ Eroare la încărcarea setărilor: {e}. Folosesc tema implicită.")
            self.current_theme = 0
            self.save_settings()

    def save_settings(self):
        """Salvează setările în fișierul JSON"""
        try:
            settings = {
                'current_theme': self.current_theme,
                'app_version': '3.2',
                'last_updated': QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
            }

            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)

            print(f"💾 Tema '{self.get_theme_name()}' salvată persistent")
        except Exception as e:
            print(f"⚠️ Eroare la salvarea setărilor: {e}")

    def get_current_theme(self):
        """Returnează tema curentă"""
        return self.themes[self.current_theme]

    def next_theme(self):
        """Trece la următoarea temă și o salvează"""
        self.current_theme = (self.current_theme + 1) % len(self.themes)
        self.save_settings()
        return self.get_current_theme()

    def set_theme(self, theme_index):
        """Setează o temă specifică prin index și o salvează"""
        if 0 <= theme_index < len(self.themes):
            self.current_theme = theme_index
            self.save_settings()
            return True
        return False

    def get_theme_name(self):
        """Returnează numele temei curente"""
        return self.themes[self.current_theme]["name"]

    def get_all_theme_names(self):
        """Returnează lista cu toate numele temelor"""
        return [theme["name"] for theme in self.themes]


class CurrencyToggleWidget(QWidget):
    """Widget pentru toggle RON/EUR în meniul lateral"""

    def __init__(self, currency_logic, theme_manager, parent=None):
        super().__init__(parent)
        self.currency_logic = currency_logic
        self.theme_manager = theme_manager
        self.setFixedHeight(95)
        self._setup_ui()
        self._connect_signals()
        self._update_display()

    def _setup_ui(self):
        """Configurează interfața"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(6)

        # Separator vizual
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: rgba(189, 195, 199, 120); margin: 2px 10px;")
        layout.addWidget(separator)

        # Container pentru butoane
        button_container = QHBoxLayout()
        button_container.setSpacing(8)
        button_container.setContentsMargins(5, 0, 5, 0)

        # Spacer pentru centrare butoane
        button_container.addStretch()

        # Buton RON
        self.ron_btn = QPushButton("RON")
        self.ron_btn.setFixedSize(55, 28)
        self.ron_btn.setCursor(Qt.PointingHandCursor)
        self.ron_btn.setFont(QFont("Arial", 9, QFont.Bold))
        button_container.addWidget(self.ron_btn)

        # Buton EUR
        self.eur_btn = QPushButton("EUR")
        self.eur_btn.setFixedSize(55, 28)
        self.eur_btn.setCursor(Qt.PointingHandCursor)
        self.eur_btn.setFont(QFont("Arial", 9, QFont.Bold))
        button_container.addWidget(self.eur_btn)

        # Spacer pentru alinierea finală
        button_container.addStretch()

        layout.addLayout(button_container)

        # Indicator permisiuni pe al doilea rând
        self.permission_label = QLabel()
        self.permission_label.setFont(QFont("Arial", 9, QFont.Bold))
        self.permission_label.setAlignment(Qt.AlignCenter)
        self.permission_label.setMinimumHeight(32)
        layout.addWidget(self.permission_label)

    def _connect_signals(self):
        """Conectează semnalele"""
        self.ron_btn.clicked.connect(self.currency_logic.switch_to_ron)
        self.eur_btn.clicked.connect(self.currency_logic.switch_to_eur)
        self.currency_logic.currency_changed.connect(self._update_display)

    def _update_display(self):
        """Actualizează afișajul în funcție de starea curentă"""
        current_currency = self.currency_logic.get_current_currency()
        can_write = self.currency_logic.can_write_data()
        is_eur_available = self.currency_logic.is_eur_conversion_available()
        theme = self.theme_manager.get_current_theme()

        # Activare/Dezactivare butoane
        self.eur_btn.setEnabled(is_eur_available)

        # Stiluri pentru butoanele active/inactive
        base_style = "border-radius: 8px; font-size: 9pt; font-weight: bold; padding: 4px 8px;"
        active_style = f"background: qlineargradient(x1:0, y1:0, x2:0, y2:1, {theme['menu_active'][0]}); color: white; border: 2px solid {theme['menu_active'][1]};"
        inactive_style = f"background: qlineargradient(x1:0, y1:0, x2:0, y2:1, {theme['menu_gradient'][0]}); color: {theme['menu_text']}; border: 1px solid {theme['menu_border']};"
        disabled_style = "background-color: #d3d3d3; color: #808080; border: 1px solid #a0a0a0;"

        # Aplicarea stilurilor RON
        if current_currency == 'RON':
            if can_write:
                self.ron_btn.setStyleSheet(base_style + active_style)
                self.ron_btn.setToolTip("Modul RON - Citire și Scriere")
            else:
                self.ron_btn.setStyleSheet(base_style + active_style)
                self.ron_btn.setToolTip("Modul RON - Doar Citire (Protecție Date)")
        else:
            self.ron_btn.setStyleSheet(base_style + inactive_style)
            self.ron_btn.setToolTip("Comută la modul RON")

        # Aplicarea stilurilor EUR
        if current_currency == 'EUR':
            self.eur_btn.setStyleSheet(base_style + active_style)
            self.eur_btn.setToolTip("Modul EUR - Citire și Scriere")
        elif is_eur_available:
            self.eur_btn.setStyleSheet(base_style + inactive_style)
            self.eur_btn.setToolTip("Comută la modul EUR")
        else:
            self.eur_btn.setStyleSheet(base_style + disabled_style)
            self.eur_btn.setToolTip("EUR indisponibil - Conversia nu a fost aplicată")

        # Actualizarea indicatorului de permisiuni
        permission_text = "Citire-Scriere" if can_write else "Doar Citire"
        permission_color = "#27AE60" if can_write else "#E67E22"
        icon = "✅" if can_write else "🔒"

        # Setare text cu icon
        self.permission_label.setText(f"{icon} {permission_text}")

        # Stil tip card modern - OPTIMIZAT pentru evitarea text clipping
        self.permission_label.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {'#eafaf1' if can_write else '#fdf6e3'},
                stop:1 {'#d4efdf' if can_write else '#fbeee0'});
            color: {permission_color};
            font-size: 9pt;
            font-weight: bold;
            padding: 6px 20px;
            border-radius: 12px;
            margin-left: 16px;
            margin-right: 16px;
        """)


class ModernButton(QPushButton):
    """Buton îmbunătățit cu efecte moderne"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.is_active = False
        self.theme_manager = None

        # Animație pentru hover
        self.hover_animation = QPropertyAnimation(self, b"geometry")
        self.hover_animation.setDuration(150)
        self.hover_animation.setEasingCurve(QEasingCurve.OutCubic)

        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(28)

    def set_theme_manager(self, theme_manager):
        """Setează manager-ul de teme"""
        self.theme_manager = theme_manager
        self.update_style()

    def set_active(self, active):
        """Setează starea activă"""
        self.is_active = active
        self.update_style()

    def update_style(self):
        """Actualizează stilul butonului"""
        if not self.theme_manager:
            return

        theme = self.theme_manager.get_current_theme()

        if self.is_active:
            # Buton activ
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        {theme['menu_active'][0]});
                    border: 2px solid {theme['menu_active'][1]};
                    border-radius: 8px;
                    padding: 4px 12px;
                    font-size: 10pt;
                    color: white;
                    text-align: left;
                    font-weight: bold;
                    backdrop-filter: blur(10px);
                }}
            """)
        else:
            # Buton normal
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        {theme['menu_gradient'][0]});
                    border: 1px solid {theme['menu_border']};
                    border-radius: 8px;
                    padding: 4px 12px;
                    font-size: 10pt;
                    color: {theme['menu_text']};
                    text-align: left;
                    font-weight: normal;
                    backdrop-filter: blur(5px);
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        {theme['menu_gradient'][1]});
                    transform: scale(1.02);
                    backdrop-filter: blur(8px);
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        {theme['menu_active'][0]});
                    transform: scale(0.98);
                }}
            """)

    def enterEvent(self, event):
        """Animație la hover"""
        if not self.is_active:
            current = self.geometry()
            target = QRect(current.x() - 1, current.y(), current.width() + 2, current.height())
            self.hover_animation.setStartValue(current)
            self.hover_animation.setEndValue(target)
            self.hover_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Animație la leave"""
        if not self.is_active:
            current = self.geometry()
            target = QRect(current.x() + 1, current.y(), current.width() - 2, current.height())
            self.hover_animation.setStartValue(current)
            self.hover_animation.setEndValue(target)
            self.hover_animation.start()
        super().leaveEvent(event)


class ModernSubmenuButton(QPushButton):
    """Buton modern pentru submeniu"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.is_active = False
        self.theme_manager = None
        self.setCursor(Qt.PointingHandCursor)

    def set_theme_manager(self, theme_manager):
        """Setează manager-ul de teme"""
        self.theme_manager = theme_manager
        self.update_style()

    def set_active(self, active):
        """Setează starea activă"""
        self.is_active = active
        self.update_style()

    def update_style(self):
        """Actualizează stilul butonului"""
        if not self.theme_manager:
            return

        theme = self.theme_manager.get_current_theme()

        if self.is_active:
            # Buton activ
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        {theme['submenu_active'][0]});
                    color: white;
                    border: 1px solid {theme['submenu_active'][1]};
                    border-radius: 8px;
                    padding: 6px 12px;
                    font-size: 10pt;
                    font-weight: bold;
                    backdrop-filter: blur(10px);
                }}
            """)
        else:
            # Buton normal
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        {theme['submenu_gradient'][0]});
                    color: {theme['submenu_text']};
                    border: 1px solid {theme['submenu_border']};
                    border-radius: 8px;
                    padding: 6px 12px;
                    font-size: 10pt;
                    font-weight: normal;
                    backdrop-filter: blur(5px);
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        {theme['submenu_gradient'][1]});
                    transform: translateY(-1px);
                    backdrop-filter: blur(8px);
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        {theme['submenu_active'][0]});
                    transform: translateY(0px);
                }}
            """)


class CalculatorWindow(QMainWindow):
    """Fereastră calculator cu design modern"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🧮 Calculator C.A.R.")
        self.setWindowIcon(QIcon("icons/calc.png"))
        self.setMinimumSize(450, 350)
        self.resize(450, 350)

        # Calculator widget
        calculator_widget = CalculatorWidget()
        self.setCentralWidget(calculator_widget)

        # Styling modern
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(236, 240, 241, 240), stop:1 rgba(189, 195, 199, 220));
                backdrop-filter: blur(10px);
            }
        """)

        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.center_window()

    def center_window(self):
        """Centrează fereastra pe ecran"""
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )


class CARApp(QMainWindow):
    """Aplicația principală cu sistem dual RON/EUR prin monkey patching condițional"""

    # ===== MODIFICARE 1: Constantă pentru meniuri protejate =====
    # Meniuri care necesită permisiuni de scriere în baze de date
    WRITE_PROTECTED_MENUS = [
        "Actualizări",      # Submeniu întreg: Adăugare, Sume lunare, Lichidare, Ștergere, Dividende
        "Generare lună",    # Operațiuni INSERT masive pentru lună nouă
        "Optimizare baze"   # Operațiuni structurale VACUUM/REINDEX
    ]

    def __init__(self):
        super().__init__()

        # Componente principale
        self.theme_manager = ThemeManager()
        self.currency_logic = CurrencyLogic()
        self.conversie_checker = ConversieStatusChecker()
        self.currency_logic.currency_changed.connect(self._on_currency_changed)

        # State management
        self.loaded_widgets = {}
        self.calculator_window = None
        self.imprumuturi_noi_window = None
        self.menu_buttons = {}
        self.submenu_buttons = []
        self.current_submenu_text = None

        # Setup interfață
        self._setup_main_window()
        self._setup_ui()
        self.setup_shortcuts()
        self._apply_modern_styling()

        # Încarcă widget-ul inițial de statistici
        self._load_initial_stats_widget()

        # ===== MODIFICARE 5: Setare inițială permisiuni =====
        self._update_menu_write_permissions()

        self.show()

    def _on_currency_changed(self, currency):
        """Gestionează schimbarea monedei"""
        print(f"--- Schimbare monedă către: {currency} ---")
        
        # RE-PATCH toate modulele deja încărcate
        self._repatch_loaded_modules()

        # ===== MODIFICARE 3: Actualizare permisiuni după schimbare monedă =====
        self._update_menu_write_permissions()

        # Reîncarcă widget-ul curent dacă este sensibil la monedă
        if hasattr(self, 'current_submenu_text') and self.current_submenu_text:
            self.on_submenu_clicked(self.current_submenu_text, force_reload=True)
        elif any(btn.is_active for btn in self.menu_buttons.values() if btn.text().endswith("Listări")):
            self.menu_buttons["Listări"].click()

    def _repatch_loaded_modules(self):
        """Re-patchuiește toate modulele UI deja încărcate"""
        import sys
        from pathlib import Path

        # Maparea bazelor RON -> EUR
        db_mapping = {
            "MEMBRII.db": "MEMBRIIEUR.db",
            "DEPCRED.db": "DEPCREDEUR.db",
            "activi.db": "activiEUR.db",
            "INACTIVI.db": "INACTIVIEUR.db",
            "LICHIDATI.db": "LICHIDATIEUR.db"
        }

        base_path = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
        current_currency = self.currency_logic.get_current_currency()

        print(f"🔄 Re-patching pentru modul: {current_currency}")

        # Re-patchuiește toate modulele UI din sys.modules
        patched_count = 0
        for module_name, module in sys.modules.items():
            if module_name.startswith('ui.') and hasattr(module, 'DB_MEMBRII'):

                for attr_name in dir(module):
                    if attr_name.startswith('DB_'):
                        current_value_str = str(getattr(module, attr_name))

                        if current_currency == "EUR":
                            # Comută la EUR
                            for ron_db, eur_db in db_mapping.items():
                                if ron_db in current_value_str and eur_db not in current_value_str:
                                    new_value = current_value_str.replace(ron_db, eur_db)
                                    if (base_path / eur_db).exists():
                                        setattr(module, attr_name, new_value)
                                        print(f"RE-PATCH EUR: {module_name}.{attr_name} -> {eur_db}")
                                        patched_count += 1
                                    else:
                                        print(f"WARNING: {eur_db} nu există, păstrez {ron_db}")
                                    break
                        else:
                            # Comută la RON
                            for ron_db, eur_db in db_mapping.items():
                                if eur_db in current_value_str:
                                    new_value = current_value_str.replace(eur_db, ron_db)
                                    setattr(module, attr_name, new_value)
                                    print(f"RE-PATCH RON: {module_name}.{attr_name} -> {ron_db}")
                                    patched_count += 1
                                    break

        print(f"✅ Re-patching completat: {patched_count} atribute modificate")

    # ===== MODIFICARE 2: Metodă pentru actualizare permisiuni meniuri =====
    def _update_menu_write_permissions(self):
        """Actualizează starea meniurilor în funcție de permisiunile de scriere"""
        can_write = self.currency_logic.can_write_data()
        current_currency = self.currency_logic.get_current_currency()
        is_conversion_applied = self.conversie_checker.is_conversion_applied()
        
        # Determină starea de protecție
        is_write_protected = is_conversion_applied and current_currency == "RON"
        
        # Actualizează fiecare meniu protejat
        for menu_name in self.WRITE_PROTECTED_MENUS:
            if menu_name in self.menu_buttons:
                button = self.menu_buttons[menu_name]
                button.setEnabled(can_write)
                
                # Actualizează tooltip-ul cu informații despre restricție
                if is_write_protected:
                    original_tooltip = button.toolTip().split('\n')[0]
                    button.setToolTip(
                        f"{original_tooltip}\n\n"
                        f"🔒 RESTRICȚIONAT în modul RON post-conversie\n"
                        f"Comută la EUR pentru operațiuni de scriere"
                    )
                    
                    # Aplicare stil vizual pentru buton dezactivat
                    theme = self.theme_manager.get_current_theme()
                    button.setStyleSheet(f"""
                        QPushButton {{
                            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(189, 195, 199, 150), stop:1 rgba(149, 165, 166, 170));
                            border: 1px solid rgba(127, 140, 141, 150);
                            border-radius: 8px;
                            padding: 4px 12px;
                            font-size: 10pt;
                            color: rgba(52, 73, 94, 150);
                            text-align: left;
                            font-weight: normal;
                            backdrop-filter: blur(5px);
                        }}
                        QPushButton:disabled {{
                            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(189, 195, 199, 120), stop:1 rgba(149, 165, 166, 140));
                            color: rgba(127, 140, 141, 180);
                        }}
                    """)
                else:
                    # Restaurează tooltip-ul original
                    shortcuts_map = {
                        "Actualizări": "Alt+A",
                        "Generare lună": "Alt+G",
                        "Optimizare baze": "Alt+O"
                    }
                    shortcut = shortcuts_map.get(menu_name, "")
                    tooltip = menu_name
                    if shortcut:
                        tooltip += f"\nScurtătură: {shortcut}"
                    button.setToolTip(tooltip)
                    
                    # Restaurează stilul normal
                    button.update_style()
        
        # Log pentru debugging
        status = "RESTRICȚIONAT" if is_write_protected else "PERMIS"
        print(f"📝 Permisiuni scriere actualizate: {status} (Monedă: {current_currency}, Conversie: {is_conversion_applied})")

    def _setup_main_window(self):
        """Configurează fereastra principală"""
        self.setGeometry(100, 100, 1200, 800)
        self.move(50, 50)
        self.setWindowIcon(QIcon("icons/app_icon.png"))
        self.update_window_title()

        # Timer pentru actualizarea titlului
        self.title_timer = QTimer(self)
        self.title_timer.timeout.connect(self.update_window_title)
        self.title_timer.start(1000)

    def _setup_ui(self):
        """Configurează interfața utilizator"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Splitter principal
        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)

        # Container pentru meniu
        self.menu_container = QFrame()
        self._setup_menu_container()

        # Container pentru conținut
        self.content_container = QFrame()
        self._setup_content_container()

        # Adaugă la splitter
        self.splitter.addWidget(self.menu_container)
        self.splitter.addWidget(self.content_container)
        self.splitter.setStretchFactor(1, 3)

    def _setup_menu_container(self):
        """Configurează container-ul de meniu cu toggle RON/EUR integrat"""
        self.menu_container.setStyleSheet(
            "border: 2px solid black; border-radius: 5px; background-color: rgba(240, 240, 240, 200); backdrop-filter: blur(10px);")
        menu_layout = QVBoxLayout(self.menu_container)
        menu_layout.setSpacing(2)
        menu_layout.setContentsMargins(10, 10, 10, 10)

        # Butoanele de meniu
        menu_items = [
            ("Actualizări", "👥"),
            ("Vizualizări", "📊"),
            ("Listări", "📋"),
            ("Salvări", "💾"),
            ("Împrumuturi Noi", "💰"),
            ("Calcule", "🧮"),
            ("CAR DBF Converter", "🔄"),
            ("Conversie RON->EUR", "💱"),
            ("Optimizare baze", "⚡"),
            ("Generare lună", "📅"),
            ("Selector temă", "🎭"),
            ("Versiune", "ℹ️"),
            ("Ieșire", "🚪")
        ]

        # Mapare scurtături pentru tooltip-uri
        shortcuts_map = {
            "Actualizări": "Alt+A",
            "Vizualizări": "Alt+V",
            "Listări": "Alt+L",
            "Salvări": "Alt+S",
            "Împrumuturi Noi": "Alt+I",
            "Calcule": "Ctrl+Alt+C",
            "CAR DBF Converter": "Ctrl+Alt+D",
            "Conversie RON->EUR": "Ctrl+Alt+R",
            "Optimizare baze": "Alt+O",
            "Generare lună": "Alt+G",
            "Selector temă": "Ctrl+Alt+T",
            "Versiune": "Alt+R",
            "Ieșire": "Alt+Q"
        }

        for item, emoji in menu_items:
            btn = ModernButton(f"{emoji} {item}")
            btn.set_theme_manager(self.theme_manager)
            btn.clicked.connect(self.menu_clicked)
            menu_layout.addWidget(btn, 0)
            self.menu_buttons[item] = btn

            # Setare tooltip cu scurtătură
            if item in shortcuts_map and shortcuts_map[item]:
                btn.setToolTip(f"{item}\nScurtătură: {shortcuts_map[item]}")
            else:
                btn.setToolTip(item)

            # Configurare specială pentru butonul de conversie
            if item == "Conversie RON->EUR":
                self._update_conversie_button_state(btn)

        # Adăugare toggle RON/EUR în meniul lateral
        self.currency_toggle = CurrencyToggleWidget(self.currency_logic, self.theme_manager)
        menu_layout.addWidget(self.currency_toggle)

        menu_layout.addStretch()

    def _update_conversie_button_state(self, btn):
        """Actualizează starea butonului de conversie"""
        if self.conversie_checker.is_conversion_applied():
            btn.setText("💱 Sistem în EUR")
            btn.setEnabled(False)
            btn.setToolTip("Conversia definitivă la EUR a fost aplicată.")
        else:
            btn.setEnabled(CONVERSIE_WIDGET_AVAILABLE)
            btn.setToolTip("Pornește procesul de conversie RON -> EUR.")

    def _setup_content_container(self):
        """Configurează container-ul de conținut"""
        self.content_container.setStyleSheet(
            "border: 2px solid black; border-radius: 5px; background-color: rgba(255, 255, 255, 200); backdrop-filter: blur(10px);")
        content_layout = QVBoxLayout(self.content_container)

        # Submenu bar
        self.submenu_bar = QWidget()
        self.submenu_layout = QHBoxLayout(self.submenu_bar)
        self.submenu_layout.setSpacing(10)
        self.submenu_layout.setContentsMargins(10, 5, 10, 5)
        self.submenu_bar.setVisible(False)
        content_layout.addWidget(self.submenu_bar)

        # Content area
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet(
            "border: none; background-color: rgba(248, 248, 248, 200); backdrop-filter: blur(5px);")
        content_layout.addWidget(self.content_area)

    def _load_initial_stats_widget(self):
        """Încarcă widget-ul inițial de statistici"""
        try:
            self.statistici_widget = StatisticiWidget()
            self.content_area.addWidget(self.statistici_widget)
            self.animate_transition_to(self.statistici_widget)
            print("INFO: Widget-ul de statistici inițial a fost încărcat")
        except Exception as e:
            print(f"EROARE la încărcarea widget-ului de statistici: {e}")

    def _apply_modern_styling(self):
        """Aplică styling modern"""
        theme = self.theme_manager.get_current_theme()
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    {theme['background']});
                backdrop-filter: blur(15px);
            }}
        """)

    def update_window_title(self):
        """Actualizează titlul ferestrei"""
        current_date = QDateTime.currentDateTime().toString("dd/MM/yyyy")
        current_time = QDateTime.currentDateTime().toString("HH:mm:ss")
        spaces = " " * (self.width() // 10)
        currency_info = f" • {self.currency_logic.get_current_currency()}"
        permission_info = " (R-O)" if not self.currency_logic.can_write_data() else ""

        self.setWindowTitle(f"C.A.R. Petroșani{spaces}{current_date} - {current_time}{currency_info}{permission_info}")

    def on_submenu_clicked(self, text, force_reload=False):
        """Gestionează click-urile pe submeniu - cu suport pentru dual currency"""
        self.current_submenu_text = text
        current_currency = self.currency_logic.get_current_currency()
        widget_key = f"{text}_{current_currency}"

        # Forțează reîncărcarea dacă este necesar
        if force_reload and widget_key in self.loaded_widgets:
            old_widget = self.loaded_widgets.pop(widget_key)
            self.content_area.removeWidget(old_widget)
            old_widget.deleteLater()

        # Încarcă widget-ul dacă nu există în cache
        if widget_key not in self.loaded_widgets:
            widget_class = self._get_widget_class(text)
            if not widget_class:
                return

            try:
                # Verifică dacă widget-ul acceptă currency_logic ca parametru
                sig = inspect.signature(widget_class.__init__)
                if 'currency_logic' in sig.parameters:
                    widget = widget_class(currency_logic=self.currency_logic)
                else:
                    widget = widget_class()

                self.loaded_widgets[widget_key] = widget
                self.content_area.addWidget(widget)
                print(f"WIDGET CREAT: {widget_key} cu clasa {widget_class.__name__}")
            except Exception as e:
                print(f"EROARE la instanțierea {widget_key}: {e}")
                QMessageBox.critical(self, "Eroare Widget", f"Nu s-a putut crea instanța pentru '{text}'.")
                return

        # Actualizează UI
        for btn in self.submenu_buttons:
            btn.set_active(btn.text() == text)
        self.animate_transition_to(self.loaded_widgets[widget_key])
        print(f"ACTIVAT: '{text}' în modul {current_currency}")

    def revino_la_statistici(self):
        """Revine la statistici"""
        self.current_submenu_text = None
        self.submenu_bar.setVisible(False)
        self.animate_transition_to(self.statistici_widget)
        self.statistici_widget.load_data()

        for btn in self.menu_buttons.values():
            btn.set_active(False)

    def menu_clicked(self):
        """Gestionează click-urile pe meniu"""
        sender = self.sender().text()
        if " " in sender:
            sender_name = sender.split(" ", 1)[1]
        else:
            sender_name = sender

        # ===== MODIFICARE 4: Verificare permisiuni pentru meniuri protejate =====
        if sender_name in self.WRITE_PROTECTED_MENUS:
            if not self.currency_logic.can_write_data():
                QMessageBox.warning(
                    self,
                    "Operațiune Restricționată",
                    f"<b>{sender_name}</b> necesită permisiuni de scriere.<br><br>"
                    f"🔒 Modul <b>RON</b> este doar pentru <b>citire</b> după aplicarea conversiei.<br><br>"
                    f"💡 Pentru a efectua modificări:<br>"
                    f"&nbsp;&nbsp;&nbsp;1. Comută toggle-ul la <b>EUR</b><br>"
                    f"&nbsp;&nbsp;&nbsp;2. Efectuează operațiunile necesare<br>"
                    f"&nbsp;&nbsp;&nbsp;3. Bazele EUR sunt activate pentru scriere completă",
                    QMessageBox.Ok
                )
                return

        for btn in self.menu_buttons.values():
            btn.set_active(False)

        # Gestionează butoanele speciale
        if sender_name == "Selector temă":
            self.show_theme_selector()
            self.menu_buttons["Selector temă"].set_active(True)
            return

        if sender_name == "Împrumuturi Noi":
            self.open_imprumuturi_noi_window()
            if "Împrumuturi Noi" in self.menu_buttons:
                self.menu_buttons["Împrumuturi Noi"].set_active(True)
            return

        if sender_name == "Calcule":
            self.open_calculator_window()
            if "Calcule" in self.menu_buttons:
                self.menu_buttons["Calcule"].set_active(True)
            return

        # Gestionează CAR DBF Converter
        if sender_name == "CAR DBF Converter":
            if CAR_DBF_AVAILABLE:
                self.submenu_bar.setVisible(False)
                if "CAR DBF Converter" not in self.loaded_widgets:
                    widget = CARDBFConverterWidget()
                    self.loaded_widgets["CAR DBF Converter"] = widget
                    self.content_area.addWidget(widget)
                self.animate_transition_to(self.loaded_widgets["CAR DBF Converter"])
                if "CAR DBF Converter" in self.menu_buttons:
                    self.menu_buttons["CAR DBF Converter"].set_active(True)
            else:
                QMessageBox.warning(self, "CAR DBF Converter",
                                    "CAR DBF Converter nu este disponibil!\n\n"
                                    "Asigură-te că fișierul car_dbf_converter_widget.py există în directorul aplicației.")
            return

        # Gestionează Conversie RON->EUR
        if sender_name == "Conversie RON->EUR":
            if CONVERSIE_WIDGET_AVAILABLE and not self.conversie_checker.is_conversion_applied():
                self.submenu_bar.setVisible(False)
                if "Conversie RON->EUR" not in self.loaded_widgets:
                    widget = ConversieWidget()
                    self.loaded_widgets["Conversie RON->EUR"] = widget
                    self.content_area.addWidget(widget)
                self.animate_transition_to(self.loaded_widgets["Conversie RON->EUR"])
                if "Conversie RON->EUR" in self.menu_buttons:
                    self.menu_buttons["Conversie RON->EUR"].set_active(True)
            return

        # Logica originală
        self.revino_la_statistici()
        if sender_name in self.menu_buttons:
            self.menu_buttons[sender_name].set_active(True)

        if sender_name == "Optimizare baze":
            self.submenu_bar.setVisible(False)
            if "Optimizare baze" not in self.loaded_widgets:
                widget = OptimizareIndexWidget()
                self.loaded_widgets["Optimizare baze"] = widget
                self.content_area.addWidget(widget)
            self.animate_transition_to(self.loaded_widgets["Optimizare baze"])
            if "Optimizare baze" in self.menu_buttons:
                self.menu_buttons["Optimizare baze"].set_active(True)
            return

        if sender_name == "Ieșire":
            self.close()
            return

        if sender_name in ["Actualizări", "Vizualizări"]:
            submenu_items = []
            if sender_name == "Actualizări":
                submenu_items = ["Adăugare membru", "Sume lunare", "Lichidare membru", "Ștergere membru", "Dividende"]
            elif sender_name == "Vizualizări":
                submenu_items = ["Situație lunară", "Situație trimestrială", "Situație anuală", "Verificare fișe",
                                 "Afișare membri inactivi"]
            self.load_submenu(submenu_items)
        elif sender_name == "Listări":
            current_currency = self.currency_logic.get_current_currency()
            widget_key = f"Listări_{current_currency}"

            self.submenu_bar.setVisible(False)

            if widget_key not in self.loaded_widgets:
                widget_class = self._get_listari_widget_class()
                widget = widget_class()
                self.loaded_widgets[widget_key] = widget
                self.content_area.addWidget(widget)
                print(f"WIDGET CREAT: {widget_key} cu clasa {widget_class.__name__}")

            self.animate_transition_to(self.loaded_widgets[widget_key])
            print(f"ACTIVAT: 'Listări' în modul {current_currency}")

        elif sender_name in ["Salvări", "Versiune", "Generare lună"]:
            direct_mapping = {
                "Salvări": OperatiuniSalvareWidget,
                "Versiune": DespreWidget,
                "Generare lună": GenerareLunaNouaWidget
            }

            self.submenu_bar.setVisible(False)
            if sender_name not in self.loaded_widgets:
                widget = direct_mapping[sender_name]()
                self.loaded_widgets[sender_name] = widget
                self.content_area.addWidget(widget)
            self.animate_transition_to(self.loaded_widgets[sender_name])

    def load_submenu(self, items):
        """Încarcă submeniul"""
        for i in reversed(range(self.submenu_layout.count())):
            widget = self.submenu_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.submenu_buttons.clear()
        self.submenu_bar.setVisible(True)

        for item in items:
            button = ModernSubmenuButton(item)
            button.set_theme_manager(self.theme_manager)
            button.clicked.connect(lambda checked, text=item: self.on_submenu_clicked(text))
            self.submenu_layout.addWidget(button)
            self.submenu_buttons.append(button)

        # Buton ieșire cu styling modern
        iesire_btn = ModernSubmenuButton("⬅ Ieșire Meniu")
        iesire_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(231, 76, 60, 220), stop:1 rgba(192, 57, 43, 240));
                color: white;
                border: 1px solid rgba(169, 50, 38, 180);
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 10pt;
                font-weight: bold;
                backdrop-filter: blur(10px);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(236, 112, 99, 200), stop:1 rgba(203, 67, 53, 220));
                backdrop-filter: blur(8px);
            }
        """)
        iesire_btn.clicked.connect(self.revino_la_statistici)
        self.submenu_layout.addWidget(iesire_btn)

        # Activează primul buton din submeniu, dacă există
        if self.submenu_buttons:
            first_button_text = self.submenu_buttons[0].text()
            self.on_submenu_clicked(first_button_text)

    def show_theme_selector(self):
        """Afișează selector de teme cu preview real-time"""
        dialog = QDialog(self)
        dialog.setWindowTitle("🎨 Selectează Tema - Preview Real-Time")
        dialog.setModal(True)
        dialog.resize(500, 400)

        # Centrează dialogul
        parent_geometry = self.geometry()
        dialog.move(
            parent_geometry.x() + (parent_geometry.width() - dialog.width()) // 2,
            parent_geometry.y() + (parent_geometry.height() - dialog.height()) // 2
        )

        layout = QVBoxLayout(dialog)

        # Header cu informații
        label = QLabel(f"Selectează tema dorită din cele {len(self.theme_manager.themes)} disponibile:")
        label.setStyleSheet("font-size: 11pt; font-weight: bold; margin: 10px;")
        layout.addWidget(label)

        # Label cu tema curentă
        current_label = QLabel(f"Tema curentă: {self.theme_manager.get_theme_name()}")
        current_label.setStyleSheet("font-size: 10pt; color: #666; margin-left: 10px;")
        layout.addWidget(current_label)

        # Lista cu teme organizată pe categorii
        theme_list = QListWidget()

        # Grupare pe categorii
        categories = {
            "clasic": "🎭 Clasice"
        }

        for cat_key, cat_name in categories.items():
            # Adaugă header pentru categorie
            theme_list.addItem(f"───── {cat_name} ─────")

            # Adaugă temele din categoria respectivă
            for i, theme in enumerate(self.theme_manager.themes):
                if theme.get("category", "clasic") == cat_key:
                    theme_list.addItem(f"  {i + 1:2d}. {theme['name']}")

        theme_list.setCurrentRow(self._find_theme_row(self.theme_manager.current_theme))

        theme_list.setStyleSheet("""
            QListWidget {
                font-size: 10pt;
                padding: 5px;
                background-color: rgba(255, 255, 255, 230);
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: rgba(59, 130, 246, 200);
                color: white;
                border-radius: 3px;
            }
        """)
        layout.addWidget(theme_list)

        # Butoane
        button_layout = QHBoxLayout()

        ok_btn = QPushButton("✅ Aplică Tema")
        cancel_btn = QPushButton("❌ Anulează")

        for btn in [ok_btn, cancel_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px 16px;
                    font-size: 10pt;
                    border-radius: 5px;
                    font-weight: bold;
                }
            """)

        ok_btn.setStyleSheet(ok_btn.styleSheet() + """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(34, 197, 94, 200), stop:1 rgba(22, 163, 74, 220));
                color: white;
                border: 1px solid rgba(22, 163, 74, 180);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 222, 128, 180), stop:1 rgba(34, 197, 94, 200));
            }
        """)

        cancel_btn.setStyleSheet(cancel_btn.styleSheet() + """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(239, 68, 68, 200), stop:1 rgba(220, 38, 38, 220));
                color: white;
                border: 1px solid rgba(185, 28, 28, 180);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(248, 113, 113, 180), stop:1 rgba(239, 68, 68, 200));
            }
        """)

        # Funcții pentru butoane
        def on_theme_change():
            """Preview real-time când se schimbă selecția"""
            current_item = theme_list.currentItem()
            if current_item and not current_item.text().startswith("─────"):
                try:
                    # Extrage indexul temei din text
                    theme_text = current_item.text().strip()
                    if ". " in theme_text:
                        theme_index = int(theme_text.split(".")[0].strip()) - 1
                        if 0 <= theme_index < len(self.theme_manager.themes):
                            # Aplică tema temporar pentru preview
                            old_theme = self.theme_manager.current_theme
                            self.theme_manager.set_theme(theme_index)
                            self._apply_modern_styling()
                            self._update_all_buttons()

                            # Actualizează labelul cu tema curentă
                            current_label.setText(f"Preview: {self.theme_manager.get_theme_name()}")
                except Exception as e:
                    print(f"Eroare preview: {e}")

        def apply_theme():
            """Aplică tema selectată"""
            current_item = theme_list.currentItem()
            if current_item and not current_item.text().startswith("─────"):
                try:
                    theme_text = current_item.text().strip()
                    if ". " in theme_text:
                        theme_index = int(theme_text.split(".")[0].strip()) - 1
                        if 0 <= theme_index < len(self.theme_manager.themes):
                            self.theme_manager.set_theme(theme_index)
                            new_theme = self.theme_manager.get_theme_name()

                            self._apply_modern_styling()
                            self._update_all_buttons()

                            print(f"🎨 Tema aplicată: '{new_theme}'")

                            QMessageBox.information(dialog, "Tema Aplicată",
                                                    f"Tema '{new_theme}' a fost aplicată și salvată.\n\nNoua temă va fi păstrată la următoarea pornire a aplicației.")
                except Exception as e:
                    print(f"Eroare la aplicarea temei: {e}")
            dialog.accept()

        # Conectează semnalele
        theme_list.currentItemChanged.connect(lambda: on_theme_change())
        ok_btn.clicked.connect(apply_theme)
        cancel_btn.clicked.connect(dialog.reject)

        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        # Instrucțiuni
        info_label = QLabel("💡 Navighează prin liste pentru preview real-time ")
        info_label.setStyleSheet("font-size: 9pt; color: #666; margin: 5px; font-style: italic;")
        layout.addWidget(info_label)

        dialog.exec_()

    def _find_theme_row(self, theme_index):
        """Găsește rândul temei în lista organizată pe categorii"""
        row = 0
        categories = {"clasic": "🎭 Clasice"}

        for category in categories:
            row += 1  # Pentru header-ul categoriei
            for i, theme in enumerate(self.theme_manager.themes):
                if theme.get("category", "clasic") == category:
                    if i == theme_index:
                        return row
                    row += 1
        return 0

    def _update_all_buttons(self):
        """Actualizează stilul tuturor butoanelor"""
        for button in self.menu_buttons.values():
            if isinstance(button, ModernButton):
                button.update_style()

        for button in self.submenu_buttons:
            if isinstance(button, ModernSubmenuButton):
                button.update_style()

        # Actualizează și toggle-ul de monedă
        if hasattr(self, 'currency_toggle'):
            self.currency_toggle._update_display()

    def animate_transition_to(self, widget):
        """Animație modernă pentru tranziții"""
        if widget == self.content_area.currentWidget():
            return

        current_widget = self.content_area.currentWidget()
        if current_widget:
            current_widget.hide()

        self.content_area.setCurrentWidget(widget)
        widget.show()

        widget.setWindowOpacity(0.0)
        self.fade_animation = QPropertyAnimation(widget, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.start()

    def open_calculator_window(self):
        """Deschide calculatorul"""
        if self.calculator_window is None or not self.calculator_window.isVisible():
            self.calculator_window = CalculatorWindow(self)
            self.calculator_window.show()
        else:
            self.calculator_window.raise_()
            self.calculator_window.activateWindow()

    def open_imprumuturi_noi_window(self):
        """Deschide fereastra pentru Împrumuturi Noi"""
        if self.imprumuturi_noi_window is None or not self.imprumuturi_noi_window.isVisible():
            self.imprumuturi_noi_window = ImprumuturiNoiWidget(self)
            self.imprumuturi_noi_window.show()
        else:
            self.imprumuturi_noi_window.raise_()
            self.imprumuturi_noi_window.activateWindow()

    def keyPressEvent(self, event):
        """Interceptare taste la nivel de fereastră principală"""
        # Interceptare F12 pentru comutare către Împrumuturi Noi
        if event.key() == Qt.Key_F12:
            try:
                # Verifică dacă fereastra Împrumuturi Noi există și este ascunsă
                if self.imprumuturi_noi_window is not None and not self.imprumuturi_noi_window.isVisible():
                    # Folosește QTimer pentru activare sigură
                    QTimer.singleShot(50, self._activate_imprumuturi_window)
                    event.accept()
                    return
            except Exception as e:
                print(f"Eroare la comutare către Împrumuturi Noi: {e}")

        super().keyPressEvent(event)

    def _activate_imprumuturi_window(self):
        """Metodă helper pentru activarea ferestrei Împrumuturi Noi"""
        try:
            if self.imprumuturi_noi_window is not None:
                self.imprumuturi_noi_window.show()
                self.imprumuturi_noi_window.raise_()
                self.imprumuturi_noi_window.activateWindow()
        except Exception as e:
            print(f"Eroare la activarea ferestrei Împrumuturi Noi: {e}")

    def setup_shortcuts(self):
        """Configurează scurtăturile complete pentru meniul lateral"""
        shortcuts = {
            "Actualizări": "Alt+A",
            "Vizualizări": "Alt+V",
            "Listări": "Alt+L",
            "Salvări": "Alt+S",
            "Împrumuturi Noi": "Alt+I",
            "Calcule": "Ctrl+Alt+C",
            "CAR DBF Converter": "Ctrl+Alt+D",
            "Conversie RON->EUR": "Ctrl+Alt+R",
            "Optimizare baze": "Alt+O",
            "Generare lună": "Alt+G",
            "Selector temă": "Alt+T",
            "Versiune": "Alt+R",
            "Ieșire": "Alt+Q"
        }

        for menu_text, key_sequence in shortcuts.items():
            # Găsește butonul corespunzător în meniu
            button = None
            for btn in self.menu_buttons.values():
                if menu_text in btn.text():
                    button = btn
                    break

            if button and key_sequence:
                shortcut = QShortcut(QKeySequence(key_sequence), self)
                shortcut.activated.connect(button.click)
                print(f"✅ Scurtătură configurată: {key_sequence} -> {menu_text}")

        # Scurtătură specială pentru F12 (Împrumuturi Noi)
        f12_shortcut = QShortcut(QKeySequence("F12"), self)
        f12_shortcut.activated.connect(self.open_imprumuturi_noi_window)

    def _get_widget_class(self, text):
        """Maparea simplificată - alege widget-ul corect în funcție de monedă"""
        widget_map = {
            "Adăugare membru": AdaugareMembruWidget,
            "Sume lunare": SumeLunareWidget,
            "Lichidare membru": LichidareMembruWidget,
            "Ștergere membru": StergereMembruWidget,
            "Dividende": DividendeWidget,
            "Situație lunară": VizualizareLunaraWidget,
            "Situație trimestrială": VizualizareTrimestrialaWidget,
            "Situație anuală": VizualizareAnualaWidget,
            "Verificare fișe": VerificareFiseWidget,
            "Afișare membri inactivi": MembriLichidatiWidget,
            "Listări": self._get_listari_widget_class
        }

        # Pentru Listări, alege widget-ul corect în funcție de monedă
        if text == "Listări":
            return self._get_listari_widget_class()

        widget_class = widget_map.get(text)
        if not widget_class:
            QMessageBox.critical(self, "Eroare", f"Widget pentru '{text}' nu este definit.")
            return None
        return widget_class

    def _get_listari_widget_class(self):
        """Returnează clasa corectă pentru Listări în funcție de monedă"""
        if self.currency_logic.get_current_currency() == "EUR":
            return ListariEURWidget
        else:
            return ListariWidget

    def closeEvent(self, event):
        """Cleanup la închiderea aplicației"""

        # Închide ferestrele deschise la ieșire
        if self.calculator_window:
            self.calculator_window.close()
        if self.imprumuturi_noi_window:
            self.imprumuturi_noi_window.close()

        reply = QMessageBox.question(self, 'Confirmare Ieșire',
                                     "Sunteți sigur că doriți să închideți aplicația?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    # Setări pentru efecte mai bune
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    try:
        window = CARApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"EROARE CRITICĂ la pornirea aplicației: {e}")
        QMessageBox.critical(None, "Eroare Critică", f"Aplicația nu poate porni:\n{e}")
        sys.exit(1)