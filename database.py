import sqlite3

bazadanych = 'data.db'


def odczytajDane(nazwa):
    odpowiedz = ''
    conn = sqlite3.connect(bazadanych)
    c = conn.cursor()
    for row in c.execute("SELECT wartosc FROM dane WHERE nazwa=?", (nazwa,)):
        odpowiedz = str(row[0])
    conn.commit()
    conn.close()
    return odpowiedz


def dodajDo(nazwa, wartosc):
    conn = sqlite3.connect(bazadanych)
    c = conn.cursor()
    c.execute("UPDATE dane SET wartosc = wartosc + ? WHERE nazwa = ?", (wartosc, nazwa))
    conn.commit()
    conn.close()


def zeruj(nazwa):
    conn = sqlite3.connect(bazadanych)
    c = conn.cursor()
    c.execute("UPDATE dane SET wartosc = 0 WHERE nazwa = ?", (nazwa,))
    conn.commit()
    conn.close()
