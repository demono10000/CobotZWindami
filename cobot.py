import time
import sqlite3
import elektromagnes
import elementyGlobalne
import gui
import silnik


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
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    zrobioneTacki = 0
    for row in c.execute("SELECT wartosc FROM dane WHERE nazwa='tackiZrobione'"):
        zrobioneTacki = int(row[0])
    conn.commit()
    conn.close()
    if zrobioneTacki == 0:
        elementyGlobalne.client.publish("cobot/polecenia", "jedz nad zrobione")
        while not elementyGlobalne.msgmqtt == 'jestem na miejscu':
            time.sleep(0.1)
        silnik.silnik2.jedzDoGory()
        while silnik.silnik2.stan():
            time.sleep(0.1)
    else:
        silnik.silnik2.jedzDoGory()
        time.sleep(1.75)
        silnik.silnik2.stop()
    elektromagnes.przelaczElektromagnesy(True)
    silnik.silnik2.jedzDoDolu()
    time.sleep(8)
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
    while not elementyGlobalne.msgmqtt == 'soczewka odlozona':
        time.sleep(0.1)
    elementyGlobalne.msgmqtt = ''


def wlozSoczewkeZeSlupka():
    elementyGlobalne.client.publish("cobot/polecenia", "zabierz ze slupka")
    while not elementyGlobalne.msgmqtt == 'soczewka wlozona':
        time.sleep(0.1)
    elementyGlobalne.maszynaPusta = False


def wezNowaTacke():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    tackiNowe = 0
    for row in c.execute("SELECT wartosc FROM dane WHERE nazwa='tackiNowe'"):
        tackiNowe = int(row[0])
    conn.commit()
    conn.close()
    if tackiNowe < 1:
        return False
    elementyGlobalne.client.publish("cobot/polecenia", "wez nowa tacke")
    while not elementyGlobalne.msgmqtt == 'podaj tacke':
        time.sleep(0.1)
    silnik.silnik1.jedzDoGory()
    while silnik.silnik1.stan():
        time.sleep(0.1)
    if silnik.silnik1.stanKraniecGora():
        return False
    gui.guiGlowne.zmienNoweTacki(-1)
    elementyGlobalne.client.publish("cobot/polecenia", "tacka podana")
    while not elementyGlobalne.msgmqtt == 'podnies tacki':
        time.sleep(0.1)
    silnik.silnik2.jedzDoGory()
    while silnik.silnik2.stan():
        time.sleep(0.1)
    elementyGlobalne.client.publish("cobot/polecenia", "tacki podniesione")
    while not elementyGlobalne.msgmqtt == 'tacka oddana':
        time.sleep(0.1)
    silnik.silnik2.jedzDoDolu()
    time.sleep(1)
    silnik.silnik2.stop()
    return True
