import elementyGlobalne
import mqtt
import random
import time


def test_odbiorDanych():
    mqtt.inicjalizacja()
    time.sleep(0.001)
    # losowa liczba
    rand = random.randint(0, 100)
    elementyGlobalne.client.publish("cobot/wiadomosc", f"wiadmosc testowa {rand}")
    time.sleep(0.1)
    assert elementyGlobalne.msgmqtt == f"wiadmosc testowa {rand}"
