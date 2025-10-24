# CAR Petroșani - Aplicație Desktop Windows

Aplicație desktop pentru gestionarea Casei de Ajutor Reciproc Petroșani, dezvoltată în Python cu PyQt5, cu suport complet pentru conversie RON→EUR și sistem dual currency cu protecție avansată a datelor.

## 📋 Caracteristici Principale

### 🔄 Sistem Dual Currency RON/EUR
- **Monkey Patching Condițional**: Comutare dinamică între bazele de date RON și EUR la runtime
- **Protecție Scriere Avansată**: Modul RON devine read-only după aplicarea conversiei
- **Toggle Valutar**: Comutare rapidă între RON și EUR direct din interfață
- **Indicatori Vizuali**: Afișare clară a monedei active și permisiunilor (Citire-Scriere / Doar Citire)
- **Fișier Configurare**: `dual_currency.json` pentru persistența statusului conversiei

### 💱 Conversie RON → EUR
- **Conformitate CE**: Conversie conform Regulamentului CE 1103/97
- **Conversie Directă Individuală**: Fiecare înregistrare este convertită separat
- **Precizie Decimal**: Calcule financiare exacte pentru conformitate UE
- **Curs Fix Configurabil**: Curs implicit 4.9755 RON/EUR (modificabil)
- **Clone Perfecte**: Creează baze de date EUR ca clone ale bazelor RON
- **Statistici Conversie**: Raportare detaliată cu totaluri și diferențe de rotunjire

### 🎨 Interfață Modernă cu 21+ Teme Vizuale
- **Teme Clasice Glass**: Verde Original, Albastru Ocean, Violet Elegant, Portocaliu Sunset, Roz Delicat, Turcoaz Marin
- **Teme Profesionale**: Corporate Blue, Black Professional, Dark Gray, Charcoal, Slate, Executive Gray, Sage, Warm Beige, Deep Navy, Soft Lavender, Cool Mint, Warm Taupe, Steel Blue, Soft Cream
- **Teme Optimizate**: Text Negru pe Off-White, Text Gri Închis, Text Negru pe Gri, Text Gri pe Fundal Crem, Schema Gri Monochromă
- **Persistență**: Tema selectată este salvată automat în `car_settings.json`
- **Preview Real-Time**: Vizualizare instantanee a temelor înainte de aplicare
- **Efecte Moderne**: Gradient glass, shadow effects, animații fluide

### 📊 Module Funcționale Complete

#### 1. **Gestiune Membri**
   - **Adăugare Membru**: Înregistrare membri noi cu validare completă
   - **Lichidare Membru**: Procesare lichidare cu calcul solduri finale
   - **Ștergere Membru**: Ștergere cu verificări de integritate
   - **Verificare Fișe**: Validare consistență date membri

#### 2. **Operațiuni Financiare**
   - **Sume Lunare**: Introducere plăți lunare cu calculator dobândă integrat
   - **Împrumuturi Noi**: Gestionare împrumuturi cu calcul rate și dobândă (Fereastră separată - F12)
   - **Dividende**: Calculare și distribuire dividende pentru membri activi
   - **Calculator**: Calculator integrat cu funcții avansate (Ctrl+Alt+C)

#### 3. **Vizualizări și Raportări**
   - **Situație Lunară**: Vizualizare detalii pentru o lună selectată
   - **Situație Trimestrială**: Raportare date pe trimestru
   - **Situație Anuală**: Sinteză anuală completă
   - **Statistici**: Dashboard cu totaluri, medii și distribuții
   - **Afișare Membri Inactivi**: Monitorizare membri cu lipsă activitate

#### 4. **Listări și Chitanțe**
   - **Generare Chitanțe PDF**: Creare automată chitanțe lunare pentru membri
   - **Configurare Tipărire**: Număr chitanță inițial, chitanțe per pagină (5-15)
   - **Preview Chitanțe**: Previzualizare date înainte de generare PDF
   - **Sistem Progres**: Bare de progres pentru operații lungi cu protecție anti-înghețare
   - **Pagină Totaluri**: PDF include pagină finală cu totaluri dobândă, împrumuturi, depuneri
   - **Listări RON**: Modul specializat pentru generare chitanțe în RON
   - **Listări EUR**: Modul specializat pentru generare chitanțe în EUR
   - **Actualizare Automată**: CHITANTE.db actualizat cu numerele chitanțelor (STARTCH_PR, STARTCH_AC)

#### 5. **Administrare Sistem**
   - **Generare Lună Nouă**: Proces automatizat cu calcul dobânzi și actualizare solduri
   - **Optimizare Baze**: VACUUM și REINDEX pentru performanță optimă
   - **Salvări**: Operațiuni backup și restore pentru bazele de date
   - **CAR DBF Converter**: Import/export date din formate DBF (Ctrl+Alt+D)

### ⌨️ Scurtături Tastatură Complete

| Scurtătură | Funcție |
|------------|---------|
| **Alt+A** | Meniu Actualizări |
| **Alt+V** | Meniu Vizualizări |
| **Alt+L** | Listări |
| **Alt+S** | Salvări |
| **Alt+I** | Împrumuturi Noi |
| **Alt+O** | Optimizare Baze |
| **Alt+G** | Generare Lună |
| **Alt+T** | Selector Temă |
| **Alt+R** | Versiune |
| **Alt+Q** | Ieșire |
| **Ctrl+Alt+C** | Calculator |
| **Ctrl+Alt+D** | CAR DBF Converter |
| **Ctrl+Alt+R** | Conversie RON→EUR |
| **F12** | Comutare rapidă către Împrumuturi Noi |

### 🔒 Protecție Date și Permisiuni

După aplicarea conversiei RON→EUR, sistemul implementează protecție automată:

**Modul RON (Doar Citire)**:
- Vizualizare date permisă
- Operațiuni de scriere blocate
- Meniuri protejate: Actualizări, Generare Lună, Optimizare Baze

**Modul EUR (Citire-Scriere)**:
- Toate operațiunile permise
- Modificări salvate în bazele EUR
- Flexibilitate completă pentru actualizări

**Indicator Vizual**:
- ✅ Citire-Scriere (verde) - Operațiuni permise
- 🔒 Doar Citire (portocaliu) - Protecție activă

## 💻 Cerințe de Sistem

### Software Necesar
- **Python**: 3.7+ (recomandat 3.9 sau 3.10)
- **PyQt5**: 5.15.0+
- **SQLite3**: Include în Python (versiune 3.30+)
- **IDE Recomandat**: PyCharm Community/Professional

### Dependențe Python
```bash
PyQt5>=5.15.0
reportlab>=3.6.0  # Pentru generarea PDF chitanțe
sqlite3  # Inclus în Python standard library
pathlib  # Inclus în Python standard library
json     # Inclus în Python standard library
```

### Sistem de Operare
- **Windows**: 10 sau 11 (64-bit recomandat)
- **Minimum RAM**: 4 GB
- **Spațiu Disc**: 500 MB (incluzând baze de date)
- **Rezoluție Ecran**: Minimum 1366x768 (recomandat 1920x1080)

## 🚀 Instalare și Configurare

### 1. Clonare Repository

```bash
git clone https://github.com/totilaAtila/CARpetrosani.git
cd CARpetrosani
```

### 2. Creare Mediu Virtual (Recomandat)

```bash
# Creare mediu virtual
python -m venv venv

# Activare mediu virtual
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### 3. Instalare Dependențe

```bash
pip install -r requirements.txt
```

Sau instalare manuală:
```bash
pip install PyQt5>=5.15.0
pip install reportlab>=3.6.0
```

### 4. Pregătire Baze de Date

Plasați bazele de date SQLite în directorul principal al aplicației:

**Baze de Date Obligatorii:**
- `MEMBRII.db` - Informații despre membri
- `DEPCRED.db` - Depuneri și credite RON
- `LICHIDATI.db` - Membri lichidați

**Baze de Date Opționale:**
- `activi.db` - Membri activi (pentru dividende)
- `INACTIVI.db` - Membri inactivi
- `CHITANTE.db` - Tracking numere chitanțe (creat automat dacă lipsește)
- `CONVERSIE.db` - Configurații conversie valutară

**După Conversie EUR (generate automat):**
- `MEMBRIIEUR.db` - Informații membri (cu cotizații EUR)
- `DEPCREDEUR.db` - Depuneri și credite EUR
- `activiEUR.db` - Membri activi EUR
- `LICHIDATIEUR.db` - Membri lichidați EUR
- `INACTIVIEUR.db` - Membri inactivi EUR
- `dual_currency.json` - Status conversie și configurare

### 5. Rulare Aplicație

```bash
python main.py
```

## 📁 Structura Proiectului

```
CARpetrosani/
├── main.py                          # Punct de intrare cu early database patching
├── main_ui.py                       # Interfața principală cu sistem dual currency
├── currency_logic.py                # Logică gestionare monede și permisiuni
├── dialog_styles.py                 # Stiluri pentru dialoguri
├── car_settings.json                # Setări persistente (tema selectată)
├── dual_currency.json               # Status conversie și configurare dual currency
│
├── ui/                              # Module interfață utilizator
│   ├── statistici.py                # Dashboard statistici
│   ├── adaugare_membru.py           # Adăugare membri noi
│   ├── sume_lunare.py               # Introducere plăți lunare
│   ├── lichidare_membru.py          # Procesare lichidări
│   ├── stergere_membru.py           # Ștergere membri
│   ├── dividende.py                 # Calcul și distribuire dividende
│   ├── vizualizare_lunara.py        # Vizualizare date lunare
│   ├── vizualizare_trimestriala.py  # Vizualizare date trimestriale
│   ├── vizualizare_anuala.py        # Vizualizare date anuale
│   ├── verificare_fise.py           # Validare consistență date
│   ├── afisare_membri_lichidati.py  # Afișare membri inactivi/lichidați
│   ├── listari.py                   # Generare chitanțe PDF pentru RON
│   ├── listariEUR.py                # Generare chitanțe PDF pentru EUR
│   ├── salvari.py                   # Operațiuni salvare/backup
│   ├── calculator.py                # Calculator integrat
│   ├── imprumuturi_noi.py           # Gestionare împrumuturi (fereastră separată)
│   ├── generare_luna.py             # Generare lună nouă automată
│   ├── optimizare_index.py          # Optimizare performanță baze
│   ├── despre.py                    # Informații aplicație
│   └── ...
│
├── conversie_widget.py              # Widget conversie RON→EUR
├── car_dbf_converter_widget.py      # Converter DBF (opțional)
│
├── fonts/                           # Fonturi pentru generare PDF
│   ├── Arial.ttf
│   ├── DejaVuSans-Bold.ttf
│   └── ...
│
├── icons/                           # Iconițe aplicație
│   ├── app_icon.png
│   ├── calc.png
│   └── ...
│
├── MEMBRII.db                       # Baze de date SQLite (RON)
├── DEPCRED.db
├── activi.db
├── INACTIVI.db
├── LICHIDATI.db
├── CHITANTE.db                      # Tracking chitanțe (creat automat)
│
├── MEMBRIIEUR.db                    # Baze de date SQLite (EUR - după conversie)
├── DEPCREDEUR.db
├── activiEUR.db
├── INACTIVIEUR.db
├── LICHIDATIEUR.db
├── CHITANTEEUR.db                   # Tracking chitanțe EUR (creat automat)
│
└── README.md                        # Documentație
```

## 🗄️ Structura Bazelor de Date

### Tabele Principale

#### 1. MEMBRII.db - Informații Membri
```sql
Coloane:
- NR_FISA          INTEGER PRIMARY KEY    -- Număr fișă unic
- NUM_PREN         TEXT                   -- Nume și prenume
- DOMICILIUL       TEXT                   -- Adresă domiciliu
- CALITATEA        TEXT                   -- Funcție/Departament
- DATA_INSCR       TEXT                   -- Data înscrierii (YYYY-MM-DD)
- COTIZATIE_STANDARD REAL                 -- Cotizație lunară standard (RON)
- COTIZATIE_EUR    REAL                   -- Cotizație lunară EUR (după conversie)
```

#### 2. DEPCRED.db - Depuneri și Credite
```sql
Coloane:
- NR_FISA          INTEGER                -- Referință către MEMBRII
- LUNA             INTEGER                -- Luna (1-12)
- ANUL             INTEGER                -- Anul
- DOBANDA          REAL                   -- Dobândă calculată
- IMPR_DEB         REAL                   -- Împrumut debit (nou împrumut)
- IMPR_CRED        REAL                   -- Împrumut credit (plată)
- IMPR_SOLD        REAL                   -- Sold împrumut
- DEP_DEB          REAL                   -- Depunere debit (retragere)
- DEP_CRED         REAL                   -- Depunere credit (depunere)
- DEP_SOLD         REAL                   -- Sold depunere
- PRIMA            REAL                   -- Primă/Bonus
- CONVERTIT_DIN_RON INTEGER              -- Flag conversie (1=convertit, doar în EUR)
```

#### 3. activi.db - Membri Activi (Dividende)
```sql
Coloane:
- NR_FISA          INTEGER PRIMARY KEY    -- Număr fișă
- NUM_PREN         TEXT                   -- Nume și prenume
- DEP_SOLD         REAL                   -- Sold depuneri
- DIVIDEND         REAL                   -- Dividend calculat
- BENEFICIU        REAL                   -- Beneficiu total
```

#### 4. LICHIDATI.db - Membri Lichidați
```sql
Coloane:
- nr_fisa          INTEGER PRIMARY KEY    -- Număr fișă
- data_lichidare   TEXT                   -- Data lichidării
```

#### 5. INACTIVI.db - Membri Inactivi
```sql
Coloane:
- nr_fisa          INTEGER PRIMARY KEY    -- Număr fișă
- num_pren         TEXT                   -- Nume și prenume
- lipsa_luni       INTEGER                -- Număr luni lipsă consecutive
```

#### 6. CHITANTE.db - Tracking Chitanțe
```sql
Coloane:
- STARTCH_PR       INTEGER                -- Număr chitanță precedent (ultima sesiune)
- STARTCH_AC       INTEGER                -- Număr chitanță actual (sesiunea curentă)
```

**Utilizare:**
- `STARTCH_AC` = numărul ultimei chitanțe generate
- `STARTCH_PR` = numărul ultimei chitanțe din sesiunea precedentă (pentru istoric)
- La resetare: `STARTCH_PR = 0`
- Actualizare automată la fiecare generare PDF chitanțe

### Diferențe RON vs EUR

**Baze RON** (MEMBRII.db, DEPCRED.db, etc.):
- Coloană `COTIZATIE_STANDARD` în RON
- Toate sumele în RON
- Fără coloană `CONVERTIT_DIN_RON`

**Baze EUR** (MEMBRIIEUR.db, DEPCREDEUR.db, etc.):
- Coloană `COTIZATIE_EUR` în EUR
- Toate sumele convertite la EUR
- Coloană `CONVERTIT_DIN_RON = 1` pentru tracking

## 💰 Logică Financiară

### Calcul Dobândă

Dobânda se calculează lunar pe baza soldului împrumutului:

```python
Dobândă = Sold Împrumut × Rată Dobândă

Rată Dobândă Implicită: 0.004 (4‰ - patru la mie)
```

**Exemplu:**
```
Sold Împrumut: 10,000 RON
Rată: 0.004
Dobândă Lunară = 10,000 × 0.004 = 40 RON
```

### Actualizare Solduri

**Pentru Împrumuturi:**
```python
Sold Nou = Sold Anterior + Împrumut Nou (Deb) - Plată (Cred) + Dobândă
```

**Pentru Depuneri:**
```python
Sold Nou = Sold Anterior - Retragere (Deb) + Depunere (Cred)
```

### Conversie RON → EUR

Aplicația implementează conversia conform **Regulamentului CE 1103/97**:

**Metodologie:**
- **Conversie Directă Individuală**: Fiecare înregistrare convertită separat
- **Precizie Decimal**: Utilizare aritmetică precisă pentru evitarea erorilor de rotunjire
- **Metodă de Rotunjire**: ROUND_HALF_UP (0.5 rotunjit la 1)
- **Curs Fix**: 4.9755 RON/EUR (configurabil)

**Exemplu Conversie:**
```python
Suma RON: 497.55 RON
Curs: 4.9755 RON/EUR
Suma EUR = 497.55 ÷ 4.9755 = 100.00 EUR (rotunjit la 2 zecimale)
```

**Formula Generală:**
```
Valoare_EUR = ROUND(Valoare_RON / Curs_Schimb, 2)
```

### Generare Lună Nouă

Procesul automatizat de generare lună nouă:

1. **Citire Solduri**: Extrage soldurile din luna anterioară pentru fiecare membru
2. **Aplicare Tranzacții**: Procesează toate tranzacțiile din luna curentă
3. **Calcul Dobândă**: Calculează dobânda pe soldul împrumutului
4. **Creare Înregistrări**: Generează înregistrări pentru luna următoare
5. **Raportare**: Raport cu membrii procesați, împrumuturi noi și omiși

## 🛠️ Utilizare

### Pornire Aplicație

1. **Lansare**: Executați `python main.py` sau dublu-click pe `main.py` (dacă Python este configurat)
2. **Încărcare Automată**: Aplicația încarcă automat tema salvată și verifică statusul conversiei
3. **Interfață**: Se deschide fereastra principală cu meniul lateral și zona de conținut

### Navigare în Aplicație

**Meniu Lateral:**
- Click pe butoane pentru acces rapid la module
- Utilizați scurtăturile tastatură pentru eficiență
- Toggle RON/EUR pentru comutare monedă
- Indicator permisiuni (Citire-Scriere / Doar Citire)

**Submeniuri:**
- Se deschid automat la click pe module cu opțiuni multiple
- Buton "⬅ Ieșire Meniu" pentru revenire la statistici

**Teme Vizuale:**
- Click pe "Selector temă" sau Alt+T
- Navigare cu tastatura pentru preview real-time
- Aplicare automată și salvare persistentă

### Operațiuni Comune

#### 1. Adăugare Membru Nou
```
Actualizări (Alt+A) → Adăugare membru
→ Completare date → Salvare
```

#### 2. Introducere Plăți Lunare
```
Actualizări (Alt+A) → Sume lunare
→ Selectare membru → Introducere date → Salvare
```

#### 3. Generare Lună Nouă
```
Generare lună (Alt+G)
→ Selectare lună și an → Confirmare → Procesare automată
```

#### 4. Conversie RON → EUR
```
Conversie RON->EUR (Ctrl+Alt+R)
→ Verificare curs → Confirmare → Conversie automată
→ Descărcare baze EUR generate
```

#### 5. Comutare între RON și EUR
```
Toggle în meniul lateral: Click pe RON sau EUR
→ Aplicația re-patchuiește modulele automat
→ Widget-urile se reîncarcă cu datele corecte
```

#### 6. Generare Chitanțe PDF (Listări)
```
Listări (Alt+L)
→ Selectare lună și an pentru chitanțe
→ Setare număr chitanță inițial (ex: 1001)
→ Configurare chitanțe per pagină (5-15, default 10)
→ Click "Preview" pentru verificare date
→ Verificare totaluri (dobândă, împrumuturi, depuneri)
→ Click "Tipărește PDF" → Confirmare
→ Generare automată cu progres vizual
→ PDF salvat ca chitante_LUNA_AN.pdf
→ Deschidere automată PDF sau click "Deschide PDF"
```

**Caracteristici Chitanțe:**
- Format A4 cu 10 chitanțe per pagină (configurabil 5-15)
- Dimensiune chitanță: 2,5 cm înălțime
- Informații: Nr.Fișă, Nume, Dobândă, Rată Împrumut, Sold Împrumut, Depuneri, Retrageri, Total de Plată
- Pagină finală cu totaluri generale
- Actualizare automată CHITANTE.db (tracking STARTCH_PR, STARTCH_AC)

## 🔧 Configurare Avansată

### Fișier car_settings.json

```json
{
    "current_theme": 0,
    "app_version": "3.2",
    "last_updated": "2025-10-24 14:30:00"
}
```

### Fișier dual_currency.json

```json
{
    "conversie_aplicata": true,
    "data_conversie": "2025-10-24 15:45:00",
    "curs_folosit": 4.9755,
    "baze_convertite": [
        "MEMBRII",
        "DEPCRED",
        "activi",
        "INACTIVI",
        "LICHIDATI"
    ]
}
```

## 🐛 Troubleshooting

### Problema: Aplicația nu pornește

**Soluții:**
```bash
# Verificare versiune Python
python --version  # Trebuie să fie 3.7+

# Reinstalare PyQt5
pip uninstall PyQt5
pip install PyQt5

# Verificare dependențe
pip list | grep PyQt5
```

### Problema: Erori la încărcarea bazelor de date

**Verificări:**
1. Bazele de date există în directorul aplicației
2. Fișierele nu sunt corupte (testare cu DB Browser for SQLite)
3. Permisiuni de citire/scriere pe fișiere
4. Spațiu disponibil pe disc

```bash
# Testare integritate bază de date
sqlite3 MEMBRII.db "PRAGMA integrity_check;"
```

### Problema: Toggle RON/EUR nu funcționează

**Cauze Posibile:**
- Fișierul `dual_currency.json` lipsește sau este corupt
- Bazele EUR nu există după conversie
- Permisiuni de scriere blocate

**Soluție:**
```bash
# Verificare existență baze EUR
ls *EUR.db

# Verificare dual_currency.json
cat dual_currency.json
```

### Problema: Tema nu se salvează

**Soluție:**
```bash
# Verificare permisiuni
# Windows (PowerShell):
Get-Acl car_settings.json

# Ștergere fișier corupt și regenerare
del car_settings.json
# Repornire aplicație pentru regenerare automată
```

### Problema: Erori de calcul financiar

**Verificări:**
- Toate valorile sunt numerice (nu TEXT)
- Câmpurile nu conțin NULL
- Soldurile sunt consistente

```sql
-- Verificare consistență
SELECT NR_FISA, LUNA, ANUL, 
       IMPR_SOLD, DEP_SOLD 
FROM DEPCRED 
WHERE IMPR_SOLD IS NULL OR DEP_SOLD IS NULL;
```

### Problema: Chitanțele PDF nu se generează

**Cauze Posibile:**
- Fonturile lipsesc (Arial.ttf, DejaVuSans-Bold.ttf)
- Permisiuni insuficiente pentru scriere
- DEPCRED.db sau MEMBRII.db lipsesc

**Soluții:**
```bash
# Verificare fonturi
ls fonts/Arial.ttf
ls fonts/DejaVuSans-Bold.ttf

# Copiere fonturi din Windows
copy C:\Windows\Fonts\Arial.ttf fonts\

# Verificare permisiuni
# Windows:
icacls chitante_*.pdf

# Verificare existență baze
dir DEPCRED.db MEMBRII.db
```

### Problema: Număr chitanță prea mare (8+ cifre)

**Soluție:**
- Apăsați "Reset" în modulul Listări
- Confirmați resetarea numărului la 1
- Sau setați manual un număr mai mic
- CHITANTE.db va fi actualizat cu noul număr

## 📖 FAQ (Întrebări Frecvente)

**Î: Pot reveni de la EUR la RON după conversie?**
**R:** Nu, conversia este definitivă. Sistemul păstrează bazele RON în modul read-only pentru referință istorică.

**Î: Ce se întâmplă dacă șterg dual_currency.json?**
**R:** Sistemul va considera conversia ca neaplicată și va permite din nou modul de scriere pentru RON.

**Î: Pot folosi o altă rată de dobândă?**
**R:** Da, rata se poate modifica în fișierele de configurare sau direct în cod (variabila `INTEREST_RATE_DEFAULT`).

**
