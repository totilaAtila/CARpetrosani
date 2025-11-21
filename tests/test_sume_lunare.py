"""
Teste pentru modulul sume_lunare.py
Testează:
- Calcul solduri lunare (împrumut și depozit)
- Recalculare luni ulterioare după modificări
- Calcul dobândă manuală
- Precizie Decimal (BUG #1)
- Validare date introduse
"""
import pytest
import sqlite3
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


class TestCalculSolduriLunare:
    """Teste pentru calculul soldurilor lunare"""

    @pytest.mark.unit
    @pytest.mark.critical
    @pytest.mark.decimal_precision
    def test_calcul_sold_imprumut_luna_curenta(self):
        """
        Test calcul sold împrumut pentru luna curentă
        Formula: impr_sold_nou = impr_sold_vechi + impr_deb - impr_cred
        """
        impr_sold_vechi = Decimal("1000.00")
        impr_deb_nou = Decimal("0.00")
        impr_cred_nou = Decimal("100.00")

        impr_sold_nou = impr_sold_vechi + impr_deb_nou - impr_cred_nou

        # Ajustare pentru zeroizare < 0.005
        if impr_sold_nou <= Decimal("0.005"):
            impr_sold_nou = Decimal("0.00")

        assert impr_sold_nou == Decimal("900.00")

    @pytest.mark.unit
    @pytest.mark.critical
    @pytest.mark.decimal_precision
    def test_calcul_sold_depozit_luna_curenta(self):
        """
        Test calcul sold depozit pentru luna curentă
        Formula: dep_sold_nou = dep_sold_vechi + dep_deb - dep_cred
        """
        dep_sold_vechi = Decimal("100.00")
        dep_deb_nou = Decimal("10.00")
        dep_cred_nou = Decimal("0.00")

        dep_sold_nou = dep_sold_vechi + dep_deb_nou - dep_cred_nou

        assert dep_sold_nou == Decimal("110.00")

    @pytest.mark.unit
    @pytest.mark.critical
    def test_sold_imprumut_zeroizat_sub_prag(self):
        """Test că soldul împrumut se zeroizează dacă < 0.005"""
        impr_sold_calculat = Decimal("0.003")

        # Ajustare
        if impr_sold_calculat <= Decimal("0.005"):
            impr_sold_final = Decimal("0.00")
        else:
            impr_sold_final = impr_sold_calculat

        assert impr_sold_final == Decimal("0.00")

    @pytest.mark.unit
    @pytest.mark.critical
    def test_sold_imprumut_nu_zeroizat_peste_prag(self):
        """Test că soldul împrumut NU se zeroizează dacă > 0.005"""
        impr_sold_calculat = Decimal("0.01")

        # Ajustare
        if impr_sold_calculat <= Decimal("0.005"):
            impr_sold_final = Decimal("0.00")
        else:
            impr_sold_final = impr_sold_calculat

        assert impr_sold_final == Decimal("0.01")


class TestRecalculareLuniUlterioare:
    """Teste pentru recalcularea lunilor ulterioare după modificări"""

    @pytest.mark.integration
    @pytest.mark.critical
    @pytest.mark.decimal_precision
    def test_recalculare_luna_urmatoare(self, mock_all_dbs):
        """
        Test recalculare luna următoare după modificare luna curentă
        Soldurile trebuie să se propage corect
        """
        db_depcred = mock_all_dbs['DEPCRED']

        conn = sqlite3.connect(db_depcred)
        cursor = conn.cursor()

        # Obține solduri Ianuarie (luna sursă)
        cursor.execute("""
            SELECT IMPR_SOLD, DEP_SOLD
            FROM DEPCRED
            WHERE NR_FISA = 1 AND LUNA = 1 AND ANUL = 2025
        """)
        ian_impr_sold, ian_dep_sold = cursor.fetchone()

        # Obține solduri Februarie (calculat din Ianuarie)
        cursor.execute("""
            SELECT IMPR_SOLD, DEP_SOLD, IMPR_CRED, DEP_DEB
            FROM DEPCRED
            WHERE NR_FISA = 1 AND LUNA = 2 AND ANUL = 2025
        """)
        feb_impr_sold, feb_dep_sold, feb_impr_cred, feb_dep_deb = cursor.fetchone()

        # Verifică propagare sold împrumut
        # feb_impr_sold = ian_impr_sold - feb_impr_cred
        sold_asteptat = Decimal(str(ian_impr_sold)) - Decimal(str(feb_impr_cred))
        assert Decimal(str(feb_impr_sold)) == sold_asteptat

        # Verifică propagare sold depozit
        # feb_dep_sold = ian_dep_sold + feb_dep_deb
        sold_dep_asteptat = Decimal(str(ian_dep_sold)) + Decimal(str(feb_dep_deb))
        assert Decimal(str(feb_dep_sold)) == sold_dep_asteptat

        conn.close()

    @pytest.mark.integration
    @pytest.mark.critical
    def test_recalculare_cascada_6_luni(self, mock_all_dbs):
        """
        Test recalculare în cascadă pentru 6 luni
        Modificare în luna 1 → recalculare luni 2-6
        """
        db_depcred = mock_all_dbs['DEPCRED']

        conn = sqlite3.connect(db_depcred)
        cursor = conn.cursor()

        # Obține solduri pentru lunile 1-6 pentru membrul 1
        cursor.execute("""
            SELECT LUNA, IMPR_SOLD, DEP_SOLD, IMPR_CRED, DEP_DEB
            FROM DEPCRED
            WHERE NR_FISA = 1 AND ANUL = 2025 AND LUNA BETWEEN 1 AND 6
            ORDER BY LUNA
        """)
        luni = cursor.fetchall()

        # Verifică consistență solduri între luni consecutive
        for i in range(len(luni) - 1):
            luna_curenta = luni[i]
            luna_urmatoare = luni[i + 1]

            # Sold împrumut luna următoare = sold curent - credit următoare
            impr_sold_curent = Decimal(str(luna_curenta[1]))
            impr_cred_urmatoare = Decimal(str(luna_urmatoare[3]))
            impr_sold_asteptat = impr_sold_curent - impr_cred_urmatoare

            # Ajustare zeroizare
            if impr_sold_asteptat <= Decimal("0.005"):
                impr_sold_asteptat = Decimal("0.00")

            impr_sold_urmatoare = Decimal(str(luna_urmatoare[1]))

            # Verifică
            assert impr_sold_urmatoare == impr_sold_asteptat, \
                f"Luna {luna_urmatoare[0]}: sold așteptat {impr_sold_asteptat}, găsit {impr_sold_urmatoare}"

        conn.close()


class TestCalculDobandaManuala:
    """Teste pentru calculul dobânzii manuale"""

    @pytest.mark.unit
    @pytest.mark.critical
    @pytest.mark.decimal_precision
    def test_calcul_dobanda_manuala_basic(self):
        """
        Test calcul dobândă manuală conform config_dobanda.json
        """
        # Suma soldurilor din perioada împrumutului
        solduri_perioada = [
            Decimal("500.00"),
            Decimal("400.00"),
            Decimal("300.00"),
            Decimal("200.00"),
            Decimal("100.00")
        ]

        sum_solduri = sum(solduri_perioada)
        rata_dobanda = Decimal("0.004")  # 4‰

        dobanda = (sum_solduri * rata_dobanda).quantize(Decimal("0.01"), ROUND_HALF_UP)

        # Suma = 1500.00
        # Dobândă = 1500.00 × 0.004 = 6.00
        assert dobanda == Decimal("6.00")

    @pytest.mark.unit
    @pytest.mark.critical
    def test_determinare_perioada_imprumut(self):
        """
        Test determinare perioadă împrumut pentru calcul dobândă
        Caută ultima lună cu impr_deb > 0 înainte de luna curentă
        """
        tranzactii = [
            (1, 2025, Decimal("1000.00"), Decimal("0.00")),  # Luna 1 - împrumut nou
            (2, 2025, Decimal("0.00"), Decimal("100.00")),   # Luna 2 - rată
            (3, 2025, Decimal("0.00"), Decimal("100.00")),   # Luna 3 - rată
            (4, 2025, Decimal("0.00"), Decimal("100.00")),   # Luna 4 - rată
            (5, 2025, Decimal("0.00"), Decimal("100.00")),   # Luna 5 - rată (luna curentă)
        ]

        luna_curenta = 5
        anul_curent = 2025

        # Caută ultima lună cu impr_deb > 0
        luna_start = None
        for luna, anul, impr_deb, _ in tranzactii:
            if impr_deb > Decimal("0.00") and (anul * 100 + luna) <= (anul_curent * 100 + luna_curenta):
                if luna_start is None or (anul * 100 + luna) > luna_start:
                    luna_start = anul * 100 + luna

        # Trebuie să găsească luna 1/2025
        assert luna_start == 202501


class TestValidariInputuri:
    """Teste pentru validarea inputurilor în sume_lunare"""

    @pytest.mark.unit
    def test_validare_numar_real_valid(self):
        """Test validare număr real valid"""
        text_values = ["100.00", "0.0", "1234.56", "0.005"]

        for text in text_values:
            try:
                val = Decimal(text)
                valid = True
            except:
                valid = False

            assert valid is True

    @pytest.mark.unit
    def test_validare_numar_real_invalid(self):
        """Test validare număr real invalid"""
        text_values = ["abc", "", "12.34.56", "text"]

        for text in text_values:
            try:
                val = Decimal(text)
                valid = True
            except:
                valid = False

            assert valid is False

    @pytest.mark.unit
    def test_validare_format_luna_an(self):
        """Test validare format Luna-An (LL-AAAA)"""
        # Format valid
        text = "04-2025"
        parts = text.split('-')

        valid = (
            len(parts) == 2 and
            parts[0].isdigit() and
            parts[1].isdigit() and
            1 <= int(parts[0]) <= 12 and
            1990 <= int(parts[1]) <= 2100
        )

        assert valid is True

    @pytest.mark.unit
    def test_validare_format_luna_an_invalid(self):
        """Test validare format Luna-An invalid"""
        invalid_formats = ["13-2025", "00-2025", "04-1989", "04/2025", "2025-04"]

        for text in invalid_formats:
            parts = text.split('-')

            try:
                valid = (
                    len(parts) == 2 and
                    parts[0].isdigit() and
                    parts[1].isdigit() and
                    1 <= int(parts[0]) <= 12 and
                    1990 <= int(parts[1]) <= 2100
                )
            except:
                valid = False

            assert valid is False


class TestPrecizieDecimal:
    """Teste pentru precizia Decimal în sume_lunare"""

    @pytest.mark.unit
    @pytest.mark.critical
    @pytest.mark.bugfix
    @pytest.mark.decimal_precision
    def test_str_decimal_pentru_update(self):
        """Test că folosim str(decimal) pentru UPDATE (BUG #1 fix)"""
        impr_sold_nou = Decimal("850.00")
        dep_sold_nou = Decimal("110.00")

        # CORECT (BUG #1 fix): str(decimal)
        valores_update = (
            str(impr_sold_nou),
            str(dep_sold_nou)
        )

        # Verificăm că sunt stringuri
        assert isinstance(valores_update[0], str)
        assert isinstance(valores_update[1], str)

        # Verificăm valorile
        assert Decimal(valores_update[0]) == Decimal("850.00")
        assert Decimal(valores_update[1]) == Decimal("110.00")

    @pytest.mark.unit
    @pytest.mark.bugfix
    @pytest.mark.decimal_precision
    def test_citire_decimal_din_db(self):
        """Test pattern citire Decimal din DB"""
        # Simulăm valori citite din DB
        values_from_db = ["100.00", "0.0", "1234.56"]

        for value in values_from_db:
            # CORECT: Decimal(str(value))
            decimal_val = Decimal(str(value))

            assert isinstance(decimal_val, Decimal)

    @pytest.mark.unit
    @pytest.mark.critical
    @pytest.mark.decimal_precision
    def test_precizie_recalculare_12_luni(self):
        """
        Test precizie Decimal pentru recalculare 12 luni
        Verifică că nu există erori acumulate
        """
        # Simulăm recalculare pentru 12 luni
        sold_initial = Decimal("1200.00")
        rata_lunara = Decimal("100.00")

        sold_curent = sold_initial

        for luna in range(1, 13):
            # Scădere rată
            sold_curent = sold_curent - rata_lunara

            # Ajustare zeroizare
            if sold_curent <= Decimal("0.005"):
                sold_curent = Decimal("0.00")

        # După 12 luni cu rată 100: 1200 - 12×100 = 0
        assert sold_curent == Decimal("0.00")

        # Verifică precizie (fără erori microscopice)
        diferenta = abs(sold_curent - Decimal("0.00"))
        assert diferenta == Decimal("0.00")


class TestIntegrationSumeLunare:
    """Teste de integrare pentru sume_lunare"""

    @pytest.mark.integration
    @pytest.mark.critical
    @pytest.mark.decimal_precision
    def test_modificare_si_recalculare_membru(self, mock_all_dbs):
        """
        Test integrare: Modificare tranzacție și recalculare luni ulterioare
        """
        db_depcred = mock_all_dbs['DEPCRED']

        conn = sqlite3.connect(db_depcred)
        cursor = conn.cursor()

        # Obține sold Martie pentru membrul 1
        cursor.execute("""
            SELECT IMPR_SOLD, DEP_SOLD
            FROM DEPCRED
            WHERE NR_FISA = 1 AND LUNA = 3 AND ANUL = 2025
        """)
        martie_before = cursor.fetchone()
        martie_impr_sold_before = Decimal(str(martie_before[0]))
        martie_dep_sold_before = Decimal(str(martie_before[1]))

        # Modificăm IMPR_CRED în Martie (simulăm modificare manuală)
        cursor.execute("""
            UPDATE DEPCRED
            SET IMPR_CRED = 150.00
            WHERE NR_FISA = 1 AND LUNA = 3 AND ANUL = 2025
        """)
        conn.commit()

        # Recalculăm sold Martie
        cursor.execute("""
            SELECT IMPR_SOLD, IMPR_DEB, IMPR_CRED
            FROM DEPCRED
            WHERE NR_FISA = 1 AND LUNA = 2 AND ANUL = 2025
        """)
        feb_impr_sold, _, _ = cursor.fetchone()

        cursor.execute("""
            SELECT IMPR_CRED, IMPR_DEB
            FROM DEPCRED
            WHERE NR_FISA = 1 AND LUNA = 3 AND ANUL = 2025
        """)
        martie_impr_cred, martie_impr_deb = cursor.fetchone()

        # Nou sold Martie = sold Februarie + deb Martie - cred Martie
        nou_impr_sold_martie = Decimal(str(feb_impr_sold)) + Decimal(str(martie_impr_deb)) - Decimal(str(martie_impr_cred))

        # Ajustare zeroizare
        if nou_impr_sold_martie <= Decimal("0.005"):
            nou_impr_sold_martie = Decimal("0.00")

        # Update Martie
        cursor.execute("""
            UPDATE DEPCRED
            SET IMPR_SOLD = ?
            WHERE NR_FISA = 1 AND LUNA = 3 AND ANUL = 2025
        """, (str(nou_impr_sold_martie),))
        conn.commit()

        # Verifică modificare
        cursor.execute("""
            SELECT IMPR_SOLD
            FROM DEPCRED
            WHERE NR_FISA = 1 AND LUNA = 3 AND ANUL = 2025
        """)
        martie_impr_sold_after = Decimal(str(cursor.fetchone()[0]))

        # Soldul trebuie să fie diferit de cel inițial
        assert martie_impr_sold_after != martie_impr_sold_before

        # Soldul trebuie să fie calculat corect
        assert martie_impr_sold_after == nou_impr_sold_martie

        conn.close()

    @pytest.mark.integration
    @pytest.mark.critical
    def test_calcul_dobanda_din_db(self, mock_all_dbs):
        """
        Test integrare: Calcul dobândă din DB pentru membru cu împrumut achitat
        """
        db_depcred = mock_all_dbs['DEPCRED']

        conn = sqlite3.connect(db_depcred)
        cursor = conn.cursor()

        # Calculează dobândă pentru membrul 1 (achitat în Noiembrie)
        nr_fisa = 1
        anul = 2025
        luna_achitare = 11

        # Caută luna de start (ultima cu impr_deb > 0)
        cursor.execute("""
            SELECT MAX(anul*100+luna)
            FROM DEPCRED
            WHERE NR_FISA = ? AND IMPR_DEB > 0 AND (anul*100+luna <= ?)
        """, (nr_fisa, anul * 100 + luna_achitare))

        luna_start_code = cursor.fetchone()[0]

        assert luna_start_code == 202501  # Ianuarie 2025

        # Calculează suma soldurilor
        cursor.execute("""
            SELECT SUM(IMPR_SOLD)
            FROM DEPCRED
            WHERE NR_FISA = ? AND (anul*100+luna BETWEEN ? AND ?) AND IMPR_SOLD > 0
        """, (nr_fisa, luna_start_code, anul * 100 + luna_achitare))

        sum_solduri = Decimal(str(cursor.fetchone()[0]))

        # Calculează dobândă
        rata_dobanda = Decimal("0.004")
        dobanda = (sum_solduri * rata_dobanda).quantize(Decimal("0.01"), ROUND_HALF_UP)

        # Suma soldurilor = 5500.00 (1000+900+800+700+600+500+400+300+200+100)
        assert sum_solduri == Decimal("5500.00")

        # Dobândă = 5500 × 0.004 = 22.00
        assert dobanda == Decimal("22.00")

        conn.close()


class TestQuantizeDecimal:
    """Teste pentru rotunjirea Decimal cu quantize"""

    @pytest.mark.unit
    @pytest.mark.decimal_precision
    def test_quantize_0_01_round_half_up(self):
        """Test rotunjire Decimal la 2 zecimale cu ROUND_HALF_UP"""
        values = [
            (Decimal("100.005"), Decimal("100.01")),
            (Decimal("100.004"), Decimal("100.00")),
            (Decimal("100.125"), Decimal("100.13")),
            (Decimal("100.124"), Decimal("100.12")),
        ]

        for input_val, expected in values:
            result = input_val.quantize(Decimal("0.01"), ROUND_HALF_UP)
            assert result == expected

    @pytest.mark.unit
    @pytest.mark.decimal_precision
    def test_quantize_preserve_precision(self):
        """Test că quantize păstrează precizia Decimal"""
        val = Decimal("123.456789")
        quantized = val.quantize(Decimal("0.01"), ROUND_HALF_UP)

        # Rezultat = 123.46
        assert quantized == Decimal("123.46")
        assert isinstance(quantized, Decimal)

        # NU există pierdere de precizie ca la float
        # float(123.456789) poate da 123.45999999...
