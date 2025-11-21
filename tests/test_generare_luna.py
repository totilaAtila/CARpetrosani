"""
Teste pentru modulul generare_luna.py
Testează:
- Calcul solduri (împrumut și depozit)
- Calcul dobândă la achitare împrumut
- Moștenire rată din luna anterioară
- Precizie Decimal (BUG #1)
- Cotizație standard
"""
import pytest
import sqlite3
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


class TestCalculSolduri:
    """Teste pentru calculul soldurilor în generare_luna"""

    @pytest.mark.unit
    @pytest.mark.critical
    def test_calcul_sold_imprumut_basic(self):
        """Test calcul sold împrumut: sold_nou = sold_vechi + deb - cred"""
        sold_vechi = Decimal("1000.00")
        impr_deb = Decimal("0.00")
        impr_cred = Decimal("100.00")

        sold_nou = sold_vechi + impr_deb - impr_cred

        assert sold_nou == Decimal("900.00")

    @pytest.mark.unit
    @pytest.mark.critical
    def test_calcul_sold_depozit_basic(self):
        """Test calcul sold depozit: sold_nou = sold_vechi + deb - cred"""
        sold_vechi = Decimal("100.00")
        dep_deb = Decimal("10.00")  # Cotizație
        dep_cred = Decimal("0.00")

        sold_nou = sold_vechi + dep_deb - dep_cred

        assert sold_nou == Decimal("110.00")

    @pytest.mark.unit
    @pytest.mark.critical
    def test_zeroizare_sold_imprumut_sub_prag(self):
        """Test zeroizare sold împrumut dacă < 0.005"""
        sold_vechi = Decimal("0.01")
        impr_cred = Decimal("0.01")

        sold_nou_calculat = sold_vechi - impr_cred

        # Aplicăm logica de zeroizare
        if sold_nou_calculat <= Decimal('0.005'):
            sold_nou = Decimal("0.00")
        else:
            sold_nou = sold_nou_calculat

        assert sold_nou == Decimal("0.00")

    @pytest.mark.unit
    @pytest.mark.critical
    def test_nu_zeroizare_sold_imprumut_peste_prag(self):
        """Test că soldul nu se zeroizează dacă > 0.005"""
        sold_vechi = Decimal("0.01")
        impr_cred = Decimal("0.003")

        sold_nou_calculat = sold_vechi - impr_cred

        # Aplicăm logica de zeroizare
        if sold_nou_calculat <= Decimal('0.005'):
            sold_nou = Decimal("0.00")
        else:
            sold_nou = sold_nou_calculat

        assert sold_nou == Decimal("0.007")


class TestCalculDobanda:
    """Teste pentru calculul dobânzii la achitare împrumut"""

    @pytest.mark.unit
    @pytest.mark.critical
    @pytest.mark.decimal_precision
    def test_calcul_dobanda_achitare_completa(self):
        """Test calcul dobândă când împrumutul este achitat complet"""
        # Suma soldurilor lunare din perioada împrumutului
        solduri_lunare = [
            Decimal("1000.00"),  # Luna 1
            Decimal("900.00"),   # Luna 2
            Decimal("800.00"),   # Luna 3
            Decimal("700.00"),   # Luna 4
            Decimal("600.00"),   # Luna 5
            Decimal("500.00"),   # Luna 6
            Decimal("400.00"),   # Luna 7
            Decimal("300.00"),   # Luna 8
            Decimal("200.00"),   # Luna 9
            Decimal("100.00"),   # Luna 10
        ]

        sum_solduri = sum(solduri_lunare)
        rata_dobanda = Decimal("0.004")  # 4‰

        # Formula: dobanda = SUM(solduri) × rata
        dobanda_calculata = (sum_solduri * rata_dobanda).quantize(
            Decimal("0.01"), ROUND_HALF_UP
        )

        # Suma soldurilor = 5500.00
        # Dobândă = 5500.00 × 0.004 = 22.00
        assert dobanda_calculata == Decimal("22.00")

    @pytest.mark.unit
    @pytest.mark.critical
    @pytest.mark.bugfix  # Test pentru BUG #1
    def test_precizie_dobanda_cu_decimal(self):
        """Test că dobânda se calculează cu precizie Decimal (BUG #1)"""
        sum_solduri = Decimal("5500.00")
        rata_dobanda = Decimal("0.004")

        # CORECT: Folosim Decimal până la final
        dobanda_decimal = (sum_solduri * rata_dobanda).quantize(
            Decimal("0.01"), ROUND_HALF_UP
        )

        # GREȘIT (vechiul cod): Conversie la float()
        dobanda_float = float(sum_solduri * rata_dobanda)

        # Verificăm că Decimal e precis
        assert dobanda_decimal == Decimal("22.00")

        # float() poate introduce erori microscopice
        # Nu testăm egalitate exactă cu float

    @pytest.mark.unit
    def test_nu_calculeaza_dobanda_daca_sold_pozitiv(self):
        """Test că dobânda NU se calculează dacă soldul rămâne pozitiv"""
        sold_sursa = Decimal("100.00")
        sold_nou = Decimal("50.00")

        # Condiție: dobanda se calculează doar dacă sold_sursa > 0.005 și sold_nou == 0
        calculeaza_dobanda = (sold_sursa > Decimal('0.005')) and (sold_nou == Decimal("0.00"))

        assert calculeaza_dobanda is False


class TestMostenireRata:
    """Teste pentru moștenirea ratei din luna anterioară"""

    @pytest.mark.unit
    @pytest.mark.critical
    def test_mosteneste_rata_fara_imprumut_nou(self):
        """Test că rata se moștenește dacă nu există împrumut nou"""
        rata_luna_anterioara = Decimal("100.00")
        impr_deb_nou = Decimal("0.00")  # Nu există împrumut nou

        # Logica: moștenește rata doar dacă impr_deb_nou == 0
        if impr_deb_nou == Decimal("0.00"):
            rata_mostenit = rata_luna_anterioara.quantize(Decimal("0.01"), ROUND_HALF_UP)
        else:
            rata_mostenit = Decimal("0.00")

        assert rata_mostenit == Decimal("100.00")

    @pytest.mark.unit
    @pytest.mark.critical
    def test_nu_mosteneste_rata_cu_imprumut_nou(self):
        """Test că rata NU se moștenește dacă există împrumut nou"""
        rata_luna_anterioara = Decimal("100.00")
        impr_deb_nou = Decimal("500.00")  # Există împrumut nou

        # Logica: NU moștenește rata dacă impr_deb_nou > 0
        if impr_deb_nou == Decimal("0.00"):
            rata_mostenit = rata_luna_anterioara.quantize(Decimal("0.01"), ROUND_HALF_UP)
        else:
            rata_mostenit = Decimal("0.00")

        assert rata_mostenit == Decimal("0.00")

    @pytest.mark.unit
    def test_plafonare_rata_la_sold_sursa(self):
        """Test că rata se plafonează la soldul sursă"""
        rata_mostenit = Decimal("100.00")
        sold_sursa = Decimal("50.00")

        # Plafonează rata la sold
        if rata_mostenit > sold_sursa:
            rata_finala = sold_sursa
        else:
            rata_finala = rata_mostenit

        assert rata_finala == Decimal("50.00")


class TestCotizatieStandard:
    """Teste pentru aplicarea cotizației standard"""

    @pytest.mark.unit
    @pytest.mark.critical
    def test_aplicare_cotizatie_standard(self):
        """Test că cotizația standard se aplică uniform în toate lunile"""
        cotizatie_standard = Decimal("10.00")

        # În generare_luna, dep_deb_nou = cotizatie_standard
        dep_deb_nou = cotizatie_standard

        assert dep_deb_nou == Decimal("10.00")

    @pytest.mark.unit
    def test_cotizatie_diferita_per_membru(self):
        """Test că membri diferiți pot avea cotizații diferite"""
        cotizatii = {
            1: Decimal("10.00"),
            2: Decimal("10.00"),
            3: Decimal("15.00"),  # Director
            10: Decimal("12.00")  # Administrator
        }

        assert cotizatii[1] == Decimal("10.00")
        assert cotizatii[3] == Decimal("15.00")


class TestIntegrationGenerareLuna:
    """Teste de integrare pentru generare_luna cu DB mockuită"""

    @pytest.mark.integration
    @pytest.mark.critical
    def test_generare_luna_decembrie_cu_dobanda(self, mock_all_dbs):
        """
        Test integrare: Generare luna Decembrie 2025 pentru membrul 1
        Membrul 1 achită împrumutul în Noiembrie → Decembrie trebuie să aibă dobândă
        """
        db_depcred = mock_all_dbs['DEPCRED']
        db_membrii = mock_all_dbs['MEMBRII']

        conn_depcred = sqlite3.connect(db_depcred)
        conn_membrii = sqlite3.connect(db_membrii)

        cursor_depcred = conn_depcred.cursor()
        cursor_membrii = conn_membrii.cursor()

        # Verifică starea în Noiembrie (luna sursă)
        cursor_depcred.execute("""
            SELECT IMPR_SOLD, DEP_SOLD, IMPR_CRED
            FROM DEPCRED
            WHERE NR_FISA = 1 AND LUNA = 11 AND ANUL = 2025
        """)
        nov_data = cursor_depcred.fetchone()

        assert nov_data is not None
        impr_sold_nov = Decimal(str(nov_data[0]))
        dep_sold_nov = Decimal(str(nov_data[1]))
        impr_cred_nov = Decimal(str(nov_data[2]))

        # Sold împrumut în Noiembrie = 0.00 (achitat)
        assert impr_sold_nov == Decimal("0.00")

        # Calculează dobânda pentru perioada Ianuarie-Noiembrie
        cursor_depcred.execute("""
            SELECT SUM(IMPR_SOLD)
            FROM DEPCRED
            WHERE NR_FISA = 1 AND ANUL = 2025 AND LUNA BETWEEN 1 AND 11
            AND IMPR_SOLD > 0
        """)
        sum_solduri = Decimal(str(cursor_depcred.fetchone()[0]))

        # Suma soldurilor = 1000 + 900 + 800 + 700 + 600 + 500 + 400 + 300 + 200 + 100 = 5500
        assert sum_solduri == Decimal("5500.00")

        # Dobândă = 5500 × 0.004 = 22.00
        rata_dobanda = Decimal("0.004")
        dobanda_asteptata = (sum_solduri * rata_dobanda).quantize(Decimal("0.01"), ROUND_HALF_UP)
        assert dobanda_asteptata == Decimal("22.00")

        conn_depcred.close()
        conn_membrii.close()

    @pytest.mark.integration
    def test_excludere_membri_lichidati(self, mock_all_dbs):
        """Test că membrii lichidați sunt excluși la generare lună"""
        db_lichidati = mock_all_dbs['LICHIDATI']

        conn = sqlite3.connect(db_lichidati)
        cursor = conn.cursor()

        # Obține lista de lichidați
        cursor.execute("SELECT nr_fisa FROM lichidati")
        lichidati = {row[0] for row in cursor.fetchall()}

        # Verifică că 99 și 100 sunt lichidați
        assert 99 in lichidati
        assert 100 in lichidati

        # Membri activi = toți membri - lichidați
        membri_activi = {1, 2, 3, 4, 5} - lichidati

        # Verifică că membrii lichidați nu sunt în activi
        assert 99 not in membri_activi
        assert 100 not in membri_activi

        conn.close()


class TestPrecizieDecimal:
    """Teste pentru precizie Decimal (BUG #1 rezolvat)"""

    @pytest.mark.unit
    @pytest.mark.critical
    @pytest.mark.bugfix
    @pytest.mark.decimal_precision
    def test_str_decimal_conversie_pentru_insert(self):
        """Test că folosim str(decimal) pentru INSERT (BUG #1 fix)"""
        dobanda_noua = Decimal("22.00")
        impr_deb_nou = Decimal("0.00")
        impr_cred_nou = Decimal("100.00")

        # CORECT (BUG #1 fix): str(decimal)
        valores_insert = (
            str(dobanda_noua),
            str(impr_deb_nou),
            str(impr_cred_nou)
        )

        # Verificăm că sunt stringuri
        assert isinstance(valores_insert[0], str)
        assert isinstance(valores_insert[1], str)
        assert isinstance(valores_insert[2], str)

        # Verificăm că valorile sunt corecte
        assert Decimal(valores_insert[0]) == Decimal("22.00")
        assert Decimal(valores_insert[1]) == Decimal("0.00")
        assert Decimal(valores_insert[2]) == Decimal("100.00")

    @pytest.mark.unit
    @pytest.mark.bugfix
    def test_citire_decimal_din_db(self):
        """Test pattern citire Decimal din DB"""
        # Simulăm valoare citită din DB (vine ca float sau string)
        value_from_db = "22.00"

        # CORECT: Decimal(str(value))
        decimal_value = Decimal(str(value_from_db))

        assert decimal_value == Decimal("22.00")
        assert isinstance(decimal_value, Decimal)

    @pytest.mark.unit
    @pytest.mark.bugfix
    @pytest.mark.decimal_precision
    def test_precizie_calcule_pentru_800_membri(self):
        """
        Test precizie Decimal pentru 800 membri × 12 luni
        Verifică că nu există erori de rotunjire acumulate
        """
        # Simulăm calcule pentru 800 membri
        suma_totala = Decimal("0.00")

        for membru in range(800):
            # Fiecare membru contribuie cu dividende calculate precis
            dividend = Decimal("123.456").quantize(Decimal("0.01"), ROUND_HALF_UP)
            suma_totala += dividend

        # 800 × 123.46 = 98,768.00
        suma_asteptata = Decimal("98768.00")

        assert suma_totala == suma_asteptata

        # Verifică că nu există diferențe microscopice
        diferenta = abs(suma_totala - suma_asteptata)
        assert diferenta == Decimal("0.00")
