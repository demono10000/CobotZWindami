#! /usr/bin/env python
import RPi.GPIO as GPIO
import time
import sqlite3
import elementyGlobalne
import gui


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(elementyGlobalne.piny['kraniecSilnik1Gora'], GPIO.IN, GPIO.PUD_UP)  # kraniecSilnik1Gora
GPIO.setup(elementyGlobalne.piny['kraniecSilnik1dol'], GPIO.IN, GPIO.PUD_UP)  # kraniecSilnik1dol
GPIO.setup(elementyGlobalne.piny['kraniecSilnik2Gora'], GPIO.IN, GPIO.PUD_UP)  # kraniecSilnik2Gora
GPIO.setup(elementyGlobalne.piny['kraniecSilnik2dol'], GPIO.IN, GPIO.PUD_UP)  # kraniecSilnik2dol
GPIO.setup(elementyGlobalne.piny['wykrytoKolizje'], GPIO.IN, GPIO.PUD_UP)  # wykryto kolizje

conn = sqlite3.connect('data.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS dane(nazwa text UNIQUE, wartosc integer)")
c.execute("INSERT OR IGNORE INTO dane(nazwa, wartosc) VALUES ('tackiNowe', 0)")
c.execute("INSERT OR IGNORE INTO dane(nazwa, wartosc) VALUES ('tackiZrobione', 0)")
conn.commit()
conn.close()

# broker="127.0.0.1"
broker = "192.168.188.149"

czasstart = 0


def on_message(client, userdata, message):
    elementyGlobalne.msgmqtt = str(message.payload.decode("utf-8"))
    print('mqtt', elementyGlobalne.msgmqtt)
    if "szerokosc przed" in elementyGlobalne.msgmqtt:
        dane = float(elementyGlobalne.msgmqtt.split(':')[1][:4])
        gui.guiGlowne.labelSzerokoscPrzed['text'] = 'Szerokość przed:\n{}mm'.format(
            str(dane))
        gui.guiGlowne.szerokoscPrzedSuma += dane
        gui.guiGlowne.szerokoscPrzedIlosc += 1
        if dane > gui.guiGlowne.szerokoscPrzedMax:
            gui.guiGlowne.szerokoscPrzedMax = dane
            gui.guiGlowne.labelSzerokoscPrzedMax['text'] = 'Przed max: {}mm'.format(
                str(dane))
        if dane < gui.guiGlowne.szerokoscPrzedMin:
            gui.guiGlowne.szerokoscPrzedMin = dane
            gui.guiGlowne.labelSzerokoscPrzedMin['text'] = 'Przed min: {}mm'.format(
                str(dane))
        gui.guiGlowne.labelSzerokoscPrzedSrednia[
            'text'] = 'Przed średnia: {:.2f}mm'.format(
                gui.guiGlowne.szerokoscPrzedSuma /
                gui.guiGlowne.szerokoscPrzedIlosc)
    if "szerokosc po" in elementyGlobalne.msgmqtt:
        dane = float(elementyGlobalne.msgmqtt.split(':')[1][:4])
        gui.guiGlowne.labelSzerokoscPo['text'] = 'Szerokość po:\n{}mm'.format(
            str(dane))
        if dane > gui.guiGlowne.szerokoscPoMax:
            gui.guiGlowne.szerokoscPoMax = dane
            gui.guiGlowne.labelSzerokoscPoMax['text'] = 'Po max: {}mm'.format(
                str(dane))
        if dane < gui.guiGlowne.szerokoscPoMin:
            gui.guiGlowne.szerokoscPoMin = dane
            gui.guiGlowne.labelSzerokoscPoMin['text'] = 'Po min: {}mm'.format(
                str(dane))

    global czasstart
    if elementyGlobalne.msgmqtt == 'czas start':
        if czasstart > 0:
            elementyGlobalne.gui.labelCzasStartStart['text'] = "Czas cyklu:\n{}s".format(
                int(time.time() - czasstart))
        czasstart = time.time()
    if elementyGlobalne.msgmqtt == 'koniec obrobki soczewki':
        elementyGlobalne.gui.labelCzasStartStop['text'] = "Czas maszyny:\n{}s".format(
            int(time.time() - czasstart))


elementyGlobalne.client.on_message = on_message

elementyGlobalne.client.connect(broker)
elementyGlobalne.client.loop_start()
elementyGlobalne.client.subscribe("cobot/wiadomosc")

gui.guiGlowne.mainloop()
