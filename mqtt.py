import elementyGlobalne
import gui
import time

broker = "192.168.188.149"
# broker="127.0.0.1"


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
    if elementyGlobalne.msgmqtt == 'czas start':
        if elementyGlobalne.czasSstart > 0:
            gui.guiGlowne.labelCzasStartStart['text'] = "Czas cyklu:\n{}s".format(
                int(time.time() - elementyGlobalne.czasStart))
        elementyGlobalne.czasStart = time.time()
    if elementyGlobalne.msgmqtt == 'koniec obrobki soczewki':
        gui.guiGlowne.labelCzasStartStop['text'] = "Czas maszyny:\n{}s".format(
            int(time.time() - elementyGlobalne.czasStart))


def on_connect(client, userdata, flags, rc):
    print("MQTT: połączono z kodem zwrotnym: " + str(rc))
    client.subscribe("cobot/wiadomosc")


def inicjalizacja():
    elementyGlobalne.client.on_message = on_message
    elementyGlobalne.client.on_connect = on_connect
    elementyGlobalne.client.connect(broker)
    elementyGlobalne.client.loop_start()
