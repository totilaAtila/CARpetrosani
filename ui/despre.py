# -*- coding: utf-8 -*-
"""
Despre aplicația CAR Petroșani
Versiune modernizată - interfață profesională slick
Fără emoji, design clean, acordeon modern
"""

import sys
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QScrollArea, QWidget, QPushButton,
    QHBoxLayout, QFrame, QApplication
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont

# --- Configurare Cale Resurse ---
try:
    if getattr(sys, 'frozen', False):
        BASE_RESOURCE_PATH = os.path.dirname(sys.executable)
    else:
        current_script_path = os.path.abspath(__file__)
        ui_directory = os.path.dirname(current_script_path)
        BASE_RESOURCE_PATH = os.path.dirname(ui_directory)
except Exception as e:
    print(f"Eroare la configurarea căilor în despre.py: {e}")

# --- Date Aplicație ---
CURRENT_VERSION = "FINALA"

CHANGELOG = {
    "BETA2": [
        "Adăugare interfață pastelată modernă",
        "Modul de introducere membru nou complet funcțional",
        "Optimizări majore ale interfeței pentru redimensionare",
        "Implementare validări centralizate"
    ],
    "BETA3": [
        "Meniu 'Generare lună' cu opțiuni avansate (selectare, ștergere, suprascriere)",
        "Refactorizare module pentru performanță și claritate",
        "Buton 'Împrumut nou' cu estimare automată dobândă",
        "Statistici detaliate despre restanțe și lichidări în timp real",
        "Numerotare automată și export rapid chitanțe",
        "Manual interactiv extins cu descrieri detaliate"
    ],
    "BETA4": [
        "Corectare căi fonturi DejaVu pentru funcționare după împachetare",
        "Export Excel în module vizualizare",
        "Sortare date prin click pe antet coloane",
        "Fixare antet în timpul scrollului în Excel",
        "Uniformizare stil între module",
        "Dialog-uri stilizate cu efecte hover",
        "Marcare vizuală împrumuturi noi și achitate"
    ],
    "BETA5": [
        "Rezolvare erori critice procesare dividende ianuarie",
        "Îmbunătățire calcul dobândă lichidări anticipate",
        "Corectare afișare membri inactivi perioade extinse",
        "Optimizări performanță baze de date mari",
        "Corectare format date financiare în PDF",
        "Compatibilitate îmbunătățită Windows nou",
        "Validări suplimentare prevenire inconsistențe"
    ],
    "BETA6": [
        "Suport complet dividende la începutul anului",
        "Îmbunătățire calcul dobândă împrumuturi achitate la lichidare",
        "Corectare calcul total plată chitanțe",
        "Optimizare export Excel cu antet fix",
        "Corecție rată împrumut moștenită după lichidare",
        "Dialog-uri confirmare stilizate modern",
        "Uniformizare interfață module vizualizare"
    ],
    "BETA7": [
        "Configurare externă dobândă prin config_dobanda.json",
        "Sistem de recalculare automată solduri",
        "Îmbunătățire detecție împrumuturi noi",
        "Optimizare performanță module mari",
        "Calculator dobândă la zi pentru lichidări"
    ],
    "BETA8": [
        "Sistem avansat generare chitanțe PDF batch",
        "Dialog-uri non-blocking asincrone",
        "Deschidere PDF în thread separat",
        "Jurnal activitate cu font mărit la 9pt",
        "State machine pentru generare PDF",
        "Auto-recovery UI la probleme neașteptate",
        "Feedback continuu progres (la 10 chitanțe)",
        "Optimizare memorie și cleanup automat",
        "Calculator separat independent complet funcțional"
    ],
    "FINALA": [
        "Sistem dual-currency RON/EUR cu monkey patching",
        "Widget conversie definitivă RON→EUR conform UE",
        "Toggle currency în bara principală",
        "Protecție baze RON doar-citire",
        "Clonare automată baze EUR cu validare",
        "CAR DBF Converter pentru sisteme legacy",
        "Sistem de recalculare complete solduri",
        "Optimizare baze cu indexare automată",
        "20 teme profesionale moderne",
        "Interfață slick fără elemente decorative excesive"
    ]
}

# Manual Utilizare - Structură Acordeon Modern
MANUAL_STRUCTURE = {
    "Actualizări": {
        "descriere": "Operațiuni de modificare și actualizare date membri",
        "submeniuri": {
            "Adăugare membru": {
                "descriere": "Înregistrarea unui membru nou în sistem cu validare completă a datelor",
                "functionalitati": [
                    "Introducere date identificare: nume, prenume, domiciliu",
                    "Atribuire automată număr fișă unic",
                    "Validare format CNP și verificare duplicat",
                    "Setare cotizație standard lunară",
                    "Înregistrare dată înscriere cu calendar",
                    "Salvare automată în MEMBRII.db și DEPCRED.db"
                ],
                "note": "Sistemul verifică automat dacă numărul de fișă există deja și previne duplicatele"
            },
            "Sume lunare": {
                "descriere": "Gestionarea tranzacțiilor lunare pentru fiecare membru cu calcule automate",
                "functionalitati": [
                    "Afișare istoric complet tranzacții membru",
                    "Adăugare/modificare tranzacții: împrumuturi, rate, cotizații, retrageri",
                    "Calcul automat solduri împrumuturi și depuneri",
                    "Buton 'Împrumut nou' cu calculator estimativ rate",
                    "Calculator dobândă la zi pentru lichidări complete",
                    "Detecție automată împrumuturi noi în tabel (marcaj vizual)",
                    "Recalculare automată solduri după modificări",
                    "Validări matematice stricte pentru conformitate"
                ],
                "note": "Modulul include protecții împotriva erorilor de introducere și recalculează automat toate soldurile impactate"
            },
            "Lichidare membru": {
                "descriere": "Procesarea lichidării complete a unui membru activ",
                "functionalitati": [
                    "Calcul automat sold final cu dobândă la zi",
                    "Generare automată chitanță lichidare PDF",
                    "Mutare automată membru din ACTIVI în LICHIDATI",
                    "Păstrare istoric complet în DEPCRED.db",
                    "Blocare prevenire lichidări duplicate",
                    "Validare matematică sold înainte de lichidare"
                ],
                "note": "Lichidarea este finală și nu poate fi anulată. Asigurați-vă că toate calculele sunt corecte"
            },
            "Ștergere membru": {
                "descriere": "Eliminarea definitivă a unui membru din toate bazele de date",
                "functionalitati": [
                    "Dialog confirmare dublă pentru siguranță",
                    "Ștergere din toate bazele: MEMBRII, DEPCRED, ACTIVI, INACTIVI",
                    "Verificare că membrul nu are sold activ",
                    "Jurnal complet al operației de ștergere",
                    "Opțiune anulare în orice moment"
                ],
                "note": "Operație IREVERSIBILĂ. Folosiți doar pentru corecții erori grave de introducere"
            },
            "Dividende": {
                "descriere": "Atribuirea dividendelor anuale la începutul fiecărui an pentru toți membrii activi",
                "functionalitati": [
                    "Selectare an pentru distribuire dividende",
                    "Calcul automat pe bază formula configurabilă",
                    "Aplicare automată la toți membrii activi",
                    "Validare că dividende nu au fost aplicate deja",
                    "Raportare sumă totală distribuită",
                    "Jurnal operații cu timestamp"
                ],
                "note": "Dividendele se aplică o singură dată pe an, de obicei în ianuarie"
            }
        }
    },
    "Vizualizări": {
        "descriere": "Rapoarte și analize detaliate situație financiară",
        "submeniuri": {
            "Situație lunară": {
                "descriere": "Raport detaliat pentru o lună specifică cu toate tranzacțiile",
                "functionalitati": [
                    "Selectare lună și an din calendar",
                    "Tabel complet: membru, împrumuturi, rate, cotizații, solduri",
                    "Totalizare automată pe coloane",
                    "Sortare date prin click pe antet",
                    "Export Excel cu formatare profesională",
                    "Filtrare opțională după criterii"
                ],
                "note": "Antetul rămâne fix la scroll pentru referință ușoară"
            },
            "Situație trimestrială": {
                "descriere": "Vizualizare agregată pe 3 luni consecutive",
                "functionalitati": [
                    "Selectare trimestru și an",
                    "Agregare automată date pe 3 luni",
                    "Calcul medii și totale trimestru",
                    "Export Excel cu subtotale",
                    "Comparații între luni din trimestru"
                ],
                "note": "Util pentru analize tendințe pe termen mediu"
            },
            "Situație anuală": {
                "descriere": "Raport complet pentru un an întreg cu toate operațiunile",
                "functionalitati": [
                    "Selectare an fiscal",
                    "Totalizare anuală toate categoriile",
                    "Statistici anuale: împrumuturi, rate, cotizații",
                    "Export Excel cu grafice automate",
                    "Comparație cu ani anteriori (opțional)"
                ],
                "note": "Esențial pentru raportări anuale și audit financiar"
            },
            "Verificare fișe": {
                "descriere": "Verificarea integrității și consistenței datelor pentru toți membrii",
                "functionalitati": [
                    "Scanare automată toate fișele membre",
                    "Detectare discrepanțe matematice solduri",
                    "Identificare înregistrări lipsa",
                    "Raport erori cu detalii localizare",
                    "Sugestii automate corecții",
                    "Export raport verificare"
                ],
                "note": "Recomandabil de rulat lunar pentru asigurarea calității datelor"
            },
            "Afișare membri inactivi": {
                "descriere": "Lista membrilor care nu au efectuat plăți de cotizație timp îndelungat",
                "functionalitati": [
                    "Configurare prag luni inactivitate",
                    "Listă automată membri inactivi cu detalii",
                    "Afișare ultimă lună plată cotizație",
                    "Calcul luni inactivitate pentru fiecare",
                    "Export listă pentru contactare"
                ],
                "note": "Util pentru menținerea bazei active de membri și recuperare restanțe"
            }
        }
    },
    "Listări": {
        "descriere": "Generare chitanțe și documente oficiale pentru plăți",
        "functionalitati": [
            "Selectare lună și an pentru listare",
            "Generare automată chitanțe PDF pentru toți membrii cu plăți",
            "Numerotare automată chitanțe secvențial",
            "Format profesional conform standarde contabile",
            "Salvare automată în director dedicat",
            "Deschidere directă PDF după generare",
            "Sistem batch processing pentru volume mari",
            "Progress bar în timp real cu feedback la fiecare 10 chitanțe",
            "Posibilitate de resetare numărul chitanței la 1 atunci când numărul de caractere depășește chenarul de tipărire"
        ],
        "note": "Sistemul funcționează în modul dual-currency (RON/EUR) automat conform monedei active"
    },
    "Generare lună": {
        "descriere": "Crearea automată lunii noi cu preluare solduri din luna anterioară",
        "functionalitati": [
            "Selectare lună și an nouă",
            "Verificare automată existență lună",
            "Preluare solduri finale din ultima lună existentă",
            "Aplicare cotizație standard la toți membrii activi",
            "Creare înregistrări pentru toți membrii activi",
            "Opțiuni: suprascriere, ștergere, anulare",
            "Validări matematice complete înainte de generare",
            "Raportare detaliere operațiuni efectuate"
        ],
        "note": "Operație complexă - verificați atent datele înainte de confirmare. Suportă suprascriere lună existentă cu confirmare"
    },
    "Salvări": {
        "descriere": "Operațiuni backup, restaurare și întreținere baze de date",
        "submeniuri": {
            "Backup Complet": {
                "descriere": "Creare copie siguranță toate bazele de date",
                "functionalitati": [
                    "Backup automat toate fișierele .db",
                    "Creare director timestamped în 'backup_db'",
                    "Verificare integritate după backup",
                    "Afișare mărime totală backup",
                    "Păstrare istoric backups pentru restaurări",
                    "Deschidere automată folder backup în Explorer"
                ],
                "note": "Recomandabil înainte de operațiuni majore sau la finalul fiecărei luni"
            },
            "Restaurare": {
                "descriere": "Recuperare date din backup anterior",
                "functionalitati": [
                    "Selectare folder backup dorit",
                    "Previzualizare conținut backup",
                    "Restaurare selectivă sau completă",
                    "Confirmare dublă înainte de suprascriere",
                    "Verificare integritate după restaurare",
                    "Backup automat înainte de restaurare"
                ],
                "note": "ATENȚIE: Restaurarea suprascrie datele curente. Verificați data backup-ului atent"
            },
            "Ștergere An": {
                "descriere": "Eliminare definitivă date pentru un an complet",
                "functionalitati": [
                    "Selectare an pentru ștergere",
                    "Afișare statistici an (nr înregistrări, membri afectați)",
                    "Confirmare multiplă pentru siguranță",
                    "Backup automat obligatoriu înainte de ștergere",
                    "Ștergere recursivă toate lunile anului",
                    "Raport detaliat operațiuni efectuate"
                ],
                "note": "IREVERSIBIL fără backup. Folosiți doar pentru arhivare ani vechi conform politici legale"
            },
            "Verifică Integritatea": {
                "descriere": "Verificare PRAGMA integrity_check pe toate bazele",
                "functionalitati": [
                    "Scanare automată toate fișierele .db",
                    "PRAGMA integrity_check pentru fiecare DB",
                    "Detectare corupții sau inconsistențe",
                    "Raport detaliat probleme găsite",
                    "Sugestii remediere automată",
                    "Export raport verificare"
                ],
                "note": "Rulați periodic sau după crash sistem pentru asigurarea sănătății bazelor"
            }
        }
    },
    "Optimizare baze": {
        "descriere": "Optimizare și întreținere performanță baze de date",
        "functionalitati": [
            "VACUUM: Recuperare spațiu nefolosit și defragmentare",
            "ANALYZE: Actualizare statistici pentru optimizer query",
            "REINDEX: Reconstruire indexi pentru performanță maximă",
            "Creare indexi automatici pe coloane critice (NR_FISA, LUNA, ANUL)",
            "Verificare integritate referințe între tabele",
            "Raportare mărime înainte/după optimizare",
            "Progress indicator în timp real",
            "Backup automat recomandat înainte de operație"
        ],
        "note": "Recomandabil lunar sau după operațiuni majore cu volume mari. Îmbunătățește semnificativ viteza query-urilor și reduce dimensiunea fișierelor"
    },
    "Conversie RON→EUR": {
        "descriere": "Aplicarea conversiei definitive RON→EUR pentru tranziția la moneda euro",
        "stari_sistem": {
            "Perioada 1 - Pre-conversie": {
                "descriere": "Funcționare normală doar cu RON",
                "comportament": [
                    "Toggle currency INACTIV (doar RON vizibil)",
                    "Toate modulele funcționează normal cu RON",
                    "Baze originale: DEPCRED.db, MEMBRII.db, activi.db, INACTIVI.db, LICHIDATI.db",
                    "Butonul Conversie ACTIV și vizibil în meniu"
                ]
            },
            "Perioada 2 - Post-conversie": {
                "descriere": "Sistem dual-currency cu toggle RON/EUR",
                "comportament": [
                    "Toggle currency ACTIV (implicit pornește pe EUR)",
                    "Baze clonate EUR: DEPCREDEUR.db, MEMBRIIEUR.db, activiEUR.db, INACTIVIEUR.db, LICHIDATIEUR.db",
                    "Modul EUR: Citire și scriere complete în bazele EUR",
                    "Modul RON: DOAR CITIRE pentru protecție date istorice",
                    "Butonul Conversie DISPARE din meniu (conversie deja aplicată), apare anunț: Sistem în EUR",
                    "Monkey patching activ: redirectare automată apeluri DB"
                ]
            }
        },
        "proces_conversie": {
            "descriere": "Proces automat clonare și conversie conform regulilor UE",
            "etape": [
                "1. Validare schemă și integritate date toate bazele (DEPCRED, MEMBRII, ACTIVI, INACTIVI, LICHIDATI)",
                "2. Validare comprehensivă consistență membri între baze",
                "3. Obținere lock-uri exclusive pe toate bazele pentru evitare corupții",
                "4. Clonare fizică toate cele 5 baze de date cu verificare",
                "5. Conversie DEPCRED.db: toate sumele RON→EUR cu rotunjire ROUND_HALF_UP",
                "6. Conversie MEMBRII.db: cotizații standard RON→EUR",
                "7. Conversie activi.db: solduri, dividende, beneficii RON→EUR",
                "8. Clonare directă INACTIVI.db și LICHIDATI.db (fără conversie)",
                "9. Validare matematică finală: suma_totală_EUR = suma_totală_RON / curs",
                "10. Salvare configurație conversie cu timestamp și curs aplicat"
            ],
            "validari_ue": [
                "Rotunjire obligatorie ROUND_HALF_UP (conform Regulamentul CE 1103/97)",
                "Precizie 2 zecimale pentru toate sumele EUR",
                "Toleranță maximă 0.01 EUR diferență la validare finală",
                "Verificare consistență sumă totală pre și post conversie",
                "Raportare detaliate discrepanțe dacă depășesc toleranța"
            ]
        },
        "monkey_patching": {
            "descriere": "Sistem de redirectare automată apeluri către baze de date corecte",
            "mecanism": [
                "La pornire aplicație: detectare automată stare conversie",
                "Patching dinamic toate modulele UI încărcate în sys.modules",
                "Înlocuire automată căi: DEPCRED.db → DEPCREDEUR.db, etc.",
                "La toggle currency: re-patching automat și reload widget activ",
                "Protecție scriere: validare permisiuni înainte de orice operație write",
                "Mesaje informative utilizator când operații blocate în modul doar-citire"
            ],
            "avantaje": [
                "Zero modificări cod modulelor existente",
                "Compatibilitate completă înapoi cu perioada pre-conversie",
                "Comutare instant între RON și EUR fără restart",
                "Protecție automată date istorice RON",
                "Transparență completă pentru modulele business logic"
            ]
        },
        "note": "Operație IREVERSIBILĂ după aplicare. Creați backup complet OBLIGATORIU înainte. Verificați cursul RON/EUR atent - acesta va fi fix pentru toată istoria aplicației"
    },
    "CAR DBF Converter": {
        "descriere": "Utilitar conversie unidirecțională SQLite DB --> DBF pentru compatibilitate sistemul anterior Visual FoxPro",
        "functionalitati": [
            "Conversie SQLite → DBF: pentru export către sisteme vechi Visual FoxPro",
            "Sistem 'amprentă digitală' pentru tracking versiuni și modificări",
            "Validare automată structură și consistență date",
            "Support multiple tabele simultan",
            "Progress indicator pentru operațiuni mari",
            "Verificare integritate post-conversie",
            "Backup automat înainte de conversii"
        ],
        "proces_conversie": [
            "Pasul 1: Verificare fișiere sursa - detectare automată fișiere disponibile",
            "Pasul 2: Creare amprentă digitală - snapshot metadata pentru tracking",
            "Pasul 3: Conversie propriu-zisă cu validări stricte",
            "Pasul 4: Lansare Visual FoxPro pentru reindexare (opțional, doar Windows)"
        ],
        "note": "Modul opțional - disponibil doar dacă fișierul car_dbf_converter_widget.py este prezent. Util pentru migrare date sau integrare cu software legacy existent"
    },
    "Selector temă": {
        "descriere": "Personalizare interfață cu 20 teme profesionale moderne",
        "categorii": {
            "Profesional": [
                "Pure Black - negru complet pentru OLED",
                "Dark Gray - gri închis profesional",
                "Charcoal - cărbune elegant",
                "Steel Blue - albastru oțel modern"
            ],
            "Corporate": [
                "Navy Blue - albastru marin corporate",
                "Business Gray - gri business clasic",
                "Corporate Blue - albastru corporatist",
                "Executive Dark - întuneric executive"
            ],
            "Vibrant": [
                "Ocean Blue - albastru ocean vibrant",
                "Forest Green - verde pădure natural",
                "Purple Night - violet noapte profund",
                "Ruby Red - roșu rubin elegant"
            ],
            "Neutral": [
                "Warm Gray - gri cald neutru",
                "Cool Slate - ardezie rece profesional",
                "Beige Professional - bej profesional cald",
                "Taupe Modern - taupe modern sofisticat"
            ]
        },
        "functionalitati": [
            "Previzualizare live la hover pe temă",
            "Aplicare instant fără restart",
            "Salvare automată preferință temă",
            "Filtrare teme după categorie",
            "Design consistent pe toate modulele"
        ],
        "note": "Tema se aplică imediat la toate componentele aplicației pentru experiență vizuală unitară"
    },
    "Calcule": {
        "descriere": "Calculator științific separat pentru calcule financiare și matematice",
        "functionalitati": [
            "Fereastră independentă 450x350px",
            "Operații de bază: +, -, *, /",
            "Funcții științifice: √ (radical), x² (pătrat), 1/x (reciprocă)",
            "Funcții speciale: % (procente), ± (schimbare semn)",
            "Operații în lanț complexe (ex: 2+3*4=20)",
            "Repetare automată ultimă operație prin apăsare repetată '='",
            "Control complet tastatură: cifre, operatori, Enter (=), Esc (Clear), Backspace",
            "Istoric complet sesiune cu timestamp",
            "Export istoric în fișier text",
            "Gestionare erori: împărțire la zero, overflow, radical negativ",
            "Butoane color-coded: albastru (=), roșu (operatori), portocaliu (științifice)",
            "Layout 70% calcul, 30% istoric pentru eficiență"
        ],
        "utilizare": [
            "Deschidere: Click buton 'Calcule' din bara principală",
            "Rămâne deschis și funcțional pe toată durata sesiunii",
            "Se închide automat la închiderea aplicației principale",
            "Perfect pentru calcule dobândă, rate, procente în paralel cu lucrul în CAR"
        ],
        "note": "Calculator complet independent - nu interferează cu aplicația principală și permite multitasking eficient"
    },
    "Versiune": {
        "descriere": "Informații aplicație, istoric versiuni și manual utilizare complet",
        "sectiuni": [
            "Informații versiune curentă cu număr și dată",
            "Istoric complet schimbări de la BETA2 la FINALA",
            "Manual detaliat toate meniurile și submeniurile",
            "Explicații funcționalități noi (monkey patching, dual-currency)",
            "Ghid rapid operațiuni frecvente",
            "Informații tehnice sistem dual-currency"
        ],
        "note": "Documentație completă actualizată la zi cu toate funcționalitățile aplicației"
    }
}


class AccordionSection(QWidget):
    """Secțiune acordeon modernă slick - stil profesional clean"""

    def __init__(self, title, content_widget, parent=None):
        super().__init__(parent)
        self.content_widget = content_widget
        self.is_expanded = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header clickable
        self.header = QPushButton(f"▶  {title}")
        self.header.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.header.setStyleSheet("""
            QPushButton {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 12px 16px;
                text-align: left;
                color: #2c3e50;
            }
            QPushButton:hover {
                background: #e9ecef;
                border-color: #adb5bd;
            }
            QPushButton:pressed {
                background: #dee2e6;
            }
        """)
        self.header.setCursor(Qt.PointingHandCursor)
        self.header.clicked.connect(self.toggle)
        layout.addWidget(self.header)

        # Container pentru conținut
        self.content_container = QFrame()
        self.content_container.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #dee2e6;
                border-top: none;
                border-radius: 0 0 6px 6px;
                padding: 16px;
            }
        """)
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.addWidget(content_widget)
        self.content_container.setMaximumHeight(0)
        self.content_container.setVisible(False)
        layout.addWidget(self.content_container)

        # Animație pentru expand/collapse
        self.animation = QPropertyAnimation(self.content_container, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)

    def toggle(self):
        """Toggle expand/collapse cu animație"""
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()

    def expand(self):
        """Expandează secțiunea"""
        self.is_expanded = True
        self.header.setText(self.header.text().replace("▶", "▼"))

        # Calculează înălțimea necesară
        self.content_widget.adjustSize()
        target_height = self.content_widget.sizeHint().height() + 32

        self.animation.setStartValue(0)
        self.animation.setEndValue(target_height)
        self.content_container.setVisible(True)
        self.animation.start()

    def collapse(self):
        """Colapsează secțiunea"""
        self.is_expanded = False
        self.header.setText(self.header.text().replace("▼", "▶"))

        self.animation.setStartValue(self.content_container.maximumHeight())
        self.animation.setEndValue(0)
        self.animation.finished.connect(lambda: self.content_container.setVisible(False))
        self.animation.start()


class DespreWidget(QDialog):
    """Dialog Despre - Design profesional modern slick"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CAR Petroșani - Informații Aplicație")
        self.setMinimumSize(900, 700)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header compact profesional
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2c3e50, stop:1 #3498db);
                border-radius: 8px;
                padding: 16px;
            }
        """)

        header_layout = QHBoxLayout(header_frame)
        header_layout.setSpacing(20)

        # Titlu
        title_label = QLabel("CAR Petroșani")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        header_layout.addWidget(title_label)

        # Versiune
        version_label = QLabel(f"Versiunea {CURRENT_VERSION}")
        version_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        version_label.setStyleSheet("color: #ecf0f1;")
        header_layout.addWidget(version_label)

        header_layout.addStretch()

        main_layout.addWidget(header_frame)

        # Tab-uri principale
        tabs_frame = QFrame()
        tabs_layout = QHBoxLayout(tabs_frame)
        tabs_layout.setSpacing(10)

        self.btn_ghid = self._create_tab_button("Ghid Utilizare")
        self.btn_manual = self._create_tab_button("Manual Tehnic")
        self.btn_changelog = self._create_tab_button("Istoric Versiuni")
        self.btn_tech = self._create_tab_button("Info Tehnice")
        self.btn_shortcut = self._create_tab_button("Scurtături Tastatură")

        self.btn_ghid.clicked.connect(lambda: self._switch_tab(0))
        self.btn_manual.clicked.connect(lambda: self._switch_tab(1))
        self.btn_changelog.clicked.connect(lambda: self._switch_tab(2))
        self.btn_tech.clicked.connect(lambda: self._switch_tab(3))
        self.btn_shortcut.clicked.connect(lambda: self._switch_tab(4))

        tabs_layout.addWidget(self.btn_ghid)
        tabs_layout.addWidget(self.btn_manual)
        tabs_layout.addWidget(self.btn_changelog)
        tabs_layout.addWidget(self.btn_tech)
        tabs_layout.addWidget(self.btn_shortcut)

        tabs_layout.addStretch()

        main_layout.addWidget(tabs_frame)

        # Scroll area pentru conținut
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background: white;
            }
        """)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(10)
        self.content_layout.setContentsMargins(10, 10, 10, 10)

        scroll.setWidget(self.content_widget)
        main_layout.addWidget(scroll)

        # Buton închidere
        close_btn = QPushButton("Închide")
        close_btn.setFont(QFont("Segoe UI", 10))
        close_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        close_btn.clicked.connect(self.close)
        close_btn.setMaximumWidth(150)

        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_btn)
        main_layout.addLayout(close_layout)

        # Încarcă tab implicit
        self._switch_tab(0)

    def _create_tab_button(self, text):
        """Creează buton tab modern"""
        btn = QPushButton(text)
        btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn.setStyleSheet("""
            QPushButton {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 10px 20px;
                color: #495057;
            }
            QPushButton:hover {
                background: #e9ecef;
            }
            QPushButton:checked {
                background: #3498db;
                color: white;
                border-color: #2980b9;
            }
        """)
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        return btn

    def _switch_tab(self, tab_index):
        """Comută între tab-uri"""
        # Resetează toate butoanele
        self.btn_ghid.setChecked(False)
        self.btn_manual.setChecked(False)
        self.btn_changelog.setChecked(False)
        self.btn_tech.setChecked(False)
        self.btn_shortcut.setChecked(False)

        # Curăță layout-ul
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Încarcă conținutul corespunzător
        if tab_index == 0:
            self.btn_ghid.setChecked(True)
            self._load_ghid_utilizare()
        elif tab_index == 1:
            self.btn_manual.setChecked(True)
            self._load_manual()
        elif tab_index == 2:
            self.btn_changelog.setChecked(True)
            self._load_changelog()
        elif tab_index == 3:
            self.btn_tech.setChecked(True)
            self._load_tech_info()
        elif tab_index == 4:
            self.btn_shortcut.setChecked(True)
            self._load_shortcuts()

    def _load_ghid_utilizare(self):
        """Încarcă ghidul de utilizare pentru utilizatori non-tehnici"""
        intro_label = QLabel(
            "<b>Ghid de Utilizare CAR Petroșani</b><br>"
            "Ghid complet pentru utilizarea aplicației, destinat utilizatorilor care nu au cunoștințe de programare."
        )
        intro_label.setWordWrap(True)
        intro_label.setStyleSheet("padding: 10px; background: #d4edda; border-radius: 6px; color: #155724;")
        self.content_layout.addWidget(intro_label)

        # Secțiunea 1: Introducere
        intro_frame = self._create_section_frame("Despre Aplicație")
        intro_layout = QVBoxLayout(intro_frame)

        intro_text = QLabel(
            "CAR Petroșani este o aplicație desktop pentru gestionarea Casei de Ajutor Reciproc Petroșani. "
            "Aplicația vă permite să gestionați membri, plăți lunare, împrumuturi, dividende și să generați rapoarte și chitanțe PDF."
        )
        intro_text.setWordWrap(True)
        intro_text.setStyleSheet("color: #495057; padding: 8px;")
        intro_layout.addWidget(intro_text)
        self.content_layout.addWidget(intro_frame)

        # Secțiunea 2: Operațiuni Comune
        operations_frame = self._create_section_frame("Operațiuni Comune")
        operations_layout = QVBoxLayout(operations_frame)

        operations_html = """
        <p style='margin-bottom: 15px;'><b>1. Adăugare Membru Nou</b></p>
        <ul style='margin: 5px 0 15px 20px;'>
            <li>Click pe butonul <b>Actualizări</b> din meniul lateral (sau apăsați <b>Alt+A</b>)</li>
            <li>Selectați <b>Adăugare membru</b></li>
            <li>Completați datele membrului: nume, prenume, CNP, domiciliu, funcție</li>
            <li>Sistemul va atribui automat un număr de fișă unic</li>
            <li>Click pe <b>Salvare</b> pentru a înregistra membrul</li>
        </ul>

        <p style='margin-bottom: 15px;'><b>2. Introducere Plăți Lunare</b></p>
        <ul style='margin: 5px 0 15px 20px;'>
            <li>Click pe <b>Actualizări</b> → <b>Sume lunare</b> (sau <b>Alt+A</b>)</li>
            <li>Căutați membrul folosind numărul de fișă sau numele</li>
            <li>Introduceți datele pentru luna selectată: rate, cotizații, împrumuturi noi</li>
            <li>Sistemul va calcula automat soldurile</li>
            <li>Click pe <b>Salvare</b> pentru a înregistra tranzacția</li>
        </ul>

        <p style='margin-bottom: 15px;'><b>3. Generare Lună Nouă</b></p>
        <ul style='margin: 5px 0 15px 20px;'>
            <li>Click pe <b>Generare lună</b> (sau apăsați <b>Alt+G</b>)</li>
            <li>Selectați luna și anul pentru care doriți să generați înregistrările</li>
            <li>Sistemul va prelua automat soldurile din luna anterioară</li>
            <li>Aplicați cotizația standard pentru toți membrii activi</li>
            <li>Click pe <b>Generează</b> pentru a finaliza operația</li>
        </ul>

        <p style='margin-bottom: 15px;'><b>4. Generare Chitanțe PDF</b></p>
        <ul style='margin: 5px 0 15px 20px;'>
            <li>Click pe <b>Listări</b> (sau apăsați <b>Alt+L</b>)</li>
            <li>Selectați luna și anul pentru care doriți să generați chitanțele</li>
            <li>Setați numărul chitanței inițial (de exemplu: 1001)</li>
            <li>Configurați numărul de chitanțe per pagină (implicit: 10)</li>
            <li>Click pe <b>Preview</b> pentru a verifica datele</li>
            <li>Click pe <b>Tipărește PDF</b> pentru a genera fișierul PDF</li>
            <li>PDF-ul va fi salvat automat și deschis pentru vizualizare</li>
        </ul>

        <p style='margin-bottom: 15px;'><b>5. Vizualizare Rapoarte</b></p>
        <ul style='margin: 5px 0 15px 20px;'>
            <li>Click pe <b>Vizualizări</b> (sau apăsați <b>Alt+V</b>)</li>
            <li>Selectați tipul de raport: <b>Situație lunară</b>, <b>Situație trimestrială</b> sau <b>Situație anuală</b></li>
            <li>Alegeți perioada dorită (lună, trimestru sau an)</li>
            <li>Sistemul va afișa toate tranzacțiile și soldurile pentru perioada selectată</li>
            <li>Puteți exporta datele în format Excel prin butonul <b>Export Excel</b></li>
        </ul>
        """
        operations_label = QLabel(operations_html)
        operations_label.setWordWrap(True)
        operations_label.setTextFormat(Qt.RichText)
        operations_label.setStyleSheet("color: #495057;")
        operations_layout.addWidget(operations_label)
        self.content_layout.addWidget(operations_frame)

        # Secțiunea 3: Conversie RON - EUR
        currency_frame = self._create_section_frame("Conversie RON → EUR (Opțional)")
        currency_layout = QVBoxLayout(currency_frame)

        currency_html = """
        <p style='margin-bottom: 10px;'>Aplicația suportă conversie completă de la moneda RON la EUR. Această operație este <b>IREVERSIBILĂ</b>
        și trebuie efectuată cu atenție maximă.</p>

        <p style='margin-bottom: 10px;'><b>Pași pentru conversie:</b></p>
        <ul style='margin: 5px 0 15px 20px;'>
            <li><b>Înainte de conversie:</b> Creați un backup complet al bazelor de date (Meniu <b>Salvări</b> → <b>Backup Complet</b>)</li>
            <li>Apăsați <b>Ctrl+Alt+R</b> sau click pe butonul <b>Conversie RON→EUR</b></li>
            <li>Verificați cursul de schimb afișat (implicit: 4.9755 RON/EUR)</li>
            <li>Confirmați operația în dialogul de avertizare</li>
            <li>Sistemul va crea baze de date noi cu sufix EUR (MEMBRIIEUR.db, DEPCREDEUR.db, etc.)</li>
            <li>După conversie, puteți comuta între RON și EUR folosind toggle-ul din interfață</li>
        </ul>

        <p style='margin-bottom: 10px;'><b>După conversie:</b></p>
        <ul style='margin: 5px 0 15px 20px;'>
            <li><b>Modul RON:</b> Doar citire (nu puteți modifica datele RON)</li>
            <li><b>Modul EUR:</b> Citire și scriere completă (toate operațiunile sunt permise)</li>
            <li>Toggle între RON și EUR se face instant, fără restart aplicație</li>
        </ul>
        """
        currency_label = QLabel(currency_html)
        currency_label.setWordWrap(True)
        currency_label.setTextFormat(Qt.RichText)
        currency_label.setStyleSheet("color: #495057;")
        currency_layout.addWidget(currency_label)

        # Notă de avertizare
        warning_label = QLabel(
            "<b>IMPORTANT:</b> Operația de conversie este IREVERSIBILĂ. "
            "Asigurați-vă că aveți un backup complet înainte de a continua."
        )
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet("""
            color: #721c24;
            background: #f8d7da;
            padding: 10px;
            border-radius: 4px;
            border-left: 4px solid #dc3545;
            margin-top: 10px;
        """)
        currency_layout.addWidget(warning_label)
        self.content_layout.addWidget(currency_frame)

        # Secțiunea 4: Backup și Salvări
        backup_frame = self._create_section_frame("Backup și Siguranța Datelor")
        backup_layout = QVBoxLayout(backup_frame)

        backup_html = """
        <p style='margin-bottom: 10px;'><b>Crearea unui backup:</b></p>
        <ul style='margin: 5px 0 15px 20px;'>
            <li>Click pe <b>Salvări</b> (sau apăsați <b>Alt+S</b>)</li>
            <li>Selectați <b>Backup Complet</b></li>
            <li>Sistemul va crea automat un director cu data curentă în folder-ul <b>backup_db</b></li>
            <li>Toate bazele de date vor fi copiate în acest director</li>
            <li>Sistemul va deschide automat folder-ul de backup după finalizare</li>
        </ul>

        <p style='margin-bottom: 10px;'><b>Restaurarea din backup:</b></p>
        <ul style='margin: 5px 0 15px 20px;'>
            <li>Click pe <b>Salvări</b> → <b>Restaurare</b></li>
            <li>Selectați folder-ul de backup din care doriți să restaurați</li>
            <li>Confirmați operația (sistemul va crea automat un backup al datelor curente înainte de restaurare)</li>
            <li>Datele vor fi restaurate și aplicația va trebui repornită</li>
        </ul>

        <p style='margin-bottom: 10px;'><b>Recomandări:</b></p>
        <ul style='margin: 5px 0 15px 20px;'>
            <li>Creați backup-uri regulate (recomandat: lunar sau înainte de operațiuni majore)</li>
            <li>Păstrați backup-urile pe un dispozitiv extern (USB, cloud, etc.)</li>
            <li>Verificați periodic integritatea bazelor de date (<b>Salvări</b> → <b>Verifică Integritatea</b>)</li>
        </ul>
        """
        backup_label = QLabel(backup_html)
        backup_label.setWordWrap(True)
        backup_label.setTextFormat(Qt.RichText)
        backup_label.setStyleSheet("color: #495057;")
        backup_layout.addWidget(backup_label)
        self.content_layout.addWidget(backup_frame)

        # Secțiunea 5: Probleme Comune
        troubleshooting_frame = self._create_section_frame("Rezolvare Probleme Comune")
        troubleshooting_layout = QVBoxLayout(troubleshooting_frame)

        troubleshooting_html = """
        <p style='margin-bottom: 10px;'><b>Aplicația nu pornește:</b></p>
        <ul style='margin: 5px 0 15px 20px;'>
            <li>Verificați că toate bazele de date (MEMBRII.db, DEPCRED.db, etc.) sunt în directorul aplicației</li>
            <li>Contactați administratorul pentru asistență tehnică</li>
        </ul>

        <p style='margin-bottom: 10px;'><b>Nu pot modifica date după conversie EUR:</b></p>
        <ul style='margin: 5px 0 15px 20px;'>
            <li>Verificați că sunteți în modul EUR (nu RON)</li>
            <li>Comutați la EUR folosind toggle-ul din interfață</li>
            <li>Modul RON este doar pentru vizualizare după conversie</li>
        </ul>

        <p style='margin-bottom: 10px;'><b>Chitanțele PDF nu au caractere românești (diacritice):</b></p>
        <ul style='margin: 5px 0 15px 20px;'>
            <li>Verificați că fișierele de font (Arial.ttf, DejaVuSans-Bold.ttf) sunt în folder-ul <b>fonts</b></li>
            <li>Fonturile trebuie să fie și în directorul rădăcină al aplicației</li>
            <li>Contactați administratorul dacă problema persistă</li>
        </ul>

        <p style='margin-bottom: 10px;'><b>Erori la generare lună nouă:</b></p>
        <ul style='margin: 5px 0 15px 20px;'>
            <li>Verificați că luna anterioară a fost generată corect</li>
            <li>Asigurați-vă că toți membrii activi au înregistrări în luna anterioară</li>
            <li>Folosiți opțiunea <b>Vizualizări</b> → <b>Afișare Membri cu Date Incomplete</b> pentru identificare probleme</li>
        </ul>
        """
        troubleshooting_label = QLabel(troubleshooting_html)
        troubleshooting_label.setWordWrap(True)
        troubleshooting_label.setTextFormat(Qt.RichText)
        troubleshooting_label.setStyleSheet("color: #495057;")
        troubleshooting_layout.addWidget(troubleshooting_label)
        self.content_layout.addWidget(troubleshooting_frame)

        # Contact și Suport
        support_frame = QFrame()
        support_frame.setStyleSheet("""
            QFrame {
                background: #cfe2ff;
                border: 1px solid #9ec5fe;
                border-radius: 6px;
                padding: 12px;
                margin: 8px 0;
            }
        """)
        support_layout = QVBoxLayout(support_frame)

        support_label = QLabel(
            "<b>Suport și Documentație:</b><br>"
            "Pentru întrebări sau probleme, consultați <b>Manual Tehnic</b> sau accesați repository-ul GitHub:<br>"
            "<a href='https://github.com/totilaAtila/C.A.R._Petrosani' style='color: #0d6efd;'>"
            "https://github.com/totilaAtila/C.A.R._Petrosani</a>"
        )
        support_label.setWordWrap(True)
        support_label.setTextFormat(Qt.RichText)
        support_label.setOpenExternalLinks(True)
        support_label.setStyleSheet("color: #084298; font-size: 10pt;")
        support_layout.addWidget(support_label)
        self.content_layout.addWidget(support_frame)

        self.content_layout.addStretch()

    def _create_section_frame(self, title):
        """Creează un frame pentru o secțiune cu titlu"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 16px;
                margin: 8px 0;
            }
        """)
        layout = QVBoxLayout(frame)

        title_label = QLabel(f"<b>{title}</b>")
        title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 8px;")
        layout.addWidget(title_label)

        return frame

    def _load_shortcuts(self):
        """Încarcă lista completă de scurtături tastatură"""
        intro_label = QLabel(
            "<b>Scurtături Tastatură</b><br>"
            "Lista completă a combinațiilor de taste pentru acces rapid la funcționalități."
        )
        intro_label.setWordWrap(True)
        intro_label.setStyleSheet("padding: 10px; background: #fff3cd; border-radius: 6px; color: #856404;")
        self.content_layout.addWidget(intro_label)

        # Secțiunea Meniu Principal
        main_menu_frame = QFrame()
        main_menu_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 16px;
                margin: 8px 0;
            }
        """)
        main_menu_layout = QVBoxLayout(main_menu_frame)

        main_menu_title = QLabel("<b>Scurtături Meniu Principal</b>")
        main_menu_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        main_menu_title.setStyleSheet("color: #2c3e50;")
        main_menu_layout.addWidget(main_menu_title)

        shortcuts_main = """
        <table style='width: 100%; border-collapse: collapse; margin: 10px 0;'>
            <tr style='background: #f8f9fa;'>
                <th style='padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6; width: 30%;'>Scurtătură</th>
                <th style='padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;'>Funcționalitate</th>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: #e9ecef; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Alt+A</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Deschide meniul <b>Actualizări</b></td>
            </tr>
            <tr style='background: #f8f9fa;'>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: #e9ecef; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Alt+V</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Deschide meniul <b>Vizualizări</b></td>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: #e9ecef; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Alt+L</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Deschide <b>Listări</b> chitanțe</td>
            </tr>
            <tr style='background: #f8f9fa;'>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: #e9ecef; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Alt+S</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Deschide meniul <b>Salvări</b></td>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: #e9ecef; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Alt+I</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Deschide <b>Împrumuturi Noi</b></td>
            </tr>
            <tr style='background: #f8f9fa;'>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: #e9ecef; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Alt+G</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Deschide <b>Generare lună</b></td>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: #e9ecef; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Alt+O</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Deschide <b>Optimizare baze</b></td>
            </tr>
            <tr style='background: #f8f9fa;'>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: #e9ecef; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Alt+T</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Deschide <b>Selector temă</b></td>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: #e9ecef; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Alt+R</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Deschide <b>Versiune</b> (acest dialog)</td>
            </tr>
            <tr style='background: #f8f9fa;'>
                <td style='padding: 8px;'><kbd style='background: #e9ecef; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Alt+Q</kbd></td>
                <td style='padding: 8px;'>Închide aplicația (<b>Ieșire</b>)</td>
            </tr>
        </table>
        """
        shortcuts_label = QLabel(shortcuts_main)
        shortcuts_label.setWordWrap(True)
        shortcuts_label.setTextFormat(Qt.RichText)
        shortcuts_label.setStyleSheet("color: #495057;")
        main_menu_layout.addWidget(shortcuts_label)

        self.content_layout.addWidget(main_menu_frame)

        # Secțiunea Scurtături Avansate
        advanced_frame = QFrame()
        advanced_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 16px;
                margin: 8px 0;
            }
        """)
        advanced_layout = QVBoxLayout(advanced_frame)

        advanced_title = QLabel("<b>Scurtături Avansate</b>")
        advanced_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        advanced_title.setStyleSheet("color: #2c3e50;")
        advanced_layout.addWidget(advanced_title)

        shortcuts_advanced = """
        <table style='width: 100%; border-collapse: collapse; margin: 10px 0;'>
            <tr style='background: #f8f9fa;'>
                <th style='padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6; width: 30%;'>Scurtătură</th>
                <th style='padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;'>Funcționalitate</th>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: #e9ecef; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Ctrl+Alt+C</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Deschide <b>Calculator</b> independent</td>
            </tr>
            <tr style='background: #f8f9fa;'>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: #e9ecef; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Ctrl+Alt+D</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Deschide <b>CAR DBF Converter</b></td>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: #e9ecef; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Ctrl+Alt+R</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Deschide <b>Conversie RON→EUR</b></td>
            </tr>
            <tr style='background: #f8f9fa;'>
                <td style='padding: 8px;'><kbd style='background: #e9ecef; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>F12</kbd></td>
                <td style='padding: 8px;'>Comută rapid către <b>Împrumuturi Noi</b> (dacă fereastră deja deschisă)</td>
            </tr>
        </table>
        """
        shortcuts_advanced_label = QLabel(shortcuts_advanced)
        shortcuts_advanced_label.setWordWrap(True)
        shortcuts_advanced_label.setTextFormat(Qt.RichText)
        shortcuts_advanced_label.setStyleSheet("color: #495057;")
        advanced_layout.addWidget(shortcuts_advanced_label)

        self.content_layout.addWidget(advanced_frame)

        # Secțiunea Modul Sume Lunare
        sume_frame = QFrame()
        sume_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 16px;
                margin: 8px 0;
            }
        """)
        sume_layout = QVBoxLayout(sume_frame)

        sume_title = QLabel("<b>Scurtături Modul Sume Lunare</b>")
        sume_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        sume_title.setStyleSheet("color: #2c3e50;")
        sume_layout.addWidget(sume_title)

        shortcuts_sume = """
        <table style='width: 100%; border-collapse: collapse; margin: 10px 0;'>
            <tr style='background: #f8f9fa;'>
                <th style='padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6; width: 30%;'>Scurtătură</th>
                <th style='padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;'>Funcționalitate</th>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: #e9ecef; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Escape</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><b>Reset/Anulare</b> - Golește formularul și istoricul</td>
            </tr>
            <tr style='background: #f8f9fa;'>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: #e9ecef; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>F1</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><b>Modifică Tranzacție</b> - Deschide dialog pentru modificarea ultimei luni înregistrate</td>
            </tr>
            <tr>
                <td style='padding: 8px;'><kbd style='background: #e9ecef; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>F5</kbd></td>
                <td style='padding: 8px;'><b>Calculează Dobândă la Zi</b> - Pentru achitare anticipată împrumut</td>
            </tr>
        </table>
        """
        shortcuts_sume_label = QLabel(shortcuts_sume)
        shortcuts_sume_label.setWordWrap(True)
        shortcuts_sume_label.setTextFormat(Qt.RichText)
        shortcuts_sume_label.setStyleSheet("color: #495057;")
        sume_layout.addWidget(shortcuts_sume_label)

        self.content_layout.addWidget(sume_frame)

        # Secțiunea Calculator
        calc_frame = QFrame()
        calc_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 16px;
                margin: 8px 0;
            }
        """)
        calc_layout = QVBoxLayout(calc_frame)

        calc_title = QLabel("<b>Scurtături Calculator</b>")
        calc_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        calc_title.setStyleSheet("color: #2c3e50;")
        calc_layout.addWidget(calc_title)

        shortcuts_calc = """
        <table style='width: 100%; border-collapse: collapse; margin: 10px 0;'>
            <tr style='background: #f8f9fa;'>
                <th style='padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6; width: 30%;'>Scurtătură</th>
                <th style='padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;'>Funcționalitate</th>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: #e9ecef; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>0-9, .</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Introducere <b>cifre și punct zecimal</b></td>
            </tr>
            <tr style='background: #f8f9fa;'>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: #e9ecef; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>+, -, *, /</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'>Introducere <b>operatori matematici</b></td>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: #e9ecef; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Enter / =</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><b>Calculează rezultatul</b></td>
            </tr>
            <tr style='background: #f8f9fa;'>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: #e9ecef; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Escape / C</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><b>Clear</b> - Șterge tot conținutul</td>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: #e9ecef; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Backspace</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><b>Șterge ultimul caracter</b></td>
            </tr>
            <tr style='background: #f8f9fa;'>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><kbd style='background: #e9ecef; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>Delete</kbd></td>
                <td style='padding: 8px; border-bottom: 1px solid #eee;'><b>Clear Entry</b> - Șterge intrarea curentă</td>
            </tr>
            <tr>
                <td style='padding: 8px;'><kbd style='background: #e9ecef; padding: 4px 8px; border-radius: 3px; font-family: monospace; font-size: 11pt;'>%</kbd></td>
                <td style='padding: 8px;'><b>Calcul procent</b></td>
            </tr>
        </table>
        """
        shortcuts_calc_label = QLabel(shortcuts_calc)
        shortcuts_calc_label.setWordWrap(True)
        shortcuts_calc_label.setTextFormat(Qt.RichText)
        shortcuts_calc_label.setStyleSheet("color: #495057;")
        calc_layout.addWidget(shortcuts_calc_label)

        self.content_layout.addWidget(calc_frame)

        # Notă finală
        note_frame = QFrame()
        note_frame.setStyleSheet("""
            QFrame {
                background: #d1ecf1;
                border: 1px solid #bee5eb;
                border-radius: 6px;
                padding: 12px;
                margin: 8px 0;
            }
        """)
        note_layout = QVBoxLayout(note_frame)

        note_label = QLabel(
            "<b>Notă:</b> Toate scurtăturile funcționează indiferent de fereastra activă în cadrul aplicației. "
            "Scurtăturile cu <kbd style='background: #fff; padding: 2px 6px; border-radius: 3px;'>Alt</kbd> sunt pentru accesul rapid la meniuri, "
            "iar cele cu <kbd style='background: #fff; padding: 2px 6px; border-radius: 3px;'>Ctrl+Alt</kbd> pentru funcționalități avansate. "
            "Scurtăturile din module specifice (Sume Lunare, Calculator) funcționează doar când modulul respectiv este activ."
        )
        note_label.setWordWrap(True)
        note_label.setTextFormat(Qt.RichText)
        note_label.setStyleSheet("color: #0c5460; font-size: 9pt;")
        note_layout.addWidget(note_label)

        self.content_layout.addWidget(note_frame)

        self.content_layout.addStretch()

    def _load_manual(self):
        """Încarcă manualul de utilizare cu acordeon"""
        intro_label = QLabel(
            "<b>Manual Complet de Utilizare</b><br>"
            "Ghid detaliat pentru toate funcționalitățile aplicației CAR Petroșani. "
            "Click pe orice secțiune pentru a vedea detaliile."
        )
        intro_label.setWordWrap(True)
        intro_label.setStyleSheet("padding: 10px; background: #e3f2fd; border-radius: 6px; color: #1565c0;")
        self.content_layout.addWidget(intro_label)

        # Creează secțiuni acordeon pentru fiecare meniu
        for menu_name, menu_data in MANUAL_STRUCTURE.items():
            section_widget = self._create_menu_section_widget(menu_name, menu_data)
            accordion = AccordionSection(menu_name, section_widget)
            self.content_layout.addWidget(accordion)

        self.content_layout.addStretch()

    def _create_menu_section_widget(self, menu_name, menu_data):
        """Creează widget pentru secțiune meniu"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        # Descriere generală
        if 'descriere' in menu_data:
            desc_label = QLabel(f"<b>Descriere:</b> {menu_data['descriere']}")
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #495057; padding: 8px; background: #f8f9fa; border-radius: 4px;")
            layout.addWidget(desc_label)

        # Submeniuri (dacă există)
        if 'submeniuri' in menu_data:
            for submenu_name, submenu_data in menu_data['submeniuri'].items():
                submenu_frame = QFrame()
                submenu_frame.setStyleSheet("""
                    QFrame {
                        background: white;
                        border-left: 3px solid #3498db;
                        padding: 12px;
                        margin: 4px 0;
                    }
                """)
                submenu_layout = QVBoxLayout(submenu_frame)

                # Titlu submeniu
                title = QLabel(f"<b>{submenu_name}</b>")
                title.setFont(QFont("Segoe UI", 10, QFont.Bold))
                title.setStyleSheet("color: #2c3e50;")
                submenu_layout.addWidget(title)

                # Descriere submeniu
                if 'descriere' in submenu_data:
                    desc = QLabel(submenu_data['descriere'])
                    desc.setWordWrap(True)
                    desc.setStyleSheet("color: #6c757d; margin-left: 10px;")
                    submenu_layout.addWidget(desc)

                # Funcționalități
                if 'functionalitati' in submenu_data:
                    func_text = "<ul style='margin: 5px 0 5px 20px;'>"
                    for func in submenu_data['functionalitati']:
                        func_text += f"<li>{func}</li>"
                    func_text += "</ul>"
                    func_label = QLabel(func_text)
                    func_label.setWordWrap(True)
                    func_label.setTextFormat(Qt.RichText)
                    func_label.setStyleSheet("color: #495057; margin-left: 10px;")
                    submenu_layout.addWidget(func_label)

                # Note
                if 'note' in submenu_data:
                    note_label = QLabel(f"<b>Notă:</b> {submenu_data['note']}")
                    note_label.setWordWrap(True)
                    note_label.setStyleSheet("""
                        color: #856404;
                        background: #fff3cd;
                        padding: 8px;
                        border-radius: 4px;
                        border-left: 3px solid #ffc107;
                        margin: 8px 0 0 10px;
                    """)
                    submenu_layout.addWidget(note_label)

                layout.addWidget(submenu_frame)

        # Funcționalități directe (fără submeniuri)
        elif 'functionalitati' in menu_data:
            func_text = "<ul style='margin: 5px 0 5px 20px;'>"
            for func in menu_data['functionalitati']:
                func_text += f"<li>{func}</li>"
            func_text += "</ul>"
            func_label = QLabel(func_text)
            func_label.setWordWrap(True)
            func_label.setTextFormat(Qt.RichText)
            func_label.setStyleSheet("color: #495057; padding: 8px;")
            layout.addWidget(func_label)

        # Stări sistem (pentru Conversie)
        if 'stari_sistem' in menu_data:
            for stare_name, stare_data in menu_data['stari_sistem'].items():
                stare_frame = QFrame()
                stare_frame.setStyleSheet("""
                    QFrame {
                        background: #f8f9fa;
                        border: 2px solid #dee2e6;
                        border-radius: 6px;
                        padding: 12px;
                        margin: 8px 0;
                    }
                """)
                stare_layout = QVBoxLayout(stare_frame)

                stare_title = QLabel(f"<b>{stare_name}</b>")
                stare_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
                stare_title.setStyleSheet("color: #0056b3;")
                stare_layout.addWidget(stare_title)

                if 'descriere' in stare_data:
                    stare_desc = QLabel(stare_data['descriere'])
                    stare_desc.setWordWrap(True)
                    stare_desc.setStyleSheet("color: #6c757d; margin-left: 10px;")
                    stare_layout.addWidget(stare_desc)

                if 'comportament' in stare_data:
                    comp_text = "<ul style='margin: 5px 0 5px 20px;'>"
                    for comp in stare_data['comportament']:
                        comp_text += f"<li>{comp}</li>"
                    comp_text += "</ul>"
                    comp_label = QLabel(comp_text)
                    comp_label.setWordWrap(True)
                    comp_label.setTextFormat(Qt.RichText)
                    comp_label.setStyleSheet("color: #495057; margin-left: 10px;")
                    stare_layout.addWidget(comp_label)

                layout.addWidget(stare_frame)

        # Proces conversie (pentru Conversie)
        if 'proces_conversie' in menu_data:
            proces_data = menu_data['proces_conversie']
            proces_frame = QFrame()
            proces_frame.setStyleSheet("""
                QFrame {
                    background: white;
                    border: 2px solid #28a745;
                    border-radius: 6px;
                    padding: 12px;
                    margin: 8px 0;
                }
            """)
            proces_layout = QVBoxLayout(proces_frame)

            proces_title = QLabel("<b>Procesul de Conversie Automată</b>")
            proces_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
            proces_title.setStyleSheet("color: #155724;")
            proces_layout.addWidget(proces_title)

            if 'descriere' in proces_data:
                proces_desc = QLabel(proces_data['descriere'])
                proces_desc.setWordWrap(True)
                proces_desc.setStyleSheet("color: #6c757d; margin-left: 10px;")
                proces_layout.addWidget(proces_desc)

            if 'etape' in proces_data:
                etape_text = "<ol style='margin: 5px 0 5px 20px;'>"
                for etapa in proces_data['etape']:
                    etape_text += f"<li>{etapa}</li>"
                etape_text += "</ol>"
                etape_label = QLabel(etape_text)
                etape_label.setWordWrap(True)
                etape_label.setTextFormat(Qt.RichText)
                etape_label.setStyleSheet("color: #495057; margin-left: 10px;")
                proces_layout.addWidget(etape_label)

            if 'validari_ue' in proces_data:
                val_title = QLabel("<b>Validări Conformitate UE:</b>")
                val_title.setStyleSheet("color: #004085; margin: 8px 0 4px 10px;")
                proces_layout.addWidget(val_title)

                val_text = "<ul style='margin: 5px 0 5px 20px;'>"
                for val in proces_data['validari_ue']:
                    val_text += f"<li>{val}</li>"
                val_text += "</ul>"
                val_label = QLabel(val_text)
                val_label.setWordWrap(True)
                val_label.setTextFormat(Qt.RichText)
                val_label.setStyleSheet("color: #004085; margin-left: 10px;")
                proces_layout.addWidget(val_label)

            layout.addWidget(proces_frame)

        # Monkey patching (pentru Conversie)
        if 'monkey_patching' in menu_data:
            mp_data = menu_data['monkey_patching']
            mp_frame = QFrame()
            mp_frame.setStyleSheet("""
                QFrame {
                    background: white;
                    border: 2px solid #6610f2;
                    border-radius: 6px;
                    padding: 12px;
                    margin: 8px 0;
                }
            """)
            mp_layout = QVBoxLayout(mp_frame)

            mp_title = QLabel("<b>Sistem Monkey Patching</b>")
            mp_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
            mp_title.setStyleSheet("color: #4c0a9b;")
            mp_layout.addWidget(mp_title)

            if 'descriere' in mp_data:
                mp_desc = QLabel(mp_data['descriere'])
                mp_desc.setWordWrap(True)
                mp_desc.setStyleSheet("color: #6c757d; margin-left: 10px;")
                mp_layout.addWidget(mp_desc)

            if 'mecanism' in mp_data:
                mec_text = "<ul style='margin: 5px 0 5px 20px;'>"
                for mec in mp_data['mecanism']:
                    mec_text += f"<li>{mec}</li>"
                mec_text += "</ul>"
                mec_label = QLabel(mec_text)
                mec_label.setWordWrap(True)
                mec_label.setTextFormat(Qt.RichText)
                mec_label.setStyleSheet("color: #495057; margin-left: 10px;")
                mp_layout.addWidget(mec_label)

            if 'avantaje' in mp_data:
                av_title = QLabel("<b>Avantaje:</b>")
                av_title.setStyleSheet("color: #155724; margin: 8px 0 4px 10px;")
                mp_layout.addWidget(av_title)

                av_text = "<ul style='margin: 5px 0 5px 20px;'>"
                for av in mp_data['avantaje']:
                    av_text += f"<li>{av}</li>"
                av_text += "</ul>"
                av_label = QLabel(av_text)
                av_label.setWordWrap(True)
                av_label.setTextFormat(Qt.RichText)
                av_label.setStyleSheet("color: #155724; margin-left: 10px;")
                mp_layout.addWidget(av_label)

            layout.addWidget(mp_frame)

        # Categorii (pentru Selector temă)
        if 'categorii' in menu_data:
            for cat_name, cat_themes in menu_data['categorii'].items():
                cat_label = QLabel(f"<b>{cat_name}:</b> {', '.join(cat_themes)}")
                cat_label.setWordWrap(True)
                cat_label.setStyleSheet("color: #495057; padding: 6px; margin-left: 10px;")
                layout.addWidget(cat_label)

        # Note finale
        if 'note' in menu_data:
            note_label = QLabel(f"<b>Important:</b> {menu_data['note']}")
            note_label.setWordWrap(True)
            note_label.setStyleSheet("""
                color: #721c24;
                background: #f8d7da;
                padding: 10px;
                border-radius: 4px;
                border-left: 4px solid #dc3545;
                margin-top: 10px;
            """)
            layout.addWidget(note_label)

        # Utilizare (pentru Calcule)
        if 'utilizare' in menu_data:
            util_text = "<b>Utilizare:</b><ul style='margin: 5px 0 5px 20px;'>"
            for util in menu_data['utilizare']:
                util_text += f"<li>{util}</li>"
            util_text += "</ul>"
            util_label = QLabel(util_text)
            util_label.setWordWrap(True)
            util_label.setTextFormat(Qt.RichText)
            util_label.setStyleSheet("color: #495057; padding: 8px; background: #e7f3ff; border-radius: 4px;")
            layout.addWidget(util_label)

        # Secțiuni (pentru Versiune)
        if 'sectiuni' in menu_data:
            sect_text = "<ul style='margin: 5px 0 5px 20px;'>"
            for sect in menu_data['sectiuni']:
                sect_text += f"<li>{sect}</li>"
            sect_text += "</ul>"
            sect_label = QLabel(sect_text)
            sect_label.setWordWrap(True)
            sect_label.setTextFormat(Qt.RichText)
            sect_label.setStyleSheet("color: #495057; padding: 8px;")
            layout.addWidget(sect_label)

        return widget

    def _load_changelog(self):
        """Încarcă istoricul versiunilor"""
        intro_label = QLabel(
            "<b>Istoric Versiuni</b><br>"
            "Evoluția aplicației CAR Petroșani de la prima versiune BETA la versiunea finală."
        )
        intro_label.setWordWrap(True)
        intro_label.setStyleSheet("padding: 10px; background: #e8f5e9; border-radius: 6px; color: #2e7d32;")
        self.content_layout.addWidget(intro_label)

        for version, changes in reversed(list(CHANGELOG.items())):
            version_frame = QFrame()

            if version == "FINALA":
                version_frame.setStyleSheet("""
                    QFrame {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #fff8e1, stop:1 #ffecb3);
                        border: 2px solid #ff9800;
                        border-radius: 8px;
                        padding: 16px;
                        margin: 8px 0;
                    }
                """)
            elif version == CURRENT_VERSION:
                version_frame.setStyleSheet("""
                    QFrame {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #e3f2fd, stop:1 #bbdefb);
                        border: 2px solid #2196f3;
                        border-radius: 8px;
                        padding: 16px;
                        margin: 8px 0;
                    }
                """)
            else:
                version_frame.setStyleSheet("""
                    QFrame {
                        background: white;
                        border: 1px solid #dee2e6;
                        border-radius: 8px;
                        padding: 16px;
                        margin: 8px 0;
                    }
                """)

            version_layout = QVBoxLayout(version_frame)

            # Header versiune
            if version == "FINALA":
                version_label = QLabel(f"<b>{version}</b>")
                version_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
                version_label.setStyleSheet("color: #e65100;")
            elif version == CURRENT_VERSION:
                version_label = QLabel(f"<b>Versiunea {version}</b> - CURENT")
                version_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
                version_label.setStyleSheet("color: #1565c0;")
            else:
                version_label = QLabel(f"<b>Versiunea {version}</b>")
                version_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
                version_label.setStyleSheet("color: #37474f;")

            version_layout.addWidget(version_label)

            # Lista îmbunătățiri
            changes_text = "<ul style='margin: 8px 0 0 20px; line-height: 1.6;'>"
            for change in changes:
                changes_text += f"<li>{change}</li>"
            changes_text += "</ul>"

            changes_label = QLabel(changes_text)
            changes_label.setWordWrap(True)
            changes_label.setTextFormat(Qt.RichText)
            changes_label.setStyleSheet("color: #495057; font-size: 9pt;")
            version_layout.addWidget(changes_label)

            self.content_layout.addWidget(version_frame)

        self.content_layout.addStretch()

    def _load_tech_info(self):
        """Încarcă informații tehnice sistem"""
        intro_label = QLabel(
            "<b>Informații Tehnice</b><br>"
            "Detalii despre arhitectura și tehnologiile utilizate în aplicația CAR Petroșani."
        )
        intro_label.setWordWrap(True)
        intro_label.setStyleSheet("padding: 10px; background: #f3e5f5; border-radius: 6px; color: #6a1b9a;")
        self.content_layout.addWidget(intro_label)

        # Informații generale
        general_frame = QFrame()
        general_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 16px;
                margin: 8px 0;
            }
        """)
        general_layout = QVBoxLayout(general_frame)

        general_title = QLabel("<b>Tehnologii Utilizate</b>")
        general_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        general_title.setStyleSheet("color: #2c3e50;")
        general_layout.addWidget(general_title)

        tech_info = """
        <ul style='margin: 8px 0 0 20px; line-height: 1.8;'>
            <li><b>Limbaj:</b> Python 3.x</li>
            <li><b>Framework UI:</b> PyQt5 pentru interfață grafică modernă</li>
            <li><b>Baze de date:</b> SQLite3 pentru persistență date</li>
            <li><b>Export:</b> ReportLab pentru generare PDF, xlsxwriter pentru Excel</li>
            <li><b>Arhitectură:</b> MVC cu separare logică business și prezentare</li>
            <li><b>Conversie monedă:</b> Decimal pentru precizie matematică conform UE</li>
        </ul>
        """
        tech_label = QLabel(tech_info)
        tech_label.setWordWrap(True)
        tech_label.setTextFormat(Qt.RichText)
        tech_label.setStyleSheet("color: #495057;")
        general_layout.addWidget(tech_label)

        # Link GitHub
        github_label = QLabel(
            "<b>Repository GitHub:</b><br>"
            "<a href='https://github.com/totilaAtila/C.A.R._Petrosani' style='color: #2980b9;'>"
            "https://github.com/totilaAtila/C.A.R._Petrosani</a>"
        )
        github_label.setWordWrap(True)
        github_label.setTextFormat(Qt.RichText)
        github_label.setOpenExternalLinks(True)
        github_label.setStyleSheet("padding: 10px; background: #e8f4f8; border-radius: 6px; color: #495057; margin-top: 10px;")
        general_layout.addWidget(github_label)

        self.content_layout.addWidget(general_frame)

        # Arhitectură dual-currency
        dual_frame = QFrame()
        dual_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 16px;
                margin: 8px 0;
            }
        """)
        dual_layout = QVBoxLayout(dual_frame)

        dual_title = QLabel("<b>Arhitectură Dual-Currency (RON/EUR)</b>")
        dual_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        dual_title.setStyleSheet("color: #2c3e50;")
        dual_layout.addWidget(dual_title)

        dual_info = """
        <b>Componente principale:</b>
        <ul style='margin: 8px 0 0 20px; line-height: 1.8;'>
            <li><b>currency_logic.py:</b> Management stare conversie și validare permisiuni</li>
            <li><b>conversie_widget.py:</b> Widget aplicare conversie definitivă cu validări UE</li>
            <li><b>currency_toggle_widget.py:</b> Control toggle RON/EUR în bara principală</li>
            <li><b>main_ui.py (monkey patching):</b> Redirectare automată apeluri DB către baze corecte</li>
        </ul>

        <b>Strategia de protecție date:</b>
        <ul style='margin: 8px 0 0 20px; line-height: 1.8;'>
            <li>Bazele originale RON rămân intacte ca audit trail</li>
            <li>Conversie creează clone complete cu sufix EUR</li>
            <li>Modul RON post-conversie: DOAR CITIRE (protecție scriere)</li>
            <li>Modul EUR: Citire și scriere complete funcționale</li>
            <li>Toggle instant între moduri fără restart aplicație</li>
        </ul>

        <b>Validări matematice:</b>
        <ul style='margin: 8px 0 0 20px; line-height: 1.8;'>
            <li>ROUND_HALF_UP conform Regulamentul CE 1103/97</li>
            <li>Precizie 2 zecimale toate sumele EUR</li>
            <li>Toleranță maximă ±0.01 EUR la validare finală</li>
            <li>Verificare consistență sumă totală pre și post conversie</li>
        </ul>
        """
        dual_label = QLabel(dual_info)
        dual_label.setWordWrap(True)
        dual_label.setTextFormat(Qt.RichText)
        dual_label.setStyleSheet("color: #495057;")
        dual_layout.addWidget(dual_label)

        self.content_layout.addWidget(dual_frame)

        # Baze de date
        db_frame = QFrame()
        db_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 16px;
                margin: 8px 0;
            }
        """)
        db_layout = QVBoxLayout(db_frame)

        db_title = QLabel("<b>Structură Baze de Date</b>")
        db_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        db_title.setStyleSheet("color: #2c3e50;")
        db_layout.addWidget(db_title)

        db_info = """
        <b>Baze principale (RON + EUR post-conversie):</b>
        <ul style='margin: 8px 0 0 20px; line-height: 1.8;'>
            <li><b>DEPCRED.db / DEPCREDEUR.db:</b> Tranzacții lunare - împrumuturi, rate, cotizații, solduri</li>
            <li><b>MEMBRII.db / MEMBRIIEUR.db:</b> Date identificare membri și cotizații standard</li>
            <li><b>activi.db / activiEUR.db:</b> Membri activi cu solduri depuneri, dividende, beneficii</li>
            <li><b>INACTIVI.db / INACTIVIEUR.db:</b> Membri inactivi și număr luni fără plată</li>
            <li><b>LICHIDATI.db / LICHIDATIEUR.db:</b> Istoric lichidări cu date finalizare</li>
        </ul>

        <b>Baze auxiliare (comune ambelor monede):</b>
        <ul style='margin: 8px 0 0 20px; line-height: 1.8;'>
            <li><b>CHITANTE.db:</b> Numerotare secvențială chitanțe generate</li>
            <li><b>config_dobanda.json:</b> Rată dobândă configurabilă extern</li>
            <li><b>conversion_config.json:</b> Status conversie și curs aplicat</li>
        </ul>
        """
        db_label = QLabel(db_info)
        db_label.setWordWrap(True)
        db_label.setTextFormat(Qt.RichText)
        db_label.setStyleSheet("color: #495057;")
        db_layout.addWidget(db_label)

        self.content_layout.addWidget(db_frame)

        self.content_layout.addStretch()


def test_despre_widget():
    """Funcție test pentru rulare standalone"""
    app = QApplication(sys.argv)
    dialog = DespreWidget()
    dialog.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    test_despre_widget()