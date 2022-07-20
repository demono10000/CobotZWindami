import RPi.GPIO as GPIO

pin = 12

GPIO.setup(pin, GPIO.OUT)  # elektrozamki


# True - wlacz
def przelaczElektromagnesy(stan):
    if stan:
        GPIO.output(pin, GPIO.LOW)
    else:
        GPIO.output(pin, GPIO.HIGH)


przelaczElektromagnesy(False)
