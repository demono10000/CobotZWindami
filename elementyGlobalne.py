import paho.mqtt.client as paho

piny = {'kraniecSilnik1Gora': 13,
        'kraniecSilnik1dol': 16,
        'kraniecSilnik2Gora': 26,
        'kraniecSilnik2dol': 21,
        'wykrytoKolizje': 18}
pomin = [0, 10, 87, 77, 38, 49]
wybranaSoczewka = None
soczewka = -1
ostatniaSoczewka = -1
maszynaPusta = True
client = paho.Client("client-001")
msgmqtt = ''
trwaWyjmowanie = False
czasStart = 0
