import database


def test_zapisBazyDanych():
    database.stworzBaze()
    x = database.odczytajDane('tackiNowe')
    database.dodajDo('tackiNowe', 1)
    assert database.odczytajDane('tackiNowe') == x + 1
    database.zeruj('tackiNowe')
    assert database.odczytajDane('tackiNowe') == 0
    database.dodajDo('tackiNowe', -1)
    assert database.odczytajDane('tackiNowe') == -1
