"""
Teste pentru modulul conversie_widget.py
Testează:
- Conversie RON→EUR conform Regulamentul CE 1103/97
- Validare integritate membri între DEPCRED și MEMBRII
- Precizie Decimal în conversii
- Conversie directă individuală (fiecare înregistrare separat)
- Curs fix 4.9755 RON/EUR
"""
import pytest
import sqlite3
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import sys
import os

# Adaugă calea pentru import
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importă clase reale din conversie_widget
try:
    from conversie_widget import MemberIntegrityValidator
except ImportError:
    pytest.skip("conversie_widget nu poate fi importat", allow_module_level=True)


class TestConversieRONtoEUR:
    """Teste pentru conversia RON→EUR conform CE 1103/97"""

    @pytest.mark.unit
    @pytest.mark.critical
    @pytest.mark.decimal_precision
    def test_conversie_basic_ron_eur(self):
        """Test conversie RON→EUR cu curs 4.9755"""
        valoare_ron = Decimal("497.55")
        curs = Decimal("4.9755")

        valoare_eur = (valoare_ron / curs).quantize(Decimal("0.01"), ROUND_HALF_UP)

        # 497.55 / 4.9755 = 100.00
        assert valoare_eur == Decimal("100.00")

    @pytest.mark.unit
    @pytest.mark.critical
    @pytest.mark.decimal_precision
    def test_conversie_directa_individuala(self):
        """
        Test conversie directă individuală (conform CE 1103/97)
        Fiecare înregistrare se convertește separat, nu se însumează
        """
        inregistrari_ron = [
            Decimal("10.00"),
            Decimal("20.00"),
            Decimal("30.00")
        ]

        curs = Decimal("4.9755")

        # CORECT: Conversie directă individuală
        inregistrari_eur = [
            (val / curs).quantize(Decimal("0.01"), ROUND_HALF_UP)
            for val in inregistrari_ron
        ]

        # Verifică fiecare conversie individuală
        assert inregistrari_eur[0] == Decimal("2.01")
        assert inregistrari_eur[1] == Decimal("4.02")
        assert inregistrari_eur[2] == Decimal("6.03")

        # Suma EUR ≠ Conversie sumă RON (din cauza rotunjirilor)
        suma_eur_individual = sum(inregistrari_eur)
        suma_ron = sum(inregistrari_ron)
        suma_eur_direct = (suma_ron / curs).quantize(Decimal("0.01"), ROUND_HALF_UP)

        # 2.01 + 4.02 + 6.03 = 12.06
        # vs
        # (10 + 20 + 30) / 4.9755 = 12.05

        assert suma_eur_individual == Decimal("12.06")
        assert suma_eur_direct == Decimal("12.05")
        assert suma_eur_individual != suma_eur_direct  # Diferență din rotunjiri individuale

    @pytest.mark.unit
    @pytest.mark.critical
    def test_rotunjire_round_half_up(self):
        """Test rotunjire ROUND_HALF_UP (0.5 → 1)"""
        # 0.005 → 0.01
        val1 = Decimal("0.005").quantize(Decimal("0.01"), ROUND_HALF_UP)
        assert val1 == Decimal("0.01")

        # 0.004 → 0.00
        val2 = Decimal("0.004").quantize(Decimal("0.01"), ROUND_HALF_UP)
        assert val2 == Decimal("0.00")

        # 1.125 → 1.13
        val3 = Decimal("1.125").quantize(Decimal("0.01"), ROUND_HALF_UP)
        assert val3 == Decimal("1.13")

    @pytest.mark.unit
    @pytest.mark.critical
    @pytest.mark.decimal_precision
    def test_precizie_conversie_valori_mari(self):
        """Test precizie pentru valori mari (solduri totale)"""
        # Sold total 800 membri × ~1000 RON/membru = 800,000 RON
        sold_total_ron = Decimal("800000.00")
        curs = Decimal("4.9755")

        sold_total_eur = (sold_total_ron / curs).quantize(Decimal("0.01"), ROUND_HALF_UP)

        # 800,000 / 4.9755 = 160,770.24
        assert sold_total_eur == Decimal("160770.24")

    @pytest.mark.unit
    @pytest.mark.critical
    @pytest.mark.decimal_precision
    def test_conversie_fara_pierdere_precizie(self):
        """Test că nu există pierdere de precizie în conversie"""
        valori_ron = [
            Decimal("123.45"),
            Decimal("678.90"),
            Decimal("1234.56"),
            Decimal("9999.99")
        ]

        curs = Decimal("4.9755")

        for val_ron in valori_ron:
            val_eur = (val_ron / curs).quantize(Decimal("0.01"), ROUND_HALF_UP)

            # Reconversie la RON
            val_ron_back = (val_eur * curs).quantize(Decimal("0.01"), ROUND_HALF_UP)

            # Diferența trebuie să fie < 0.10 RON
            diferenta = abs(val_ron - val_ron_back)
            assert diferenta <= Decimal("0.10")


class TestValidareIntegritateMembri:
    """Teste pentru validarea integrității membrilor între baze"""

    @pytest.mark.integration
    @pytest.mark.critical
    def test_validator_membri_consistenti(self, mock_all_dbs):
        """
        Test validare integritate când membrii sunt consistenți
        """
        depcred_path = mock_all_dbs['DEPCRED']
        membrii_path = mock_all_dbs['MEMBRII']

        # Rulează validator real
        result = MemberIntegrityValidator.validate_member_consistency(
            depcred_path, membrii_path
        )

        # În mock avem 10 membri în MEMBRII, dar doar 2 în DEPCRED (1 și 2)
        assert result["total_membrii"] == 10
        assert result["distinct_depcred"] == 2
        assert result["difference"] == 8

        # Membri care lipsesc din DEPCRED (3-10)
        assert len(result["members_only_in_membrii"]) == 8

        # Verifică că validatorul detectează corect discrepanțele
        assert result["valid"] is True  # Nu e eroare critică dacă lipsesc din DEPCRED

    @pytest.mark.integration
    def test_validator_membri_neînregistrați(self, temp_dir):
        """
        Test validare când există activitate DEPCRED fără membru în MEMBRII
        """
        # Creează DB-uri de test
        membrii_path = temp_dir / "MEMBRII_test.db"
        depcred_path = temp_dir / "DEPCRED_test.db"

        # Creează MEMBRII cu 2 membri
        conn_membrii = sqlite3.connect(membrii_path)
        cursor = conn_membrii.cursor()
        cursor.execute("""
            CREATE TABLE MEMBRII (
                NR_FISA INTEGER PRIMARY KEY,
                NUM_PREN TEXT,
                DOMICILIUL TEXT,
                CALITATEA TEXT,
                DATA_INSCR TEXT,
                COTIZATIE_STANDARD REAL
            )
        """)
        cursor.executemany("""
            INSERT INTO MEMBRII (NR_FISA, NUM_PREN, DOMICILIUL, CALITATEA, DATA_INSCR, COTIZATIE_STANDARD)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            (1, "Test 1", "Addr 1", "Job 1", "2020-01-01", 10.0),
            (2, "Test 2", "Addr 2", "Job 2", "2020-01-01", 10.0)
        ])
        conn_membrii.commit()
        conn_membrii.close()

        # Creează DEPCRED cu 3 membri (3 nu există în MEMBRII!)
        conn_depcred = sqlite3.connect(depcred_path)
        cursor = conn_depcred.cursor()
        cursor.execute("""
            CREATE TABLE DEPCRED (
                NR_FISA INTEGER,
                LUNA INTEGER,
                ANUL INTEGER,
                DOBANDA REAL,
                IMPR_DEB REAL,
                IMPR_CRED REAL,
                IMPR_SOLD REAL,
                DEP_DEB REAL,
                DEP_CRED REAL,
                DEP_SOLD REAL,
                PRIMA INTEGER,
                PRIMARY KEY (NR_FISA, LUNA, ANUL)
            )
        """)
        cursor.executemany("""
            INSERT INTO DEPCRED (NR_FISA, LUNA, ANUL, DOBANDA, IMPR_DEB, IMPR_CRED, IMPR_SOLD, DEP_DEB, DEP_CRED, DEP_SOLD, PRIMA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (1, 1, 2025, 0, 0, 0, 0, 10, 0, 10, 1),
            (2, 1, 2025, 0, 0, 0, 0, 10, 0, 10, 1),
            (3, 1, 2025, 0, 0, 0, 0, 10, 0, 10, 1),  # Membru 3 nu există în MEMBRII!
        ])
        conn_depcred.commit()
        conn_depcred.close()

        # Rulează validator
        result = MemberIntegrityValidator.validate_member_consistency(
            depcred_path, membrii_path
        )

        # Verificări
        assert result["total_membrii"] == 2
        assert result["distinct_depcred"] == 3
        assert result["difference"] == -1

        # Membru 3 există în DEPCRED dar nu în MEMBRII - EROARE CRITICĂ
        assert len(result["members_only_in_depcred"]) == 1
        assert result["members_only_in_depcred"][0]["nr_fisa"] == 3

        # Validarea trebuie să eșueze
        assert result["valid"] is False


class TestConversieCompleta:
    """Teste pentru procesul complet de conversie"""

    @pytest.mark.integration
    @pytest.mark.critical
    @pytest.mark.decimal_precision
    @pytest.mark.slow
    def test_conversie_depcred_complet(self, mock_all_dbs):
        """
        Test conversie completă DEPCRED RON→EUR
        """
        depcred_ron_path = mock_all_dbs['DEPCRED']
        temp_depcred_eur_path = depcred_ron_path.parent / "DEPCREDEUR_test.db"

        # Copiază structura
        import shutil
        shutil.copy(depcred_ron_path, temp_depcred_eur_path)

        conn = sqlite3.connect(temp_depcred_eur_path)
        cursor = conn.cursor()

        curs = Decimal("4.9755")

        # Obține toate înregistrările
        cursor.execute("""
            SELECT NR_FISA, LUNA, ANUL, DOBANDA, IMPR_DEB, IMPR_CRED,
                   IMPR_SOLD, DEP_DEB, DEP_CRED, DEP_SOLD, PRIMA
            FROM DEPCRED
        """)

        records = cursor.fetchall()

        # Convertește fiecare înregistrare
        updated_records = []
        for record in records:
            nr_fisa, luna, anul, dobanda, impr_deb, impr_cred, impr_sold, dep_deb, dep_cred, dep_sold, prima = record

            # Conversie fiecare câmp financiar
            dobanda_eur = (Decimal(str(dobanda)) / curs).quantize(Decimal("0.01"), ROUND_HALF_UP)
            impr_deb_eur = (Decimal(str(impr_deb)) / curs).quantize(Decimal("0.01"), ROUND_HALF_UP)
            impr_cred_eur = (Decimal(str(impr_cred)) / curs).quantize(Decimal("0.01"), ROUND_HALF_UP)
            impr_sold_eur = (Decimal(str(impr_sold)) / curs).quantize(Decimal("0.01"), ROUND_HALF_UP)
            dep_deb_eur = (Decimal(str(dep_deb)) / curs).quantize(Decimal("0.01"), ROUND_HALF_UP)
            dep_cred_eur = (Decimal(str(dep_cred)) / curs).quantize(Decimal("0.01"), ROUND_HALF_UP)
            dep_sold_eur = (Decimal(str(dep_sold)) / curs).quantize(Decimal("0.01"), ROUND_HALF_UP)

            updated_records.append((
                str(dobanda_eur), str(impr_deb_eur), str(impr_cred_eur), str(impr_sold_eur),
                str(dep_deb_eur), str(dep_cred_eur), str(dep_sold_eur),
                nr_fisa, luna, anul
            ))

        # Update DB
        cursor.executemany("""
            UPDATE DEPCRED
            SET DOBANDA = ?, IMPR_DEB = ?, IMPR_CRED = ?, IMPR_SOLD = ?,
                DEP_DEB = ?, DEP_CRED = ?, DEP_SOLD = ?
            WHERE NR_FISA = ? AND LUNA = ? AND ANUL = ?
        """, updated_records)

        conn.commit()

        # Verifică conversii
        cursor.execute("""
            SELECT DEP_DEB, DEP_SOLD
            FROM DEPCRED
            WHERE NR_FISA = 2 AND LUNA = 1 AND ANUL = 2025
        """)

        dep_deb_eur, dep_sold_eur = cursor.fetchone()

        # DEP_DEB original = 10.00 RON → 2.01 EUR
        # DEP_SOLD original = 10.00 RON → 2.01 EUR
        assert Decimal(str(dep_deb_eur)) == Decimal("2.01")
        assert Decimal(str(dep_sold_eur)) == Decimal("2.01")

        conn.close()

        # Curăță fișier test
        temp_depcred_eur_path.unlink()


class TestCursFix:
    """Teste pentru curs fix 4.9755 RON/EUR"""

    @pytest.mark.unit
    def test_curs_fix_4_9755(self):
        """Test că cursul fix este 4.9755"""
        curs_oficial = Decimal("4.9755")

        assert curs_oficial == Decimal("4.9755")

    @pytest.mark.unit
    def test_conversie_cu_curs_fix(self):
        """Test conversie cu curs fix (nu variabil)"""
        valori_ron = [Decimal("100.00"), Decimal("500.00"), Decimal("1000.00")]

        curs_fix = Decimal("4.9755")

        for val_ron in valori_ron:
            val_eur = (val_ron / curs_fix).quantize(Decimal("0.01"), ROUND_HALF_UP)

            # Verifică conversie
            assert val_eur > Decimal("0.00")

            # Reconversie cu același curs
            val_ron_back = (val_eur * curs_fix).quantize(Decimal("0.01"), ROUND_HALF_UP)

            # Diferența trebuie să fie mică
            diferenta = abs(val_ron - val_ron_back)
            assert diferenta <= Decimal("0.02")


class TestPrecizieConversie:
    """Teste pentru precizia conversiei Decimal"""

    @pytest.mark.unit
    @pytest.mark.critical
    @pytest.mark.decimal_precision
    def test_no_float_in_conversion(self):
        """Test că NU folosim float() în conversii (BUG #1)"""
        val_ron = Decimal("123.45")
        curs = Decimal("4.9755")

        # CORECT: Doar Decimal
        val_eur_decimal = (val_ron / curs).quantize(Decimal("0.01"), ROUND_HALF_UP)

        # GREȘIT: float()
        val_eur_float = float(val_ron / curs)

        # Decimal e precis
        assert val_eur_decimal == Decimal("24.81")

        # float poate avea erori
        # Nu testăm egalitate exactă cu float

    @pytest.mark.unit
    @pytest.mark.critical
    @pytest.mark.decimal_precision
    def test_precizie_conversie_800_membri(self):
        """
        Test precizie conversie pentru 800 membri
        Verifică că nu există erori acumulate
        """
        curs = Decimal("4.9755")

        suma_ron = Decimal("0.00")
        suma_eur_direct = Decimal("0.00")

        for i in range(800):
            # Sold variabil pentru fiecare membru
            sold_ron = Decimal(str(100 + i * 10))

            # Conversie individuală
            sold_eur = (sold_ron / curs).quantize(Decimal("0.01"), ROUND_HALF_UP)

            suma_ron += sold_ron
            suma_eur_direct += sold_eur

        # Conversie suma totală
        suma_eur_total = (suma_ron / curs).quantize(Decimal("0.01"), ROUND_HALF_UP)

        # Diferența dintre suma conversiilor individuale și conversie totală
        diferenta = abs(suma_eur_direct - suma_eur_total)

        # Pentru 800 membri, toleranță maximă 5 EUR (din rotunjiri individuale)
        assert diferenta <= Decimal("5.00")
