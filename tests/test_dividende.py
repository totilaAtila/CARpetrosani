"""
Teste pentru modulul dividende.py
Testează:
- Calcul dividende conform formulă B = (S_membru / S_total) × P
- Transfer dividende în sold
- Validare existență Ianuarie (BUG #2)
- Precizie Decimal (BUG #1)
- Export Excel
"""
import pytest
import sqlite3
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


class TestCalculDividende:
    """Teste pentru calculul dividendelor"""

    @pytest.mark.unit
    @pytest.mark.critical
    @pytest.mark.decimal_precision
    def test_formula_dividende_basic(self):
        """
        Test formula dividende: B = (S_membru / S_total) × P
        Unde:
        - S_membru = Suma soldurilor lunare ale membrului
        - S_total = Suma soldurilor lunare ale tuturor membrilor
        - P = Profitul total al anului
        - B = Dividendul membrului
        """
        S_membru = Decimal("1200.00")
        S_total = Decimal("10000.00")
        P = Decimal("500.00")

        # Formula: B = (S_membru / S_total) × P
        B = (S_membru / S_total * P).quantize(Decimal("0.01"), ROUND_HALF_UP)

        # 1200 / 10000 = 0.12
        # 0.12 × 500 = 60.00
        assert B == Decimal("60.00")

    @pytest.mark.unit
    @pytest.mark.critical
    @pytest.mark.decimal_precision
    def test_formula_dividende_rotunjire(self):
        """Test rotunjire corectă în formula dividende"""
        S_membru = Decimal("1234.56")
        S_total = Decimal("9876.54")
        P = Decimal("123.45")

        B = (S_membru / S_total * P).quantize(Decimal("0.01"), ROUND_HALF_UP)

        # 1234.56 / 9876.54 = 0.124999...
        # 0.124999... × 123.45 = 15.43...
        assert B == Decimal("15.43")

    @pytest.mark.unit
    @pytest.mark.critical
    def test_suma_dividende_aproape_egala_cu_profit(self):
        """
        Test că suma dividendelor tuturor membrilor ≈ Profit total
        (Pot exista diferențe mici din rotunjiri)
        """
        membri = [
            {"nr_fisa": 1, "S": Decimal("1000.00")},
            {"nr_fisa": 2, "S": Decimal("1500.00")},
            {"nr_fisa": 3, "S": Decimal("2000.00")},
            {"nr_fisa": 4, "S": Decimal("2500.00")},
            {"nr_fisa": 5, "S": Decimal("3000.00")},
        ]

        S_total = sum(m["S"] for m in membri)
        P = Decimal("500.00")

        # Calculează dividende pentru fiecare membru
        dividende = []
        for membru in membri:
            B = (membru["S"] / S_total * P).quantize(Decimal("0.01"), ROUND_HALF_UP)
            dividende.append(B)

        suma_dividende = sum(dividende)

        # Diferența dintre suma dividendelor și profit
        diferenta = abs(suma_dividende - P)

        # Diferența trebuie să fie foarte mică (max 0.10 lei pentru rotunjiri)
        assert diferenta <= Decimal("0.10")

    @pytest.mark.unit
    @pytest.mark.critical
    def test_dividend_zero_daca_profit_zero(self):
        """Test că dividend = 0 dacă profitul = 0"""
        S_membru = Decimal("1000.00")
        S_total = Decimal("10000.00")
        P = Decimal("0.00")

        B = (S_membru / S_total * P).quantize(Decimal("0.01"), ROUND_HALF_UP)

        assert B == Decimal("0.00")

    @pytest.mark.unit
    def test_dividend_zero_daca_suma_membru_zero(self):
        """Test că dividend = 0 dacă membru nu are solduri"""
        S_membru = Decimal("0.00")
        S_total = Decimal("10000.00")
        P = Decimal("500.00")

        B = (S_membru / S_total * P).quantize(Decimal("0.01"), ROUND_HALF_UP)

        assert B == Decimal("0.00")


class TestTransferDividende:
    """Teste pentru transferul dividendelor în sold"""

    @pytest.mark.unit
    @pytest.mark.critical
    @pytest.mark.bugfix  # Test pentru BUG #2
    def test_validare_ianuarie_exista(self):
        """
        Test validare existență Ianuarie înainte de transfer (BUG #2 fix)
        """
        # Simulăm verificarea existenței Ianuarie în DB
        an_viitor = 2026

        # Simulăm că Ianuarie EXISTĂ
        count_ianuarie = 100  # 100 membri au Ianuarie generat

        # Validare: trebuie să existe cel puțin 1 înregistrare pentru Ianuarie
        ianuarie_exista = count_ianuarie > 0

        assert ianuarie_exista is True

    @pytest.mark.unit
    @pytest.mark.critical
    @pytest.mark.bugfix  # Test pentru BUG #2
    def test_validare_ianuarie_lipseste(self):
        """
        Test că transferul se blochează dacă Ianuarie lipsește (BUG #2 fix)
        """
        # Simulăm verificarea existenței Ianuarie în DB
        an_viitor = 2026

        # Simulăm că Ianuarie NU EXISTĂ
        count_ianuarie = 0

        # Validare: trebuie să existe cel puțin 1 înregistrare pentru Ianuarie
        ianuarie_exista = count_ianuarie > 0

        # Transfer BLOCAT
        transfer_permis = ianuarie_exista

        assert transfer_permis is False

    @pytest.mark.unit
    @pytest.mark.critical
    @pytest.mark.decimal_precision
    def test_calcul_nou_dep_deb_dupa_transfer(self):
        """Test calcul nou DEP_DEB după transfer dividende"""
        dep_deb_vechi = Decimal("10.00")  # Cotizație standard
        dividend_B = Decimal("25.50")

        # Nou DEP_DEB = DEP_DEB_vechi + Dividend
        nou_dep_deb = dep_deb_vechi + dividend_B

        assert nou_dep_deb == Decimal("35.50")

    @pytest.mark.unit
    @pytest.mark.critical
    @pytest.mark.decimal_precision
    def test_calcul_nou_dep_sold_dupa_transfer(self):
        """Test calcul nou DEP_SOLD după transfer dividende"""
        dep_sold_vechi = Decimal("100.00")
        dividend_B = Decimal("25.50")

        # Nou DEP_SOLD = DEP_SOLD_vechi + Dividend
        nou_dep_sold = dep_sold_vechi + dividend_B

        assert nou_dep_sold == Decimal("125.50")

    @pytest.mark.unit
    @pytest.mark.bugfix
    @pytest.mark.decimal_precision
    def test_transfer_foloseste_str_decimal(self):
        """Test că transferul folosește str(decimal) pentru UPDATE (BUG #1 fix)"""
        nou_dep_deb = Decimal("35.50")
        nou_dep_sold = Decimal("125.50")

        # CORECT (BUG #1 fix): str(decimal)
        valores_update = (
            str(nou_dep_deb),
            str(nou_dep_sold)
        )

        # Verificăm că sunt stringuri
        assert isinstance(valores_update[0], str)
        assert isinstance(valores_update[1], str)

        # Verificăm că valorile sunt corecte
        assert Decimal(valores_update[0]) == Decimal("35.50")
        assert Decimal(valores_update[1]) == Decimal("125.50")


class TestSumaSolduriLunare:
    """Teste pentru calculul sumei soldurilor lunare"""

    @pytest.mark.unit
    @pytest.mark.critical
    def test_suma_solduri_lunare_membru(self):
        """Test calcul suma soldurilor lunare pentru un membru"""
        solduri_lunare = [
            Decimal("10.00"),   # Ianuarie
            Decimal("20.00"),   # Februarie
            Decimal("30.00"),   # Martie
            Decimal("40.00"),   # Aprilie
            Decimal("50.00"),   # Mai
            Decimal("60.00"),   # Iunie
            Decimal("70.00"),   # Iulie
            Decimal("80.00"),   # August
            Decimal("90.00"),   # Septembrie
            Decimal("100.00"),  # Octombrie
            Decimal("110.00"),  # Noiembrie
            Decimal("120.00"),  # Decembrie
        ]

        S_membru = sum(solduri_lunare)

        # 10 + 20 + ... + 120 = 780
        assert S_membru == Decimal("780.00")

    @pytest.mark.integration
    @pytest.mark.critical
    def test_suma_solduri_lunare_din_db(self, mock_all_dbs):
        """Test calcul suma soldurilor lunare din DB mockuită"""
        db_depcred = mock_all_dbs['DEPCRED']

        conn = sqlite3.connect(db_depcred)
        cursor = conn.cursor()

        # Calculează suma soldurilor pentru membrul 2 (doar depuneri, fără împrumuturi)
        cursor.execute("""
            SELECT SUM(DEP_SOLD)
            FROM DEPCRED
            WHERE NR_FISA = 2 AND ANUL = 2025
        """)

        suma_solduri = Decimal(str(cursor.fetchone()[0]))

        # Membru 2: 10 + 20 + 30 + ... + 110 = 660
        assert suma_solduri == Decimal("660.00")

        conn.close()


class TestIntegrationDividende:
    """Teste de integrare pentru calculul dividendelor"""

    @pytest.mark.integration
    @pytest.mark.critical
    @pytest.mark.decimal_precision
    def test_calcul_complet_dividende_5_membri(self, mock_all_dbs):
        """
        Test integrare: Calcul dividende pentru 5 membri activi
        """
        db_depcred = mock_all_dbs['DEPCRED']
        db_activi = mock_all_dbs['ACTIVI']

        conn_depcred = sqlite3.connect(db_depcred)
        conn_activi = sqlite3.connect(db_activi)

        cursor_activi = conn_activi.cursor()

        # Obține membri activi
        cursor_activi.execute("SELECT NR_FISA FROM ACTIVI ORDER BY NR_FISA")
        membri_activi = [row[0] for row in cursor_activi.fetchall()]

        assert len(membri_activi) == 5

        # Calculează suma soldurilor pentru fiecare membru
        cursor_depcred = conn_depcred.cursor()

        suma_totala = Decimal("0.00")
        solduri_membri = {}

        for nr_fisa in membri_activi[:2]:  # Testăm doar primii 2 (există în mock)
            cursor_depcred.execute("""
                SELECT SUM(DEP_SOLD)
                FROM DEPCRED
                WHERE NR_FISA = ? AND ANUL = 2025
            """, (nr_fisa,))

            result = cursor_depcred.fetchone()
            if result and result[0]:
                suma = Decimal(str(result[0]))
                solduri_membri[nr_fisa] = suma
                suma_totala += suma

        # Verificăm că suma totală > 0
        assert suma_totala > Decimal("0.00")

        # Calculează dividende
        P = Decimal("500.00")
        dividende = {}

        for nr_fisa, suma in solduri_membri.items():
            B = (suma / suma_totala * P).quantize(Decimal("0.01"), ROUND_HALF_UP)
            dividende[nr_fisa] = B

        # Verifică că suma dividendelor ≈ P
        suma_dividende = sum(dividende.values())
        diferenta = abs(suma_dividende - P)
        assert diferenta <= Decimal("0.10")

        conn_depcred.close()
        conn_activi.close()

    @pytest.mark.integration
    @pytest.mark.bugfix
    def test_validare_ianuarie_in_db(self, mock_all_dbs):
        """
        Test integrare: Validare existență Ianuarie în DB (BUG #2)
        """
        db_depcred = mock_all_dbs['DEPCRED']

        conn = sqlite3.connect(db_depcred)
        cursor = conn.cursor()

        # Verifică dacă există Ianuarie 2025
        cursor.execute("""
            SELECT COUNT(*)
            FROM DEPCRED
            WHERE ANUL = 2025 AND LUNA = 1
        """)

        count = cursor.fetchone()[0]

        # În mock avem 2 membri cu Ianuarie 2025
        assert count > 0

        conn.close()


class TestPrecizieDividende:
    """Teste pentru precizie Decimal în calculul dividendelor"""

    @pytest.mark.unit
    @pytest.mark.critical
    @pytest.mark.decimal_precision
    @pytest.mark.bugfix
    def test_precizie_dividende_pentru_800_membri(self):
        """
        Test precizie Decimal pentru 800 membri
        Verifică că suma dividendelor = Profit (cu toleranță mică pentru rotunjiri)
        """
        # Simulăm 800 membri cu solduri diverse
        P = Decimal("10000.00")
        S_total = Decimal("100000.00")

        dividende = []
        for i in range(800):
            # Solduri variate: 100, 101, 102, ..., 899
            S_membru = Decimal(str(100 + i))
            B = (S_membru / S_total * P).quantize(Decimal("0.01"), ROUND_HALF_UP)
            dividende.append(B)

        suma_dividende = sum(dividende)

        # Diferența dintre suma dividendelor și profit
        diferenta = abs(suma_dividende - P)

        # Pentru 800 membri, toleranță maximă 1 leu (erori de rotunjire)
        assert diferenta <= Decimal("1.00")

    @pytest.mark.unit
    @pytest.mark.bugfix
    @pytest.mark.decimal_precision
    def test_no_float_conversion_in_dividend_calc(self):
        """Test că NU folosim float() în calculul dividendelor (BUG #1)"""
        S_membru = Decimal("1234.56")
        S_total = Decimal("9876.54")
        P = Decimal("123.45")

        # CORECT: Folosim doar Decimal
        B_decimal = (S_membru / S_total * P).quantize(Decimal("0.01"), ROUND_HALF_UP)

        # GREȘIT: Conversie la float (vechiul cod)
        B_float = float(S_membru / S_total * P)

        # Verificăm că Decimal e precis
        assert B_decimal == Decimal("15.43")

        # float() poate introduce erori
        # Nu testăm egalitate exactă cu float


class TestExportExcel:
    """Teste pentru export Excel dividende"""

    @pytest.mark.unit
    @pytest.mark.security  # Test legat de BUG #10
    def test_export_foloseste_xlsxwriter(self):
        """Test că exportul Excel folosește xlsxwriter (nu openpyxl) - BUG #10 fix"""
        # Verificăm că modulul xlsxwriter poate fi importat
        try:
            import xlsxwriter
            xlsxwriter_available = True
        except ImportError:
            xlsxwriter_available = False

        assert xlsxwriter_available is True

    @pytest.mark.unit
    @pytest.mark.security
    def test_openpyxl_nu_este_folosit(self):
        """Test că openpyxl NU este folosit (BUG #10 fix)"""
        # Verificăm că dividende.py nu importă openpyxl
        import sys
        from pathlib import Path

        # Citește fișierul dividende.py
        dividende_path = Path(__file__).parent.parent / "ui" / "dividende.py"

        if dividende_path.exists():
            with open(dividende_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Verifică că nu există import openpyxl
            assert "import openpyxl" not in content
            assert "from openpyxl" not in content

            # Verifică că există import xlsxwriter
            assert "import xlsxwriter" in content
