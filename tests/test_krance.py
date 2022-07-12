import piny
from silnik import silnik1, silnik2


piny


def test_wszystkieKranceWykryte():
    assert not silnik1.stanKraniecGora()
    assert not silnik1.stanKraniecDol()
    assert not silnik2.stanKraniecGora()
    assert not silnik2.stanKraniecDol()


def test_wciskanieKrancow(capsys):
    with capsys.disabled():
        print("Wcisnij kraniec gorny, tacki do zrobienia")
    while not silnik1.stanKraniecGora():
        pass
    assert True
    with capsys.disabled():
        print("Wcisnij kraniec dolny, tacki do zrobienia")
    while not silnik1.stanKraniecDol():
        pass
    assert True
    with capsys.disabled():
        print("Wcisnij kraniec gorny, tacki zrobione")
    while not silnik2.stanKraniecGora():
        pass
    assert True
    with capsys.disabled():
        print("Wcisnij kraniec dolny, tacki zrobione")
    while not silnik2.stanKraniecDol():
        pass
    assert True
