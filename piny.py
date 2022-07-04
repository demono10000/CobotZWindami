import RPi.GPIO as GPIO
import elementyGlobalne


def ustawPiny():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(elementyGlobalne.piny['kraniecSilnik1Gora'], GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(elementyGlobalne.piny['kraniecSilnik1dol'], GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(elementyGlobalne.piny['kraniecSilnik2Gora'], GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(elementyGlobalne.piny['kraniecSilnik2dol'], GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(elementyGlobalne.piny['wykrytoKolizje'], GPIO.IN, GPIO.PUD_UP)


ustawPiny()
