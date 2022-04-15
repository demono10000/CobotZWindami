#! /usr/bin/env python
import RPi.GPIO as GPIO

class Silnik:
    pozycjaDocelowa = -1
    przesun = False
    def __init__(self, pinStan, pinKierunek, kraniecGora, kraniecDol):
        self.pinStan = pinStan
        self.pinKierunek = pinKierunek
        self.kraniecGora = kraniecGora
        self.kraniecDol = kraniecDol
        self.przelacz(False)
        self.przelaczKierunek(False)
        #self.laser = laser
    #True - wlacz 
    def przelacz(self, stan):
        if stan:
            GPIO.output(self.pinStan, GPIO.LOW)
            #self.laser.przelacz(True)
        else:
            GPIO.output(self.pinStan, GPIO.HIGH)
            #self.laser.przelacz(False)
    #True - wlaczony
    def stan(self):
        return not GPIO.input(self.pinStan)
    #True - do dolu
    def przelaczKierunek(self, stan):
        if stan:
            GPIO.output(self.pinKierunek, GPIO.LOW)
        else:
            GPIO.output(self.pinKierunek, GPIO.HIGH)
    #True - do dolu
    def stanKierunku(self):
        return not GPIO.input(self.pinKierunek)
    #True - wcisniety
    def stanKraniecGora(self):
        return GPIO.input(self.kraniecGora)
    #True - wcisniety
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
            
    def stop(self):
        self.przelacz(False)
