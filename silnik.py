#! /usr/bin/env python
import RPi.GPIO as GPIO
import elementyGlobalne
from gpiozero import DigitalInputDevice


class Silnik:
    przesun = False

    def __init__(self, pinStan, pinKierunek, kraniecGora, kraniecDol, pinIR):
        self.pinStan = pinStan
        self.pinKierunek = pinKierunek
        self.kraniecGora = kraniecGora
        self.kraniecGoraWczesniej = False
        self.kraniecDol = kraniecDol
        self.kraniecDolWczesniej = False
        self.pinIR = pinIR
        self.czujnikIR = DigitalInputDevice(pinIR, pull_up=True)
        self.czujnikIR.when_activated = self.IRwykryty
        self.pozycja = 0
        self.zatrzymajNaIR = False
        GPIO.setup(pinStan, GPIO.OUT)
        GPIO.setup(pinKierunek, GPIO.OUT)
        self.przelacz(False)
        self.przelaczKierunek(False)

    # True - wlacz
    def przelacz(self, stan):
        if stan:
            GPIO.output(self.pinStan, GPIO.LOW)
        else:
            GPIO.output(self.pinStan, GPIO.HIGH)

    # True - wlaczony
    def stan(self):
        return not GPIO.input(self.pinStan)

    # True - wlaczony
    def stanIR(self):
        return self.czujnikIR.is_active

    # True - do dolu
    def przelaczKierunek(self, stan):
        if stan:
            GPIO.output(self.pinKierunek, GPIO.HIGH)
        else:
            GPIO.output(self.pinKierunek, GPIO.LOW)

    # True - do dolu
    def stanKierunku(self):
        return GPIO.input(self.pinKierunek)

    # True - wcisniety
    def stanKraniecGora(self):
        return GPIO.input(self.kraniecGora)

    # True - wcisniety
    def stanKraniecDol(self):
        return GPIO.input(self.kraniecDol)

    def jedzDoDolu(self):
        if not self.stanKraniecDol():
            self.przelaczKierunek(True)
            self.przelacz(True)

    def jedzDoGory(self):
        if not self.stanKraniecGora():
            self.przelaczKierunek(False)
            self.przelacz(True)

    def jedzDoGoryDoCzujnikaIR(self):
        self.jedzDoGory()
        self.zatrzymajNaIR = True

    def stop(self):
        self.przelacz(False)
        # print(self.pozycja)

    def IRwykryty(self):
        if self.zatrzymajNaIR:
            self.stop()
            self.zatrzymajNaIR = False


# do zrobienia tacki
silnik1 = Silnik(
    elementyGlobalne.piny['silnik1stan'],
    elementyGlobalne.piny['silnik1kierunek'],
    elementyGlobalne.piny['kraniecSilnik1Gora'],
    elementyGlobalne.piny['kraniecSilnik1dol'],
    24
)

# zrobione tacki
silnik2 = Silnik(
    elementyGlobalne.piny['silnik2stan'],
    elementyGlobalne.piny['silnik2kierunek'],
    elementyGlobalne.piny['kraniecSilnik2Gora'],
    elementyGlobalne.piny['kraniecSilnik2dol'],
    25
)
