import time
import cobot
import threading
from silnik import silnik1, silnik2
import RPi.GPIO as GPIO
import elementyGlobalne
import gui
import pad
from gpiozero import DigitalInputDevice


def glownyWatek():
    while True:
        if elementyGlobalne.soczewka == 88:
            elementyGlobalne.client.publish("cobot/polecenia", "czekaj na maszyne")
            while not elementyGlobalne.msgmqtt == 'koniec obrobki soczewki':
                time.sleep(0.1)
            cobot.wyjmijSoczewkeZMaszyny()
            cobot.nastepnaSoczewka()
            continue
        if elementyGlobalne.soczewka > 88:
            while elementyGlobalne.trwaWyjmowanie:
                time.sleep(0.1)
            cobot.schowajZrobionaTacke()
            if not cobot.wezNowaTacke():
                break
            time.sleep(3)
            elementyGlobalne.soczewka = 0
            cobot.nastepnaSoczewka()
        if elementyGlobalne.soczewka == -1:
            if not cobot.wezNowaTacke():
                break
            time.sleep(3)
            elementyGlobalne.soczewka = 0
            cobot.nastepnaSoczewka()
        cobot.wezSoczewke()
        czyMaszynaPusta()
        elementyGlobalne.ostatniaSoczewka = elementyGlobalne.soczewka
        cobot.nastepnaSoczewka()
    gui.guiGlowne.labelSoczewka['text'] = 'BŁĄD! Brak tacek'


def czyMaszynaPusta():
    if elementyGlobalne.maszynaPusta:
        cobot.wlozSoczewkeZeSlupka()
    else:
        elementyGlobalne.client.publish("cobot/polecenia", "czekaj na maszyne")
        while not elementyGlobalne.msgmqtt == 'koniec obrobki soczewki':
            time.sleep(0.1)
        time.sleep(2)
        cobot.wyjmijSoczewkeZMaszyny()
        cobot.wlozSoczewkeZeSlupka()


# True - kolizja
def kolizjaWykryta():
    return not GPIO.input(18)


def kontrolaSilnikow():
    while True:
        silniki = [silnik1, silnik2]
        for silnikk in silniki:
            if silnikk.stan():
                if silnikk.stanKierunku():
                    if silnikk.stanKraniecDol() and silnikk.kraniecDolWczesniej:
                        silnikk.przelacz(False)
                        silnikk.przelaczKierunek(False)
                        # print("kraniec dol")
                    silnikk.kraniecDolWczesniej = silnikk.stanKraniecDol()
                else:
                    if silnikk.stanKraniecGora() and silnikk.kraniecGoraWczesniej:
                        silnikk.przelacz(False)
                        silnikk.przelaczKierunek(True)
                        # print("kraniec gora")
                    silnikk.kraniecGoraWczesniej = silnikk.stanKraniecGora()
        time.sleep(0.005)


tsilniki = threading.Thread(target=kontrolaSilnikow)
tsilniki.daemon = True
tsilniki.start()


pozycjaDocelowa = 0
zatrzymaj = False
ostatniWysokiSygnal = time.time()


def enkoderSilnik1(channel):
    global zatrzymaj, pozycjaDocelowa, ostatniWysokiSygnal
    if time.time() - ostatniWysokiSygnal < 0.0023:
        return
    if silnik1.stanKierunku():
        silnik1.pozycja += 1
        if silnik1.pozycja >= pozycjaDocelowa and zatrzymaj:
            silnik1.stop()
            zatrzymaj = False
    else:
        silnik1.pozycja -= 1
        if silnik1.pozycja <= pozycjaDocelowa and zatrzymaj:
            silnik1.stop()
            zatrzymaj = False


def enkoderSilnik2(channel):
    global zatrzymaj, pozycjaDocelowa, ostatniWysokiSygnal
    if time.time() - ostatniWysokiSygnal < 0.0023:
        return
    if silnik2.stanKierunku():
        silnik2.pozycja += 1
        if silnik2.pozycja >= pozycjaDocelowa and zatrzymaj:
            silnik2.stop()
            zatrzymaj = False
    else:
        silnik2.pozycja -= 1
        if silnik2.pozycja <= pozycjaDocelowa and zatrzymaj:
            silnik2.stop()
            zatrzymaj = False


def filtrSygnalu():
    global ostatniWysokiSygnal
    ostatniWysokiSygnal = time.time()


sensor1 = DigitalInputDevice(20, pull_up=True)
sensor1.when_activated = enkoderSilnik1
sensor1.when_deactivated = filtrSygnalu

sensor2 = DigitalInputDevice(23, pull_up=True)
sensor2.when_activated = enkoderSilnik2
sensor2.when_deactivated = filtrSygnalu


def silnik1DoDolu(dystans):
    global pozycjaDocelowa, zatrzymaj
    dystans *= 2.0
    pozycjaDocelowa = silnik1.pozycja + dystans
    zatrzymaj = True
    silnik1.jedzDoDolu()


def silnik1DoGory(dystans):
    global pozycjaDocelowa, zatrzymaj
    dystans *= 2.4
    pozycjaDocelowa = silnik1.pozycja - dystans
    zatrzymaj = True
    silnik1.jedzDoGory()


def silnik2DoDolu(dystans):
    dystans *= 3.5
    global pozycjaDocelowa, zatrzymaj
    pozycjaDocelowa = silnik2.pozycja + dystans
    zatrzymaj = True
    silnik2.jedzDoDolu()


def silnik2DoGory(dystans):
    dystans *= 3.9
    global pozycjaDocelowa, zatrzymaj
    pozycjaDocelowa = silnik2.pozycja - dystans
    zatrzymaj = True
    silnik2.jedzDoGory()


def czujnikTackiNowe():
    silnik1.stop()


def czujnikTackiZrobione():
    silnik2.stop()


# ir1 = DigitalInputDevice(24, pull_up=True)
# ir1.when_activated = czujnikTackiNowe

# ir2 = DigitalInputDevice(25, pull_up=True)
# ir2.when_activated = czujnikTackiZrobione

watekglowny = threading.Thread(target=glownyWatek)
watekglowny.daemon = True

tpad = threading.Thread(target=pad.padController)
tpad.daemon = True
tpad.start()
