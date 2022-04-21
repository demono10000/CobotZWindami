import sqlite3
from contextlib import contextmanager

bazadanych = 'data.db'


@contextmanager
def db_ops():
    conn = sqlite3.connect(bazadanych)
    c = conn.cursor()
    yield c
    conn.commit()
    conn.close()


def odczytajDane(nazwa):
    with db_ops() as c:
        c.execute("SELECT wartosc FROM dane WHERE nazwa = ?", (nazwa,))
        return c.fetchone()[0]


def dodajDo(nazwa, wartosc):
    with db_ops() as c:
        c.execute("UPDATE dane SET wartosc = wartosc + ? WHERE nazwa = ?", (wartosc, nazwa))


def zeruj(nazwa):
    with db_ops() as c:
        c.execute("UPDATE dane SET wartosc = 0 WHERE nazwa = ?", (nazwa,))


def stworzBaze():
    with db_ops() as c:
        c.execute("CREATE TABLE IF NOT EXISTS dane(nazwa text UNIQUE, wartosc integer)")
        c.execute("INSERT OR IGNORE INTO dane(nazwa, wartosc) VALUES ('tackiNowe', 0)")
        c.execute("INSERT OR IGNORE INTO dane(nazwa, wartosc) VALUES ('tackiZrobione', 0)")
