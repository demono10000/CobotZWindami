import time
import cobot
import threading
from silnik import silnik1, silnik2
import RPi.GPIO as GPIO
import elementyGlobalne
import gui
import pad


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
                    if silnikk.stanKraniecDol():
                        silnikk.przelacz(False)
                        silnikk.przelaczKierunek(False)
                else:
                    if silnikk.stanKraniecGora():
                        silnikk.przelacz(False)
                        silnikk.przelaczKierunek(True)
                    elif kolizjaWykryta():
                        silnikk.przelacz(False)
                        silnikk.przelaczKierunek(True)
        time.sleep(0.01)


tsilniki = threading.Thread(target=kontrolaSilnikow)
tsilniki.daemon = True
tsilniki.start()

watekglowny = threading.Thread(target=glownyWatek)
watekglowny.daemon = True

tpad = threading.Thread(target=pad.padController)
tpad.daemon = True
tpad.start()
