import time
import cobot
import threading
from silnik import silnik1, silnik2
import elementyGlobalne
import gui
import pad
from gpiozero import DigitalInputDevice


def glownyWatek():
    while True:
        '''
        if elementyGlobalne.soczewka == 88:
            elementyGlobalne.client.publish("cobot/polecenia", "czekaj na maszyne")
            while not elementyGlobalne.msgmqtt == 'koniec obrobki soczewki':
                time.sleep(0.1)
            cobot.wyjmijSoczewkeZMaszyny()
            cobot.nastepnaSoczewka()
            continue
        '''
        if elementyGlobalne.soczewka >= 88:
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
        elementyGlobalne.ostatniaSoczewka = elementyGlobalne.soczewka
        # czyMaszynaPusta()
        # input("sygnał do zamiany soczewki")
        cobot.wlozSoczewke()
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


def kontrolaSilnikow():
    while True:
        silniki = [silnik1, silnik2]
        for silnikk in silniki:
            if silnikk.stan():
                if silnikk.stanKierunku():
                    if silnikk.stanKraniecDol() and silnikk.kraniecDolWczesniej:
                        silnikk.przelacz(False)
                        silnikk.przelaczKierunek(False)
                    silnikk.kraniecDolWczesniej = silnikk.stanKraniecDol()
                else:
                    if silnikk.stanKraniecGora() and silnikk.kraniecGoraWczesniej:
                        silnikk.przelacz(False)
                        silnikk.przelaczKierunek(True)
                    silnikk.kraniecGoraWczesniej = silnikk.stanKraniecGora()
        time.sleep(0.005)


tsilniki = threading.Thread(target=kontrolaSilnikow)
tsilniki.daemon = True
tsilniki.start()


pozycjaDocelowa = 0
zatrzymaj = False
ostatniWysokiSygnal = time.time()


def enkoder(channel):
    global zatrzymaj, pozycjaDocelowa, ostatniWysokiSygnal
    silnik = None
    if channel.pin.number == elementyGlobalne.piny['enkoder1']:
        silnik = silnik1
    elif channel.pin.number == elementyGlobalne.piny['enkoder2']:
        silnik = silnik2
    if time.time() - ostatniWysokiSygnal < 0.0023:
        return
    if silnik.stanKierunku():
        silnik.pozycja += 1
        if silnik.pozycja >= pozycjaDocelowa and zatrzymaj:
            silnik.stop()
            zatrzymaj = False
    else:
        silnik.pozycja -= 1
        if silnik.pozycja <= pozycjaDocelowa and zatrzymaj:
            silnik.stop()
            zatrzymaj = False


def filtrSygnalu():
    global ostatniWysokiSygnal
    ostatniWysokiSygnal = time.time()


sensor1 = DigitalInputDevice(elementyGlobalne.piny['enkoder1'], pull_up=True)
sensor1.when_activated = enkoder
sensor1.when_deactivated = filtrSygnalu

sensor2 = DigitalInputDevice(elementyGlobalne.piny['enkoder2'], pull_up=True)
sensor2.when_activated = enkoder
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


watekglowny = threading.Thread(target=glownyWatek)
watekglowny.daemon = True

tpad = threading.Thread(target=pad.padController)
tpad.daemon = True
tpad.start()
