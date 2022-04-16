import time
import sqlite3
import elektromagnes
import elementyGlobalne


def wyjmijSoczewkeZMaszyny():
    client.publish("cobot/polecenia", "wyjmij z maszyny:" + str(elementyGlobalne.ostatniaSoczewka))
    while not msgmqtt == 'soczewka wyjeta':
        time.sleep(0.1)
    elementyGlobalne.maszynaPusta = True
    global lblzrobsocz, zrobioneSocz
    zrobioneSocz += 1
    lblzrobsocz['text'] = "Zrobione soczewki:\n" + str(zrobioneSocz)


def nastepnaSoczewka():
    global soczewka, pomin, lblsoczewka
    soczewka += 1
    while soczewka in pomin:
        soczewka += 1
    lblsoczewka['text'] = "Numer soczewki: " + str(soczewka)


def poprzedniaSoczewka(numer):
    numer -= 1
    while numer in pomin and numer >= 0:
        numer -= 1
    if numer < 0:
        exit()
        return
    return numer


def schowajZrobionaTacke():
    global silnik2
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    zrobioneTacki = 0
    for row in c.execute("SELECT wartosc FROM dane WHERE nazwa='tackiZrobione'"):
        zrobioneTacki = int(row[0])
    conn.commit()
    conn.close()
    if zrobioneTacki == 0:
        client.publish("cobot/polecenia", "jedz nad zrobione")
        while not msgmqtt == 'jestem na miejscu':
            time.sleep(0.1)
        silnik2.jedzDoGory()
        while silnik2.stan():
            time.sleep(0.1)
    else:
        silnik2.jedzDoGory()
        time.sleep(1.75)
        silnik2.stop()
    elektromagnes.przelaczElektromagnesy(True)
    silnik2.jedzDoDolu()
    time.sleep(8)
    silnik2.stop()
    elektromagnes.przelaczElektromagnesy(False)
    global guiGlowne
    guiGlowne.zmienZrobioneTacki(1)


def wezSoczewke():
    lblsoczewka['text'] = "Numer soczewki: " + str(soczewka)
    client.publish("cobot/polecenia", "wez soczewke:" + str(soczewka))
    while not msgmqtt == 'nie wykryto soczewki' and not msgmqtt == 'soczewka zabrana':
        time.sleep(0.1)
    if msgmqtt == 'nie wykryto soczewki':
        msgmqtt = ''
        nastepnaSoczewka()
        if soczewka < 87:
            wezSoczewke()
        return
    while not msgmqtt == 'soczewka odlozona':
        time.sleep(0.1)
    msgmqtt = ''


def wlozSoczewkeZeSlupka():
    global msgmqtt, maszynaPusta, soczewka
    client.publish("cobot/polecenia", "zabierz ze slupka")
    while not msgmqtt == 'soczewka wlozona':
        time.sleep(0.1)
    maszynaPusta = False


def wezNowaTacke():
    global silnik1, silnik2
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    tackiNowe = 0
    for row in c.execute("SELECT wartosc FROM dane WHERE nazwa='tackiNowe'"):
        tackiNowe = int(row[0])
    conn.commit()
    conn.close()
    if tackiNowe < 1:
        return False
    global client
    client.publish("cobot/polecenia", "wez nowa tacke")
    while not msgmqtt == 'podaj tacke':
        time.sleep(0.1)
    silnik1.jedzDoGory()
    while silnik1.stan():
        time.sleep(0.1)
    if silnik1.stanKraniecGora():
        return False
    global guiGlowne
    guiGlowne.zmienNoweTacki(-1)
    client.publish("cobot/polecenia", "tacka podana")
    while not msgmqtt == 'podnies tacki':
        time.sleep(0.1)
    silnik2.jedzDoGory()
    while silnik2.stan():
        time.sleep(0.1)
    client.publish("cobot/polecenia", "tacki podniesione")
    while not msgmqtt == 'tacka oddana':
        time.sleep(0.1)
    silnik2.jedzDoDolu()
    time.sleep(1)
    silnik2.stop()
    return True
