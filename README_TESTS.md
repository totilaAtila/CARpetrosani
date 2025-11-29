# 🧪 Documentație Suite Teste - CARpetrosani

**Versiune:** 1.0.0
**Data:** 2025-11-20
**Framework:** pytest 7.4.0+
**Coverage:** Module critice (generare_luna, dividende, conversie_widget, sume_lunare)

---

## 📋 Cuprins

1. [Introducere](#introducere)
2. [Instalare și Configurare](#instalare-și-configurare)
3. [Rulare Teste](#rulare-teste)
4. [Structura Testelor](#structura-testelor)
5. [Module Testate](#module-testate)
6. [Markeri Pytest](#markeri-pytest)
7. [Coverage și Raportare](#coverage-și-raportare)
8. [Contribuții și Best Practices](#contribuții-și-best-practices)

---

## 🎯 Introducere

Suite-ul de teste pentru CARpetrosani acoperă **4 module critice** care gestionează:

- **Precizie financiară** (calcule Decimal, fără erori rotunjire)
- **Securitate** (eliminare vulnerabilități CVE)
- **Integritate date** (validări obligatorii)
- **Conformitate reglementări** (CE 1103/97 pentru conversie RON→EUR)

### Buguri Critice Testate

Toate testele verifică rezolvările pentru:
- ✅ **BUG #1** - Conversie Decimal→Float (precizie financiară)
- ✅ **BUG #2** - Validare Ianuarie transfer dividende
- ✅ **BUG #10** - Vulnerabilități openpyxl (migrare xlsxwriter)

---

## 📦 Instalare și Configurare

### 1. Instalare Dependențe

```bash
# Instalare dependențe testare
pip install -r requirements-dev.txt

# Sau manual
pip install pytest pytest-cov pytest-mock pytest-qt pytest-timeout
```

### 2. Verificare Instalare

```bash
# Verifică versiune pytest
pytest --version

# Verifică configurare
pytest --collect-only
```

### 3. Structură Directoare

```
CARpetrosani/
├── tests/                          # Director teste
│   ├── __init__.py                 # Init package
│   ├── conftest.py                 # Fixtures comune
│   ├── test_generare_luna.py       # Teste generare_luna
│   ├── test_dividende.py           # Teste dividende
│   ├── test_conversie_widget.py    # Teste conversie RON→EUR
│   └── test_sume_lunare.py         # Teste sume_lunare
├── pytest.ini                      # Configurare pytest
├── requirements-dev.txt            # Dependențe testare
└── README_TESTS.md                 # Documentație (acest fișier)
```

---

## 🚀 Rulare Teste

### Rulare Toate Testele

```bash
# Rulare toate testele cu output verbose
pytest -v

# Rulare cu coverage
pytest --cov=. --cov-report=html

# Rulare cu output detaliat
pytest -vv --tb=short
```

### Rulare Teste Specifice

```bash
# Rulare teste pentru un modul
pytest tests/test_generare_luna.py -v

# Rulare o clasă de teste
pytest tests/test_generare_luna.py::TestCalculSolduri -v

# Rulare un test specific
pytest tests/test_generare_luna.py::TestCalculSolduri::test_calcul_sold_imprumut_basic -v
```

### Rulare după Markeri

```bash
# Doar teste critice
pytest -m critical -v

# Doar teste precizie Decimal
pytest -m decimal_precision -v

# Doar teste pentru buguri rezolvate
pytest -m bugfix -v

# Doar teste unitare (fără integrare)
pytest -m unit -v

# Doar teste integrare
pytest -m integration -v

# Doar teste securitate
pytest -m security -v
```

### Rulare cu Filtrare

```bash
# Exclude teste lente
pytest -m "not slow" -v

# Doar teste critice și bugfix
pytest -m "critical and bugfix" -v

# Teste critice dar nu integration
pytest -m "critical and not integration" -v
```

---

## 📂 Structura Testelor

### Fixtures Comune (conftest.py)

**Fixtures pentru PyQt5:**
- `qapp` - QApplication pentru teste PyQt5 (session scope)

**Fixtures pentru baze de date mockuite:**
- `temp_dir` - Director temporar pentru fiecare test
- `mock_membrii_db` - MEMBRII.db cu 10 membri de test
- `mock_depcred_db` - DEPCRED.db cu tranzacții 2025
- `mock_lichidati_db` - LICHIDATI.db cu membri lichidați
- `mock_activi_db` - ACTIVI.db cu membri activi
- `mock_all_dbs` - Toate bazele de date mockuite

**Helper functions:**
- `assert_decimal_equal(actual, expected, msg)` - Comparație Decimal cu toleranță

---

## 🧩 Module Testate

### 1. test_generare_luna.py

**Funcționalități testate:**

#### TestCalculSolduri
- ✅ Calcul sold împrumut: `sold_nou = sold_vechi + deb - cred`
- ✅ Calcul sold depozit: `sold_nou = sold_vechi + deb - cred`
- ✅ Zeroizare sold împrumut dacă < 0.005
- ✅ Nu zeroizare dacă > 0.005

#### TestCalculDobanda
- ✅ Calcul dobândă la achitare completă: `dobanda = SUM(solduri) × rata`
- ✅ Precizie Decimal (BUG #1): `str(decimal)` vs `float()`
- ✅ Nu calculează dobândă dacă sold rămâne pozitiv

#### TestMostenireRata
- ✅ Moștenește rată dacă nu există împrumut nou
- ✅ NU moștenește rată dacă există împrumut nou
- ✅ Plafonare rată la soldul sursă

#### TestCotizatieStandard
- ✅ Aplicare cotizație standard uniform
- ✅ Cotizații diferite per membru

#### TestIntegrationGenerareLuna
- ✅ Generare luna cu dobândă calculată
- ✅ Excludere membri lichidați

#### TestPrecizieDecimal (BUG #1)
- ✅ str(decimal) pentru INSERT
- ✅ Decimal(str(value)) pentru citire
- ✅ Precizie pentru 800 membri × 12 luni

**Total teste:** ~25 teste
**Markeri:** unit, integration, critical, bugfix, decimal_precision

---

### 2. test_dividende.py

**Funcționalități testate:**

#### TestCalculDividende
- ✅ Formula: `B = (S_membru / S_total) × P`
- ✅ Rotunjire corectă
- ✅ Suma dividende ≈ Profit total
- ✅ Dividend zero dacă profit zero
- ✅ Dividend zero dacă membru fără solduri

#### TestTransferDividende (BUG #2)
- ✅ Validare existență Ianuarie (BUG #2 fix)
- ✅ Transfer blocat dacă Ianuarie lipsește
- ✅ Calcul nou DEP_DEB după transfer
- ✅ Calcul nou DEP_SOLD după transfer
- ✅ str(decimal) pentru UPDATE (BUG #1 fix)

#### TestSumaSolduriLunare
- ✅ Calculare suma soldurilor lunare membru
- ✅ Calculare din DB mockuită

#### TestIntegrationDividende
- ✅ Calcul complet pentru 5 membri
- ✅ Validare Ianuarie în DB

#### TestPrecizieDividende (BUG #1)
- ✅ Precizie pentru 800 membri
- ✅ Fără conversie float()

#### TestExportExcel (BUG #10)
- ✅ Export folosește xlsxwriter
- ✅ openpyxl NU este folosit

**Total teste:** ~20 teste
**Markeri:** unit, integration, critical, bugfix, decimal_precision, security

---

### 3. test_conversie_widget.py

**Funcționalități testate:**

#### TestConversieRONtoEUR
- ✅ Conversie RON→EUR cu curs 4.9755
- ✅ Conversie directă individuală (CE 1103/97)
- ✅ Rotunjire ROUND_HALF_UP
- ✅ Precizie pentru valori mari
- ✅ Fără pierdere precizie

#### TestValidareIntegritateMembri
- ✅ Validare membri consistenți (folosește clasa reală `MemberIntegrityValidator`)
- ✅ Validare membri neînregistrați (eroare critică)

#### TestConversieCompleta
- ✅ Conversie completă DEPCRED RON→EUR

#### TestCursFix
- ✅ Curs fix 4.9755
- ✅ Conversie cu curs fix (nu variabil)

#### TestPrecizieConversie (BUG #1)
- ✅ Fără float() în conversii
- ✅ Precizie pentru 800 membri

**Total teste:** ~15 teste
**Markeri:** unit, integration, critical, decimal_precision, slow

---

### 4. test_sume_lunare.py

**Funcționalități testate:**

#### TestCalculSolduriLunare
- ✅ Calcul sold împrumut luna curentă
- ✅ Calcul sold depozit luna curentă
- ✅ Zeroizare sold sub prag
- ✅ Nu zeroizare peste prag

#### TestRecalculareLuniUlterioare
- ✅ Recalculare luna următoare
- ✅ Recalculare cascadă 6 luni

#### TestCalculDobandaManuala
- ✅ Calcul dobândă manuală
- ✅ Determinare perioadă împrumut

#### TestValidariInputuri
- ✅ Validare număr real valid
- ✅ Validare număr real invalid
- ✅ Validare format Luna-An (LL-AAAA)

#### TestPrecizieDecimal (BUG #1)
- ✅ str(decimal) pentru UPDATE
- ✅ Decimal(str(value)) pentru citire
- ✅ Precizie recalculare 12 luni

#### TestIntegrationSumeLunare
- ✅ Modificare și recalculare membru
- ✅ Calcul dobândă din DB

#### TestQuantizeDecimal
- ✅ Rotunjire cu quantize ROUND_HALF_UP
- ✅ Păstrare precizie Decimal

**Total teste:** ~22 teste
**Markeri:** unit, integration, critical, bugfix, decimal_precision

---

## 🏷️ Markeri Pytest

### Markeri Disponibili

| Marker | Descriere | Utilizare |
|--------|-----------|-----------|
| `unit` | Teste unitare simple fără dependențe externe | `pytest -m unit` |
| `integration` | Teste de integrare cu DB mockuite | `pytest -m integration` |
| `slow` | Teste care durează >1 secundă | `pytest -m slow` |
| `critical` | Teste pentru funcționalități critice | `pytest -m critical` |
| `bugfix` | Teste pentru buguri rezolvate (BUG #1, #2, #10) | `pytest -m bugfix` |
| `decimal_precision` | Teste pentru precizie Decimal | `pytest -m decimal_precision` |
| `security` | Teste pentru securitate | `pytest -m security` |

### Exemple Combinații

```bash
# Toate testele critice cu precizie Decimal
pytest -m "critical and decimal_precision" -v

# Teste pentru buguri rezolvate, exclude integration
pytest -m "bugfix and not integration" -v

# Teste critice sau securitate
pytest -m "critical or security" -v
```

---

## 📊 Coverage și Raportare

### Generare Coverage

```bash
# Coverage HTML (recomandat)
pytest --cov=. --cov-report=html
# Deschide htmlcov/index.html în browser

# Coverage terminal
pytest --cov=. --cov-report=term

# Coverage cu detalii missing lines
pytest --cov=. --cov-report=term-missing
```

### Coverage Țintă

| Modul | Coverage Țintă | Status |
|-------|----------------|--------|
| generare_luna.py | >80% | ✅ Teste complete |
| dividende.py | >80% | ✅ Teste complete |
| conversie_widget.py | >70% | ✅ Teste funcții critice |
| sume_lunare.py | >75% | ✅ Teste complete |

### Rapoarte Detaliate

```bash
# Raport JSON
pytest --cov=. --cov-report=json -o json_report=test-results.json

# Raport XML (pentru CI/CD)
pytest --cov=. --cov-report=xml --junitxml=junit.xml

# Toate rapoartele simultan
pytest --cov=. --cov-report=html --cov-report=term --cov-report=xml
```

---

## 🛠️ Debugging Teste

### Rulare cu Debugging

```bash
# Oprește la primul eșec
pytest -x

# Oprește după 5 eșecuri
pytest --maxfail=5

# Afișează print statements
pytest -s

# Debugging detaliat
pytest -vv --tb=long

# Doar teste eșuate din ultima rulare
pytest --lf

# Teste eșuate și următorul test
pytest --ff
```

### Profiling Teste

```bash
# Arată top 10 teste cele mai lente
pytest --durations=10

# Timeout pentru teste individuale
pytest --timeout=5
```

---

## 🔧 Configurare CI/CD

### Exemplu GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run tests
      run: |
        pytest -v --cov=. --cov-report=xml --junitxml=junit.xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        files: ./coverage.xml
```

---

## 📝 Best Practices

### Scriere Teste Noi

1. **Nume descriptive:**
   ```python
   def test_calcul_dobanda_cu_precizie_decimal():
       """Test că dobânda se calculează cu precizie Decimal"""
       ...
   ```

2. **Arrange-Act-Assert pattern:**
   ```python
   def test_example():
       # Arrange
       valoare = Decimal("100.00")

       # Act
       rezultat = calculeaza_ceva(valoare)

       # Assert
       assert rezultat == Decimal("expected")
   ```

3. **Folosește fixtures pentru setup:**
   ```python
   def test_cu_db(mock_depcred_db):
       conn = sqlite3.connect(mock_depcred_db)
       # ... test ...
   ```

4. **Markeri pentru organizare:**
   ```python
   @pytest.mark.unit
   @pytest.mark.critical
   @pytest.mark.decimal_precision
   def test_important():
       ...
   ```

### Validare Decimal

```python
# ✅ CORECT
from decimal import Decimal, ROUND_HALF_UP

valoare = Decimal("100.00")
rezultat = (valoare * Decimal("0.04")).quantize(Decimal("0.01"), ROUND_HALF_UP)

# ❌ GREȘIT
valoare = 100.00  # float
rezultat = valoare * 0.04  # erori rotunjire
```

---

## 🎯 Obiective Viitoare

### Module de Testat

- [ ] test_conversie_widget_ui.py - Teste UI pentru conversie
- [ ] test_generare_luna_ui.py - Teste UI pentru generare lună
- [ ] test_listari.py - Teste export PDF chitanțe
- [ ] test_securitate.py - Teste vulnerabilități și injecții

### Îmbunătățiri Coverage

- [ ] Crește coverage conversie_widget la >80%
- [ ] Adaugă teste pentru cazuri edge (membri cu date incomplete)
- [ ] Teste pentru performanță (800 membri simulați)

### Automatizare

- [ ] Integrare GitHub Actions CI/CD
- [ ] Badge-uri coverage în README.md
- [ ] Pre-commit hooks pentru rulare teste

---

## 📚 Resurse

### Documentație pytest

- **Pytest oficial:** https://docs.pytest.org/
- **pytest-cov:** https://pytest-cov.readthedocs.io/
- **pytest-qt:** https://pytest-qt.readthedocs.io/

### Documentație Decimal

- **Python Decimal:** https://docs.python.org/3/library/decimal.html

### Proiect CARpetrosani

- **README.md:** Documentație generală proiect
- **BUGURI_IDENTIFICATE.md:** Raport buguri și rezolvări
- **Claude.md:** Contribuții Claude AI

---

## 🤝 Contribuții

### Rulează teste înainte de commit

```bash
# Rulează toate testele
pytest -v

# Verifică coverage
pytest --cov=. --cov-report=term

# Verifică linting (dacă ai flake8)
flake8 tests/
```

### Adaugă teste pentru buguri noi

1. Creează test care reproduce bug-ul
2. Verifică că testul eșuează
3. Implementează fix
4. Verifică că testul trece
5. Commit cu test și fix împreună

---

## 📞 Contact

Pentru întrebări despre teste:
- **Documentație:** Acest fișier (README_TESTS.md)
- **Buguri:** BUGURI_IDENTIFICATE.md
- **Contribuții AI:** Claude.md

---

**Versiune documentație:** 1.0.0
**Ultima actualizare:** 2025-11-20
**Autor:** Claude (AI Assistant)
