import time
import cobot
import threading
from silnik import silnik1, silnik2
import RPi.GPIO as GPIO


def glownyWatek():
    global soczewka, maszynaPusta, msgmqtt, ostatniaSoczewka, client, trwaWyjmowanie
    while True:
        if soczewka == 88:
            client.publish("cobot/polecenia", "czekaj na maszyne")
            while not msgmqtt == 'koniec obrobki soczewki':
                time.sleep(0.1)
            cobot.wyjmijSoczewkeZMaszyny()
            cobot.nastepnaSoczewka()
            continue
        if soczewka > 88:
            while trwaWyjmowanie:
                time.sleep(0.1)
            cobot.schowajZrobionaTacke()
            if not cobot.wezNowaTacke():
                break
            time.sleep(3)
            soczewka = 0
            cobot.nastepnaSoczewka()
        if soczewka == -1:
            if not cobot.wezNowaTacke():
                break
            time.sleep(3)
            soczewka = 0
            cobot.nastepnaSoczewka()
        cobot.wezSoczewke()
        czyMaszynaPusta()
        ostatniaSoczewka = soczewka
        cobot.nastepnaSoczewka()
    # lblsoczewka['text'] = 'BŁĄD! Brak tacek'


def czyMaszynaPusta():
    if maszynaPusta:
        cobot.wlozSoczewkeZeSlupka()
    else:
        client.publish("cobot/polecenia", "czekaj na maszyne")
        while not msgmqtt == 'koniec obrobki soczewki':
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
                        # silnikk.przelacz(False)
                        # silnikk.przelaczKierunek(False)
                        pass
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
