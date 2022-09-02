import time
import elektromagnes
import elementyGlobalne
import gui
import silnik
import database


def wyjmijSoczewkeZMaszyny():
    elementyGlobalne.client.publish(
        "cobot/polecenia", "wyjmij z maszyny:" + str(elementyGlobalne.ostatniaSoczewka))
    while not elementyGlobalne.msgmqtt == 'soczewka wyjeta':
        time.sleep(0.1)
    elementyGlobalne.maszynaPusta = True
    gui.guiGlowne.zrobioneSoczewki += 1
    gui.guiGlowne.labelZrobioneSoczewki['text'] = "Zrobione soczewki:\n" + str(
        gui.guiGlowne.zrobioneSoczewki)


def nastepnaSoczewka():
    elementyGlobalne.soczewka += 1
    while elementyGlobalne.soczewka in elementyGlobalne.pomin:
        elementyGlobalne.soczewka += 1
    gui.guiGlowne.labelSoczewka['text'] = "Numer soczewki: " + str(elementyGlobalne.soczewka)


def poprzedniaSoczewka(numer):
    numer -= 1
    while numer in elementyGlobalne.pomin and numer >= 0:
        numer -= 1
    if numer < 0:
        exit()
    return numer


def schowajZrobionaTacke():
    silnik.silnik2.jedzDoGoryDoCzujnikaIR()
    while silnik.silnik2.stan():
        time.sleep(0.1)
    elektromagnes.przelaczElektromagnesy(True)
    time.sleep(1)
    silnik.silnik2.jedzDoDolu()
    time.sleep(3)
    silnik.silnik2.stop()
    elektromagnes.przelaczElektromagnesy(False)
    gui.guiGlowne.zmienZrobioneTacki(1)


def wezSoczewke():
    gui.guiGlowne.labelSoczewka['text'] = "Numer soczewki: " + str(
        elementyGlobalne.soczewka)
    elementyGlobalne.client.publish("cobot/polecenia", "wez soczewke:" + str(
        elementyGlobalne.soczewka))
    while (not elementyGlobalne.msgmqtt == 'nie wykryto soczewki') and (
            not elementyGlobalne.msgmqtt == 'soczewka zabrana'):
        time.sleep(0.1)
    if elementyGlobalne.msgmqtt == 'nie wykryto soczewki':
        elementyGlobalne.msgmqtt = ''
        nastepnaSoczewka()
        if elementyGlobalne.soczewka < 87:
            wezSoczewke()
        return
    elementyGlobalne.msgmqtt = ''


def wlozSoczewkeZeSlupka():
    elementyGlobalne.client.publish("cobot/polecenia", "zabierz ze slupka")
    while not elementyGlobalne.msgmqtt == 'soczewka wlozona':
        time.sleep(0.1)
    elementyGlobalne.maszynaPusta = False


def wlozSoczewke():
    elementyGlobalne.client.publish(
        "cobot/polecenia",
        "wloz do maszyny:" + str(elementyGlobalne.ostatniaSoczewka)
    )
    while not elementyGlobalne.msgmqtt == 'soczewka wyjeta':
        time.sleep(0.1)
    gui.guiGlowne.zrobioneSoczewki += 1
    gui.guiGlowne.labelZrobioneSoczewki['text'] = "Zrobione soczewki:\n" + str(
        gui.guiGlowne.zrobioneSoczewki)


def wezNowaTacke():
    tackiNowe = database.odczytajDane('tackiNowe')
    if tackiNowe < 1:
        return False
    if silnik.silnik1.stanIR():
        print("Wykryto niezaladowana tacke")
        return False
    silnik.silnik1.jedzDoGoryDoCzujnikaIR()
    while silnik.silnik1.stan():
        time.sleep(0.1)
    if silnik.silnik1.stanKraniecGora():
        return False
    gui.guiGlowne.zmienNoweTacki(-1)
    elementyGlobalne.client.publish("cobot/polecenia", "tacka podana")
    # cobot teraz bierze tacke i kładzie ją na elektromagnesach
    while not elementyGlobalne.msgmqtt == 'tacka oddana':
        time.sleep(0.1)
    elementyGlobalne.msgmqtt = ''
    if silnik.silnik1.stanIR():
        print("Tacka nie zostala zabrana")
        return False
    print('stan przed', silnik.silnik2.stanIR())
    silnik.silnik2.jedzDoGoryDoCzujnikaIR()
    while silnik.silnik2.stan():
        time.sleep(0.1)
    print('stan po', silnik.silnik2.stanIR())
    silnik.silnik2.jedzDoDolu()
    time.sleep(0.5)
    silnik.silnik2.stop()
    return True
