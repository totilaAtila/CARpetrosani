"""
Configurare pytest și fixtures comune pentru toate testele
"""
import pytest
import sqlite3
import tempfile
import shutil
from pathlib import Path
from decimal import Decimal
from datetime import datetime
from PyQt5.QtWidgets import QApplication
import sys

# Inițializare QApplication pentru teste PyQt5
@pytest.fixture(scope="session")
def qapp():
    """Fixture pentru QApplication (necesară pentru teste PyQt5)"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # Nu închide app - va fi închisă la final


@pytest.fixture
def temp_dir():
    """Fixture pentru director temporar"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_membrii_db(temp_dir):
    """
    Creează bază de date mockuită MEMBRII.db cu date de test
    """
    db_path = temp_dir / "MEMBRII.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Schema MEMBRII
    cursor.execute("""
        CREATE TABLE MEMBRII (
            NR_FISA INTEGER PRIMARY KEY,
            NUM_PREN TEXT NOT NULL,
            DOMICILIUL TEXT,
            CALITATEA TEXT,
            DATA_INSCR TEXT,
            COTIZATIE_STANDARD REAL DEFAULT 10.00
        )
    """)

    # Date de test - 10 membri
    membri_test = [
        (1, "Popescu Ion", "Str. Libertății 1", "Inginer", "2020-01-01", 10.00),
        (2, "Ionescu Maria", "Str. Libertății 2", "Contabil", "2020-01-01", 10.00),
        (3, "Georgescu Ana", "Str. Libertății 3", "Director", "2020-01-01", 15.00),
        (4, "Vasilescu Dan", "Str. Libertății 4", "Muncitor", "2020-01-01", 10.00),
        (5, "Dumitrescu Elena", "Str. Libertății 5", "Economist", "2020-01-01", 10.00),
        (6, "Radu Mihai", "Str. Libertății 6", "Tehnician", "2021-01-01", 10.00),
        (7, "Popa Carmen", "Str. Libertății 7", "Secretar", "2021-01-01", 10.00),
        (8, "Stan Victor", "Str. Libertății 8", "Șofer", "2021-01-01", 10.00),
        (9, "Marin Ioana", "Str. Libertății 9", "Funcționar", "2022-01-01", 10.00),
        (10, "Pavel Andrei", "Str. Libertății 10", "Administrator", "2022-01-01", 12.00)
    ]

    cursor.executemany("""
        INSERT INTO MEMBRII (NR_FISA, NUM_PREN, DOMICILIUL, CALITATEA, DATA_INSCR, COTIZATIE_STANDARD)
        VALUES (?, ?, ?, ?, ?, ?)
    """, membri_test)

    conn.commit()
    conn.close()

    return db_path


@pytest.fixture
def mock_depcred_db(temp_dir):
    """
    Creează bază de date mockuită DEPCRED.db cu date de test
    """
    db_path = temp_dir / "DEPCRED.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Schema DEPCRED
    cursor.execute("""
        CREATE TABLE DEPCRED (
            NR_FISA INTEGER NOT NULL,
            LUNA INTEGER NOT NULL,
            ANUL INTEGER NOT NULL,
            DOBANDA REAL DEFAULT 0.0,
            IMPR_DEB REAL DEFAULT 0.0,
            IMPR_CRED REAL DEFAULT 0.0,
            IMPR_SOLD REAL DEFAULT 0.0,
            DEP_DEB REAL DEFAULT 0.0,
            DEP_CRED REAL DEFAULT 0.0,
            DEP_SOLD REAL DEFAULT 0.0,
            PRIMA INTEGER DEFAULT 0,
            PRIMARY KEY (NR_FISA, LUNA, ANUL)
        )
    """)

    # Date de test pentru membrul 1 - Ianuarie-Decembrie 2025
    # Scenariu: Membru cu împrumut achitat în Decembrie
    tranzactii_test = [
        # (NR_FISA, LUNA, ANUL, DOBANDA, IMPR_DEB, IMPR_CRED, IMPR_SOLD, DEP_DEB, DEP_CRED, DEP_SOLD, PRIMA)
        (1, 1, 2025, 0.0, 1000.00, 0.0, 1000.00, 10.00, 0.0, 10.00, 1),    # Ianuarie - împrumut nou
        (1, 2, 2025, 0.0, 0.0, 100.00, 900.00, 10.00, 0.0, 20.00, 0),      # Februarie
        (1, 3, 2025, 0.0, 0.0, 100.00, 800.00, 10.00, 0.0, 30.00, 0),      # Martie
        (1, 4, 2025, 0.0, 0.0, 100.00, 700.00, 10.00, 0.0, 40.00, 0),      # Aprilie
        (1, 5, 2025, 0.0, 0.0, 100.00, 600.00, 10.00, 0.0, 50.00, 0),      # Mai
        (1, 6, 2025, 0.0, 0.0, 100.00, 500.00, 10.00, 0.0, 60.00, 0),      # Iunie
        (1, 7, 2025, 0.0, 0.0, 100.00, 400.00, 10.00, 0.0, 70.00, 0),      # Iulie
        (1, 8, 2025, 0.0, 0.0, 100.00, 300.00, 10.00, 0.0, 80.00, 0),      # August
        (1, 9, 2025, 0.0, 0.0, 100.00, 200.00, 10.00, 0.0, 90.00, 0),      # Septembrie
        (1, 10, 2025, 0.0, 0.0, 100.00, 100.00, 10.00, 0.0, 100.00, 0),    # Octombrie
        (1, 11, 2025, 0.0, 0.0, 100.00, 0.00, 10.00, 0.0, 110.00, 0),      # Noiembrie - achitat
        # Decembrie va fi generat de testul de generare lună cu dobândă calculată
    ]

    # Date pentru membrul 2 - Fără împrumut, doar depuneri
    for luna in range(1, 12):
        tranzactii_test.append((2, luna, 2025, 0.0, 0.0, 0.0, 0.0, 10.00, 0.0, luna * 10.00, 1 if luna == 1 else 0))

    cursor.executemany("""
        INSERT INTO DEPCRED (NR_FISA, LUNA, ANUL, DOBANDA, IMPR_DEB, IMPR_CRED,
                             IMPR_SOLD, DEP_DEB, DEP_CRED, DEP_SOLD, PRIMA)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, tranzactii_test)

    conn.commit()
    conn.close()

    return db_path


@pytest.fixture
def mock_lichidati_db(temp_dir):
    """
    Creează bază de date mockuită LICHIDATI.db cu date de test
    """
    db_path = temp_dir / "LICHIDATI.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Schema LICHIDATI
    cursor.execute("""
        CREATE TABLE lichidati (
            nr_fisa INTEGER PRIMARY KEY,
            data_lichidare TEXT NOT NULL
        )
    """)

    # Date de test - 2 membri lichidați
    cursor.executemany("""
        INSERT INTO lichidati (nr_fisa, data_lichidare)
        VALUES (?, ?)
    """, [
        (99, "2024-12-01"),
        (100, "2024-11-15")
    ])

    conn.commit()
    conn.close()

    return db_path


@pytest.fixture
def mock_activi_db(temp_dir):
    """
    Creează bază de date mockuită ACTIVI.db cu date de test
    """
    db_path = temp_dir / "ACTIVI.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Schema ACTIVI
    cursor.execute("""
        CREATE TABLE ACTIVI (
            NR_FISA INTEGER PRIMARY KEY,
            NUM_PREN TEXT,
            DEP_SOLD REAL,
            DIVIDEND REAL DEFAULT 0.0
        )
    """)

    # Date de test - 5 membri activi
    cursor.executemany("""
        INSERT INTO ACTIVI (NR_FISA, NUM_PREN, DEP_SOLD, DIVIDEND)
        VALUES (?, ?, ?, ?)
    """, [
        (1, "Popescu Ion", 120.00, 0.0),
        (2, "Ionescu Maria", 110.00, 0.0),
        (3, "Georgescu Ana", 180.00, 0.0),
        (4, "Vasilescu Dan", 100.00, 0.0),
        (5, "Dumitrescu Elena", 105.00, 0.0)
    ])

    conn.commit()
    conn.close()

    return db_path


@pytest.fixture
def mock_all_dbs(mock_membrii_db, mock_depcred_db, mock_lichidati_db, mock_activi_db):
    """
    Fixture care returnează toate bazele de date mockuite
    """
    return {
        'MEMBRII': mock_membrii_db,
        'DEPCRED': mock_depcred_db,
        'LICHIDATI': mock_lichidati_db,
        'ACTIVI': mock_activi_db
    }


# Pytest helpers pentru comparații Decimal
def assert_decimal_equal(actual, expected, msg=""):
    """
    Compară două valori Decimal cu toleranță pentru rotunjire
    """
    actual_dec = Decimal(str(actual))
    expected_dec = Decimal(str(expected))
    diff = abs(actual_dec - expected_dec)
    tolerance = Decimal("0.01")  # Toleranță 1 ban

    assert diff <= tolerance, (
        f"{msg}\n"
        f"Expected: {expected_dec}\n"
        f"Actual: {actual_dec}\n"
        f"Difference: {diff} (tolerance: {tolerance})"
    )


# Configurare markers pentru pytest
def pytest_configure(config):
    """Configurare custom markers"""
    config.addinivalue_line("markers", "unit: Teste unitare simple")
    config.addinivalue_line("markers", "integration: Teste de integrare")
    config.addinivalue_line("markers", "slow: Teste care durează >1s")
    config.addinivalue_line("markers", "critical: Teste critice financiare")
    config.addinivalue_line("markers", "bugfix: Teste pentru buguri rezolvate")
    config.addinivalue_line("markers", "decimal_precision: Teste precizie Decimal")
    config.addinivalue_line("markers", "security: Teste securitate")
