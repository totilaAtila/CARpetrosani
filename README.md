# CARpetrosani — Aplicația Desktop Originală 🖥️

<div align="center">

**Aplicație desktop pentru gestionarea Casei de Ajutor Reciproc Petroșani**  
*Versiunea originală stabilă — Python + PyQt5 + SQLite*

[![Status](https://img.shields.io/badge/status-production-brightgreen)](https://github.com/totilaAtila/CARpetrosani)
[![Python](https://img.shields.io/badge/python-3.8+-blue)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-blue)](https://www.riverbankcomputing.com/software/pyqt/)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)](https://github.com/totilaAtila/CARpetrosani)
[![License](https://img.shields.io/badge/license-proprietary-lightgrey)](https://github.com/totilaAtila/CARpetrosani)

[🌐 Variantă Web (Production)](https://github.com/totilaAtila/CARapp_web) • [🧪 Variantă Web (Experimental)](https://github.com/totilaAtila/carapp2) • [📖 Documentație](#-documentație)

</div>

---

## 📋 Despre Proiect

**CARpetrosani** este aplicația **desktop originală** pentru gestionarea completă a Casei de Ajutor Reciproc Petroșani. Dezvoltată în Python cu interfață PyQt5, aceasta este **versiunea stabilă** utilizată în producție de câteva luni.

### 🎯 Poziționare în Familie

| Versiune | Status | Platformă | Use Case |
|----------|--------|-----------|----------|
| **CARpetrosani** (acest repo) | ✅ **Producție** | Windows Desktop | Utilizare zilnică CAR Petroșani |
| [CARapp_web](https://github.com/totilaAtila/CARapp_web) | ✅ Production | Web (universal) | Alternative cloud, mobil |
| [carapp2](https://github.com/totilaAtila/carapp2) | 🟡 Experimental | Web (desktop) | Explorare File System API |

### ✅ De ce varianta desktop?

**Avantaje:**
- 🚀 **Performanță nativă** — rulează direct pe sistem
- 💾 **Control total** — acces direct la sistem de fișiere
- 🔒 **Securitate** — datele rămân 100% local, zero cloud
- ⚡ **Stabilitate** — testat intens, utilizat în producție
- 🖥️ **Interfață familiar** — aspect Windows nativ (PyQt5)
- 📊 **Module complete** — toate funcționalitățile implementate

**Limitări:**
- ⚠️ Windows only (adaptare Linux/macOS posibilă)
- 📱 Nu rulează pe mobil
- 🔄 Instalare necesară pe fiecare calculator
- 📦 Dependențe Python (Python 3.8+, PyQt5, etc.)

---

## 🆚 Comparație cu Variantele Web

<details>
<summary><b>📊 Click pentru comparație detaliată</b></summary>

| Aspect | CARpetrosani (Desktop) | CARapp_web | carapp2 |
|--------|----------------------|------------|---------|
| **Platformă** | Windows desktop | Web universal | Web desktop |
| **Limbaj** | Python 3.8+ | JavaScript/React | TypeScript/React |
| **UI Framework** | PyQt5 | React + Tailwind | React + Tailwind |
| **Baze de date** | SQLite (native) | sql.js (WASM) | sql.js (WASM) |
| **Instalare** | Python + dependențe | Zero (browser) | Zero (browser) |
| **Performanță** | ⚡ Nativă | 🟡 Bună (WASM) | 🟡 Bună (WASM) |
| **Offline** | ✅ Total | ✅ După prima încărcare | ✅ După prima încărcare |
| **Securitate date** | ✅ 100% local | ✅ 100% local | ✅ 100% local |
| **Module complete** | ✅ 7/7 | ✅ 7/7 | ❌ 1/7 |
| **Conversie EUR** | ✅ Da | ✅ Da (Reg. CE) | ❌ Nu |
| **Generare Lună** | ✅ Original | ✅ Port TypeScript | ✅ Port TypeScript |
| **Statistici** | ✅ Complete | ✅ Complete | ❌ Placeholder |
| **Rapoarte PDF** | ✅ Da | 🟡 În curs | ❌ Nu |
| **Mobile support** | ❌ Nu | ✅ Da | ⚠️ Limitat |
| **Deploy** | Instalare locală | Netlify/Vercel | Development |
| **Maturitate** | ✅ Stabil | ✅ Stabil | 🟡 Alpha |
| **Utilizatori** | CAR Petroșani | Anyone (browser) | Dev/Testing |

</details>

### 🎯 Când să folosești CARpetrosani?

✅ **DA** — pentru:
- Utilizare **oficială** la sediul CAR Petroșani
- Când ai nevoie de **toate modulele** (7/7 funcționale)
- Performanță **maximă** (operațiuni pe mii de înregistrări)
- Control **total** asupra datelor (zero cloud)
- Interfață **Windows nativă** (look & feel familiar)
- Când lucrezi **exclusiv pe Windows desktop**

❌ **NU** — pentru:
- Utilizare **mobilă** (telefon, tabletă)
- Accesare de pe **multiple dispozitive**
- Când nu poți/vrei instala **Python + dependențe**
- Când ai nevoie de **acces web** (de oriunde)
- Când lucrezi pe **macOS** sau **Linux** (fără adaptare)

---

## ✨ Funcționalități Complete

### ✅ Module Implementate (7/7)

#### 1. 📅 Generare Lună Nouă
**Status:** ⭐ Modul核心 — sursa algoritmului pentru variante web

- Detectare automată ultima lună procesată
- Calculare automată lună următoare
- Validare consecutivitate (nu permite sărituri)
- Excludere automată membri lichidați
- Aplicare cotizații standard din MEMBRII
- Moștenire rate împrumut
- Calcul dobândă stingere (4‰)
- Dividende în ianuarie (membri activi)
- Actualizare solduri (împrumuturi + depuneri)
- **Precizie maximă** — calcule conforme Regulament CE
- Raport detaliat cu statistici
- Export bază actualizată

#### 2. 💰 Sume Lunare
- Introducere plăți pentru membrii selectați
- Calculator dobândă în timp real
- Validare date (suma, membru valid, perioadă)
- Actualizare imediată solduri
- Istoric tranzacții per membru
- Filtrare după perioadă

#### 3. 👥 Gestiune Membri
- Listă completă membri (activi + lichidați)
- Căutare după nume / număr fișă
- Vizualizare detalii complete
- Adăugare membru nou (formular validat)
- Editare date membru
- Lichidare membru (proces complet)
- Status vizual (activ/lichidat/inactiv)
- Export listă membri

#### 4. 📊 Statistici și Analize
- Total membri (activi/lichidați/inactivi)
- Distribuție solduri (împrumuturi/depuneri)
- Top 10 împrumuturi
- Top 10 depuneri
- Evoluție lunară (grafice)
- Rapoarte comparative
- Export date statistice

#### 5. 📅 Vizualizare Lunară/Anuală
- Selectare perioadă (lună/an)
- Tabel complet tranzacții
- Filtrare după membru
- Sort după orice coloană
- Rezumat lunar (totaluri)
- Export CSV/Excel

#### 6. 📄 Rapoarte și Listări
- Generare rapoarte lunare (PDF)
- Generare rapoarte anuale (PDF)
- Liste personalizate (membri, solduri, împrumuturi)
- Filtre avansate
- Template-uri customizabile
- Export multiple formate (PDF, Excel, CSV)

#### 7. 💶 Împrumuturi și Dividende
- Înregistrare împrumut nou
- Gestiune rate (planificare + tracking)
- Alertă scadențe
- Calcul dobândă automată
- Distribuire dividende (ianuarie)
- Istoric complet împrumuturi

---

## 🚀 Instalare și Configurare

### Cerințe Sistem

| Categorie | Cerință | Recomandat |
|-----------|---------|------------|
| **OS** | Windows 7+ | Windows 10/11 |
| **Python** | 3.8+ | 3.10+ |
| **RAM** | 2 GB | 4 GB+ |
| **Disk** | 100 MB | 500 MB+ (cu baze) |
| **Rezoluție** | 1024x768 | 1920x1080 |

### Instalare

#### Opțiunea 1: Instalare Rapidă (Recomandat)
```bash
# 1. Clonare repository
git clone https://github.com/totilaAtila/CARpetrosani.git
cd CARpetrosani

# 2. Creare mediu virtual Python
python -m venv venv

# 3. Activare mediu virtual
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 4. Instalare dependențe
pip install -r requirements.txt

# 5. Rulare aplicație
python main.py
```

#### Opțiunea 2: Instalare cu PyCharm (IDE Recomandat)

1. Deschide PyCharm
2. `File` → `Open` → Selectează folderul `CARpetrosani`
3. PyCharm detectează `requirements.txt` → Click "Install requirements"
4. Configurează Python interpreter (3.8+)
5. Click dreapta pe `main.py` → `Run 'main'`

### Dependențe Principale
```txt
PyQt5==5.15.9          # Framework UI
sqlite3                # Bază de date (built-in Python)
decimal                # Calcule financiare (built-in Python)
reportlab==4.0.4       # Generare PDF (optional)
openpyxl==3.1.2        # Export Excel (optional)
```

### Structură Baze de Date

Aplicația așteaptă bazele de date în folderul rădăcină sau într-un subfolder `data/`:
```
CARpetrosani/
├── data/               # Opțional: folder pentru baze
│   ├── MEMBRII.db     # ✅ Obligatoriu
│   ├── DEPCRED.db     # ✅ Obligatoriu
│   ├── LICHIDATI.db   # ℹ️ Opțional
│   └── ACTIVI.db      # ℹ️ Opțional
│
├── main.py            # Entry point
├── generare_luna.py   # ⭐ Logica generare lună
├── ui/                # Interfețe PyQt5
├── logic/             # Business logic
└── requirements.txt
```

---

## 📂 Structura Proiectului
```
CARpetrosani/
├── main.py                    # Entry point + setup fereastră principală
│
├── ui/                        # Interfețe PyQt5 (.ui + .py)
│   ├── main_window.py         # Fereastră principală
│   ├── generare_luna.py       # Dialog generare lună
│   ├── membri.py              # Dialog gestiune membri
│   ├── sume_lunare.py         # Dialog introducere sume
│   ├── statistici.py          # Fereastră statistici
│   ├── vizualizare.py         # Fereastră vizualizare lunară
│   └── rapoarte.py            # Dialog generare rapoarte
│
├── logic/                     # Business logic
│   ├── generare_luna.py       # ⭐ ALGORITM CORE (sursa pentru web)
│   ├── calcule.py             # Funcții calcul (dobândă, solduri)
│   ├── validari.py            # Validări date
│   ├── db_manager.py          # Operațiuni SQLite
│   └── conversie_eur.py       # Conversie RON→EUR (dacă există)
│
├── models/                    # Clase date
│   ├── membru.py              # Model Membru
│   ├── tranzactie.py          # Model Tranzacție
│   └── sold.py                # Model Sold
│
├── utils/                     # Utilități
│   ├── logger.py              # Logging
│   ├── config.py              # Configurări
│   └── helpers.py             # Helper functions
│
├── reports/                   # Template-uri rapoarte
│   ├── raport_lunar.py        # Generator raport lunar
│   └── raport_anual.py        # Generator raport anual
│
├── data/                      # Baze de date (opțional)
│   ├── MEMBRII.db
│   ├── DEPCRED.db
│   ├── LICHIDATI.db
│   └── ACTIVI.db
│
├── resources/                 # Resurse (iconițe, stiluri)
│   ├── icons/
│   └── styles/
│
├── tests/                     # Teste (dacă există)
│   ├── test_generare_luna.py
│   └── test_calcule.py
│
├── requirements.txt           # Dependențe Python
├── README.md                  # (acest fișier)
└── LICENSE                    # Licență
```

---

## 🧮 Logica Generare Lună — Algoritmul Original

Această logică din `logic/generare_luna.py` este **sursa** pentru portările TypeScript (carapp2 și CARapp_web).

### Algoritmul Core (Python)
```python
import sqlite3
from decimal import Decimal, ROUND_HALF_UP

def generare_luna_noua(depcred_db, membrii_db, lichidati_db, activi_db, 
                       luna_tinta, an_tinta):
    """
    Generează datele pentru luna următoare în DEPCRED.
    
    Args:
        depcred_db: Path către DEPCRED.db
        membrii_db: Path către MEMBRII.db
        lichidati_db: Path către LICHIDATI.db (optional)
        activi_db: Path către ACTIVI.db (optional)
        luna_tinta: Luna de generat (1-12)
        an_tinta: Anul de generat
    
    Returns:
        dict: Statistici generare (membri procesați, totaluri)
    """
    
    # 1. Detectare ultima lună din DEPCRED
    conn = sqlite3.connect(depcred_db)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT anul, luna FROM depcred "
        "ORDER BY anul DESC, luna DESC LIMIT 1"
    )
    ultima_luna = cursor.fetchone()
    an_sursa, luna_sursa = ultima_luna
    
    # 2. Validare consecutivitate
    luna_urmatoare = (luna_sursa % 12) + 1
    an_urmatoare = an_sursa + 1 if luna_sursa == 12 else an_sursa
    
    if luna_tinta != luna_urmatoare or an_tinta != an_urmatoare:
        raise ValueError("Puteți genera doar luna imediat următoare!")
    
    # 3. Verificare existență luna țintă
    cursor.execute(
        "SELECT COUNT(*) FROM depcred WHERE anul=? AND luna=?",
        (an_tinta, luna_tinta)
    )
    if cursor.fetchone()[0] > 0:
        raise ValueError(f"Luna {luna_tinta:02d}-{an_tinta} există deja!")
    
    # 4. Reset prima=0 pentru toate lunile
    cursor.execute("UPDATE depcred SET prima=0 WHERE prima=1")
    
    # 5. Încărcare membri + lichidați
    membrii = incarca_membrii(membrii_db)
    lichidati = incarca_lichidati(lichidati_db) if lichidati_db else set()
    
    # 6. Proces pentru fiecare membru
    membri_procesati = 0
    total_dep_sold = Decimal(0)
    total_impr_sold = Decimal(0)
    total_dobanda = Decimal(0)
    
    for membru in membrii:
        nr_fisa = membru['nr_fisa']
        
        # 6.1. Skip dacă lichidat
        if nr_fisa in lichidati:
            continue
        
        # 6.2. Preia solduri luna sursă
        cursor.execute(
            "SELECT impr_sold, dep_sold FROM depcred "
            "WHERE nr_fisa=? AND anul=? AND luna=?",
            (nr_fisa, an_sursa, luna_sursa)
        )
        sold_sursa = cursor.fetchone()
        if not sold_sursa:
            continue
        
        impr_sold_vechi = Decimal(str(sold_sursa[0]))
        dep_sold_vechi = Decimal(str(sold_sursa[1]))
        
        # 6.3. Inițializare sume noi
        cotizatie = Decimal(str(membru['cotizatie_standard']))
        dep_deb_nou = cotizatie
        dep_cred_nou = Decimal(0)
        impr_deb_nou = Decimal(0)
        impr_cred_nou = mosteneste_rata_imprumut(
            cursor, nr_fisa, an_sursa, luna_sursa
        )
        
        # 6.4. Dividend în ianuarie
        if luna_tinta == 1:
            dividend = preia_dividend(activi_db, nr_fisa)
            if dividend > 0:
                dep_deb_nou += dividend  # ← LA DEBIT!
        
        # 6.5. Calculare solduri noi
        impr_sold_nou = (impr_sold_vechi + impr_deb_nou - impr_cred_nou)
        dep_sold_nou = (dep_sold_vechi + dep_deb_nou - dep_cred_nou)
        
        # 6.6. Rotunjire și zero-izare
        impr_sold_nou = impr_sold_nou.quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        dep_sold_nou = dep_sold_nou.quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        if abs(impr_sold_nou) < Decimal('0.005'):
            impr_sold_nou = Decimal(0)
        if abs(dep_sold_nou) < Decimal('0.005'):
            dep_sold_nou = Decimal(0)
        
        # 6.7. Dobândă stingere
        dobanda = Decimal(0)
        if impr_sold_vechi > 0 and impr_sold_nou == 0:
            dobanda = calculeaza_dobanda_stingere(
                cursor, nr_fisa, an_sursa, luna_sursa
            )
        
        # 6.8. INSERT cu prima=1
        cursor.execute(
            "INSERT INTO depcred "
            "(nr_fisa, luna, anul, dobanda, impr_deb, impr_cred, "
            "impr_sold, dep_deb, dep_cred, dep_sold, prima) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)",
            (nr_fisa, luna_tinta, an_tinta,
             float(dobanda), float(impr_deb_nou), float(impr_cred_nou),
             float(impr_sold_nou), float(dep_deb_nou), float(dep_cred_nou),
             float(dep_sold_nou))
        )
        
        membri_procesati += 1
        total_dep_sold += dep_sold_nou
        total_impr_sold += impr_sold_nou
        total_dobanda += dobanda
    
    # 7. Commit și returnare statistici
    conn.commit()
    conn.close()
    
    return {
        'luna_sursa': luna_sursa,
        'an_sursa': an_sursa,
        'luna_tinta': luna_tinta,
        'an_tinta': an_tinta,
        'membri_procesati': membri_procesati,
        'total_dep_sold': float(total_dep_sold),
        'total_impr_sold': float(total_impr_sold),
        'total_dobanda': float(total_dobanda)
    }

def calculeaza_dobanda_stingere(cursor, nr_fisa, an_sursa, luna_sursa):
    """
    Calculează dobânda de stingere: 4‰ pe suma soldurilor pozitive
    din perioada împrumutului.
    """
    # 1. Găsește începutul împrumutului (ultima lună cu impr_deb > 0)
    yM1 = an_sursa * 100 + luna_sursa
    cursor.execute(
        "SELECT MAX(anul*100+luna) FROM depcred "
        "WHERE nr_fisa=? AND impr_deb>0 AND (anul*100+luna)<=?",
        (nr_fisa, yM1)
    )
    start = cursor.fetchone()[0]
    if not start:
        return Decimal(0)
    
    # 2. Sumează soldurile pozitive din perioada împrumutului
    cursor.execute(
        "SELECT SUM(impr_sold) FROM depcred "
        "WHERE nr_fisa=? AND (anul*100+luna BETWEEN ? AND ?) "
        "AND impr_sold>0",
        (nr_fisa, start, yM1)
    )
    suma_pozitive = Decimal(str(cursor.fetchone()[0] or 0))
    
    # 3. Dobândă = 4‰ = 0.004
    dobanda = suma_pozitive * Decimal('0.004')
    return dobanda.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def mosteneste_rata_imprumut(cursor, nr_fisa, an, luna):
    """
    Moștenește rata împrumutului din luna anterioară
    (doar dacă nu există impr_deb > 0).
    """
    cursor.execute(
        "SELECT impr_deb, impr_cred FROM depcred "
        "WHERE nr_fisa=? AND anul=? AND luna=?",
        (nr_fisa, an, luna)
    )
    row = cursor.fetchone()
    if not row:
        return Decimal(0)
    
    impr_deb = Decimal(str(row[0]))
    if impr_deb > 0:
        return Decimal(0)  # Există împrumut nou → nu moștenim rată
    
    return Decimal(str(row[1]))  # Moștenim impr_cred
```

### Conformitate Regulament CE

Toate calculele financiare folosesc `Decimal` cu `ROUND_HALF_UP`:
```python
from decimal import Decimal, ROUND_HALF_UP, getcontext

# Configurare globală precizie
getcontext().prec = 28  # Precizie implicită Python Decimal
getcontext().rounding = ROUND_HALF_UP

# Exemplu calcul
sold_nou = Decimal('1234.567') + Decimal('0.005')
sold_rotunjit = sold_nou.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
# Rezultat: 1234.57
```

---

## 🎨 Interfața Grafică (PyQt5)

### Fereastră Principală
```
┌────────────────────────────────────────────────────┐
│  CARapp Petroșani v1.0                        [_][□][X] │
├────────────────────────────────────────────────────┤
│  Fișier  Editare  Vizualizare  Rapoarte  Ajutor  │
├────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────┐ │
│  │  📊 Status Baze de Date                      │ │
│  │  ✅ MEMBRII: 245 membri                      │ │
│  │  ✅ DEPCRED: Ultima lună 09-2024             │ │
│  │  ✅ LICHIDATI: 12 membri                     │ │
│  │  ✅ ACTIVI: 180 membri                       │ │
│  └──────────────────────────────────────────────┘ │
│                                                    │
│  ┌──────────────┐ ┌──────────────┐               │
│  │ 📅 Generare  │ │ 💰 Sume      │               │
│  │    Lună Nouă │ │    Lunare    │               │
│  └──────────────┘ └──────────────┘               │
│                                                    │
│  ┌──────────────┐ ┌──────────────┐               │
│  │ 👥 Gestiune  │ │ 📊 Statistici│               │
│  │    Membri    │ │    & Analize │               │
│  └──────────────┘ └──────────────┘               │
│                                                    │
│  ┌──────────────┐ ┌──────────────┐               │
│  │ 📅 Vizual.   │ │ 📄 Rapoarte  │               │
│  │    Lunară    │ │    & Listări │               │
│  └──────────────┘ └──────────────┘               │
├────────────────────────────────────────────────────┤
│  Status: Gata | Bază: DEPCRED.db | Ultimul update:│
│  24.10.2025 14:30                                 │
└────────────────────────────────────────────────────┘
```

### Dialog Generare Lună
```
┌────────────────────────────────────────────┐
│  Generare Lună Nouă                   [X]  │
├────────────────────────────────────────────┤
│  Ultima lună procesată: 09-2024            │
│  Următoarea lună: 10-2024                 │
│  Rată dobândă lichidare: 0.4‰              │
├────────────────────────────────────────────┤
│  Selectați luna de generat:                │
│  Luna: [10 - Octombrie ▼]  An: [2024 ▼]   │
├────────────────────────────────────────────┤
│  [🟢 Generează Luna Selectată]             │
│  [🔴 Șterge Ultima Lună Generată]          │
│  [⚙️ Modifică Rata Dobândă]                │
├────────────────────────────────────────────┤
│  ┌─── Log Proces ─────────────────────┐   │
│  │ Început generare 10-2024...        │   │
│  │ Membri activi: 245                 │   │
│  │ Procesare fișa 1001 - Ion Popescu  │   │
│  │ Procesare fișa 1002 - Maria Ionescu│   │
│  │ ...                                 │   │
│  │ Generare finalizată cu succes!     │   │
│  │ Total solduri depuneri: 1,234,567.89│  │
│  │ Total solduri împrumuturi: 234,567.89│ │
│  └─────────────────────────────────────┘   │
├────────────────────────────────────────────┤
│            [Închide] [Export Log]          │
└────────────────────────────────────────────┘
```

### Stilizare

Aplicația folosește **Windows native look & feel** prin PyQt5:
- Teme: Respect tema Windows (Light/Dark)
- Fonturi: Segoe UI (Windows 10/11)
- Icoane: Icons8 sau Material Design Icons
- Culori: Accent colors din tema sistem

---

## 🧪 Testare

### Testare Manuală

**Checklist Standard:**

1. **Lansare aplicație**
   - [ ] Se deschide fereastra principală
   - [ ] Bazele de date se încarcă corect
   - [ ] Status baze vizibil în UI

2. **Generare Lună**
   - [ ] Detectare corectă ultima lună
   - [ ] Generare lună următoare funcționează
   - [ ] Log afișează progresul
   - [ ] Statistici finale corecte
   - [ ] Verificare date în DEPCRED.db (DB Browser for SQLite)

3. **Sume Lunare**
   - [ ] Introducere plată pentru membru
   - [ ] Calcul dobândă corect
   - [ ] Salvare în bază

4. **Gestiune Membri**
   - [ ] Listă membri corectă
   - [ ] Căutare funcționează
   - [ ] Adăugare membru nou
   - [ ] Editare date
   - [ ] Lichidare membru

5. **Statistici**
   - [ ] Grafice se afișează corect
   - [ ] Totaluri corecte
   - [ ] Export funcționează

6. **Rapoarte**
   - [ ] Generare PDF funcționează
   - [ ] Template corect
   - [ ] Date corecte în raport

### Testare Automată (dacă există)
```bash
# Unit tests
python -m pytest tests/

# Coverage
python -m pytest --cov=logic tests/

# Test specific
python -m pytest tests/test_generare_luna.py -v
```

---

## 🛠️ Depanare și Probleme Comune

### Eroare: `No module named 'PyQt5'`

**Soluție:**
```bash
pip install PyQt5==5.15.9
```

### Eroare: `Unable to open database file`

**Cauză:** Bazele de date nu sunt în locația așteptată

**Soluție:**
1. Verifică că `MEMBRII.db` și `DEPCRED.db` există
2. Plasează-le în folderul `data/` sau rădăcina proiectului
3. Verifică permisiuni (Read/Write)

### Eroare: `decimal.InvalidOperation`

**Cauză:** Valoare invalidă în calcule Decimal

**Soluție:**
1. Verifică că toate câmpurile numerice din baze sunt valide
2. Rulează `SELECT * FROM depcred WHERE impr_sold='NaN' OR dep_sold='NaN'`
3. Corectează înregistrările invalide

### Performanță Lentă

**Cauze posibile:**
- Bază de date mare (>10,000 înregistrări)
- Lipsă indexuri SQLite
- Hard disk lent (nu SSD)

**Soluții:**
```sql
-- Adaugă indexuri pentru performanță
CREATE INDEX IF NOT EXISTS idx_depcred_fisa 
  ON depcred(nr_fisa);
CREATE INDEX IF NOT EXISTS idx_depcred_perioada 
  ON depcred(anul, luna);
CREATE INDEX IF NOT EXISTS idx_depcred_prima 
  ON
