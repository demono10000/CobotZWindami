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
    print('db_ops closed')


def odczytajDane(nazwa):
    with db_ops() as c:
        c.execute("SELECT wartosc FROM dane WHERE nazwa = ?", (nazwa,))
        return c.fetchone()


def dodajDo(nazwa, wartosc):
    with db_ops() as c:
        c.execute("UPDATE dane SET wartosc = wartosc + ? WHERE nazwa = ?", (wartosc, nazwa))


def zeruj(nazwa):
    with db_ops() as c:
        c.execute("UPDATE dane SET wartosc = 0 WHERE nazwa = ?", (nazwa,))
