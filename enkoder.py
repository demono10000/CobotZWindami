import RPi.GPIO as GPIO


class Enkoder:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(pin, GPIO.IN, GPIO.PUD_UP)
        self.ostatniStan = self.stan()

    def stan(self):
        return GPIO.input(self.pin)
