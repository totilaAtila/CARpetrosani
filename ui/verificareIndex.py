import sqlite3

def listeaza_indexuri(nume_baza):
    try:
        conn = sqlite3.connect(nume_baza)
        cursor = conn.cursor()
        cursor.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index'")
        indexuri = cursor.fetchall()
        print(f"Indexuri în {nume_baza}:")
        for idx in indexuri:
            print(f" - {idx[0]} (tabel: {idx[1]}) -> {idx[2]}")
        if not indexuri:
            print("  (niciun index definit)")
    except Exception as e:
        print(f"Eroare la {nume_baza}: {e}")
    finally:
        conn.close()

# Rulăm pentru fiecare bază
for baza in ["MEMBRII.db", "DEPCRED.db", "CHITANTE.db"]:
    listeaza_indexuri(baza)
