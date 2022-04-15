#! /usr/bin/env python

import RPi.GPIO as GPIO
import time
from tkinter import *
import threading
from gpiozero import CPUTemperature
import paho.mqtt.client as paho
import requests
import sqlite3
import silnik
import os

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17, GPIO.OUT) #elektrozamki
GPIO.setup(27, GPIO.OUT) #silnik1 on/off
GPIO.setup(22, GPIO.OUT) #silnik1 kierunek
GPIO.setup(5, GPIO.OUT) #silnik2 on/off
GPIO.setup(6, GPIO.OUT) #silnik2 kierunek
#GPIO.setup(23, GPIO.OUT) #laser1
#GPIO.setup(24, GPIO.OUT) #laser2
GPIO.setup(13, GPIO.IN, GPIO.PUD_UP) #kraniecSilnik1Gora
GPIO.setup(16, GPIO.IN, GPIO.PUD_UP) #kraniecSilnik1dol
GPIO.setup(26, GPIO.IN, GPIO.PUD_UP) #kraniecSilnik2Gora
GPIO.setup(21, GPIO.IN, GPIO.PUD_UP) #kraniecSilnik2dol
GPIO.setup(18, GPIO.IN, GPIO.PUD_UP) #wykryto kolizje

conn = sqlite3.connect('data.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS dane(nazwa text UNIQUE, wartosc integer)")
c.execute("INSERT OR IGNORE INTO dane(nazwa, wartosc) VALUES ('tackiNowe', 0)")
c.execute("INSERT OR IGNORE INTO dane(nazwa, wartosc) VALUES ('tackiZrobione', 0)")
conn.commit()
conn.close()

broker="127.0.0.1"
global msgmqtt, tackiNowe, tackiZrobione, maszynaPusta
msgmqtt = ''
tackiNowe, tackiZrobione = 0, 0
maszynaPusta = True

global czasstartstart, szerprzedsuma, szerprzedilosc, szerprzedmin, szerprzedmax, szerpomin, szerpomax
czasstart = 0
szerprzedsuma = 0
szerprzedilosc = 0
szerprzedmin = 100
szerprzedmax = 0
szerpomin = 100
szerpomax = 0
def on_message(client, userdata, message):
    global msgmqtt, lblszerprzed, lblszerpo
    global lblszerprzedmin, lblszerprzedmax, lblszerprzedsrd, lblszerpomin, lblszerpomax
    global szerprzedsuma, szerprzedilosc, szerprzedmin, szerprzedmax, szerpomin, szerpomax
    time.sleep(1)
    msgmqtt = str(message.payload.decode("utf-8"))
    #print('mqtt',msgmqtt)
    if "szerokosc przed" in msgmqtt:
        dane = float(msgmqtt.split(':')[1][:4])
        lblszerprzed['text'] = 'Szerokość przed:\n{}mm'.format(str(dane))
        szerprzedsuma += dane
        szerprzedilosc += 1
        if dane > szerprzedmax:
            szerprzedmax = dane
            lblszerprzedmax['text'] = 'Przed max: {}mm'.format(str(dane))
        if dane < szerprzedmin:
            szerprzedmin = dane
            lblszerprzedmin['text'] = 'Przed min: {}mm'.format(str(dane))
        lblszerprzedsrd['text'] = 'Przed średnia: {:.2f}mm'.format(szerprzedsuma/szerprzedilosc)
    if "szerokosc po" in msgmqtt:
        dane = float(msgmqtt.split(':')[1][:4])
        lblszerpo['text'] = 'Szerokość po:\n{}mm'.format(str(dane))
        if dane > szerpomax:
            szerpomax = dane
            lblszerpomax['text'] = 'Po max: {}mm'.format(str(dane))
        if dane < szerpomin:
            szerpomin = dane
            lblszerpomin['text'] = 'Po min: {}mm'.format(str(dane))
        
    global lblczasstartstart, lblczasstartstop, czasstart
    if msgmqtt == 'czas start':
        if czasstart > 0:
            lblczasstartstart['text'] = "Czas cyklu:\n{}s".format(int(time.time()-czasstart))
        czasstart = time.time()
    if msgmqtt == 'koniec obrobki soczewki':
        lblczasstartstop['text'] = "Czas maszyny:\n{}s".format(int(time.time()-czasstart))

global client
client= paho.Client("client-001")
client.on_message=on_message

client.connect(broker)
client.loop_start()
client.subscribe("cobot/wiadomosc")

#True - wlacz
def przelaczElektromagnesy(stan):
    if stan:
        GPIO.output(17, GPIO.LOW)
    else:
        GPIO.output(17, GPIO.HIGH)
przelaczElektromagnesy(False)
#True - kolizja
def kolizjaWykryta():
    return not GPIO.input(18)

global silnik1, silnik2
silnik1 = silnik.Silnik(27, 22, 13, 16)
silnik2 = silnik.Silnik(5, 6, 26, 21)

def kontrolaSilnikow():
    global silnik1, silnik2
    czas = 0
    czasStart = 0
    while True:
        silniki = [silnik1, silnik2]
        for silnik in silniki:
            if silnik.stan():
                if silnik.stanKierunku():
                    if silnik.stanKraniecDol():
                        #silnik.przelacz(False)
                        #silnik.przelaczKierunek(False)
                        pass
                else:
                    if silnik.stanKraniecGora():
                        silnik.przelacz(False)
                        silnik.przelaczKierunek(True)
                    elif kolizjaWykryta():
                        silnik.przelacz(False)
                        silnik.przelaczKierunek(True)
        time.sleep(0.01)
tsilniki = threading.Thread(target=kontrolaSilnikow)
tsilniki.daemon = True
tsilniki.start()

#z czujnika raspberry w C
def temperatura():
    return CPUTemperature().temperature

global trwaWyjmowanie
trwaWyjmowanie = False

global window, pelnyEkran
window = Tk()
window.title("Program do maszyny podającej soczewki wykonanej przez Pawła Sołtysa")
window.geometry("1920x1080")
pelnyEkran = True
def toggle_fullscreen(event=None):
        global pelnyEkran, window
        pelnyEkran = not pelnyEkran
        window.attributes("-fullscreen", pelnyEkran)
        return "break"
window.bind("<F11>", toggle_fullscreen)
window.attributes("-fullscreen", True)
btn = Button(window, text="PEŁNY EKRAN", font=("Courier", 50), bg="green", activebackground="lime", command=toggle_fullscreen, width=11, height=1)
btn.place(x=0, y=1000)

global lbltemp, lblsoczewka, lbltackinowe, lbltackiZrobione, lblstan, lblzrobsocz, zrobioneSocz, lblszerprzed, lblszerpo
lbltemp = Label(window, text="Temp: 0", font=("Courier", 30), width=12, anchor='e')
lbltemp.place(x=1600, y=1000)
lblsoczewka = Label(window, text="Numer soczewki: 0", font=("Courier", 30), width=18, anchor='w')
lblsoczewka.place(x=0, y=250)
lbl = Label(window, text="Załadowane tacki do obrobienia", font=("Courier", 30), width=30, anchor='w')
lbl.place(x=0, y=300)
lblstan = Label(window, text="-", font=("Courier", 40), width=11, anchor='w')
lblstan.place(x=500, y=0)
zrobioneSocz = 0
lblzrobsocz = Label(window, text="Zrobione soczewki:\n0", font=("Courier", 25), width=18, height=2, anchor='c')
lblzrobsocz.place(x=750, y=100)
def resetujZrobioneSocz():
    global lblzrobsocz, zrobioneSocz
    zrobioneSocz = 0
    lblzrobsocz['text'] = "Zrobione soczewki:\n0"
            
btn = Button(window, text="RESETUJ", font=("Courier", 40), bg="yellow", activebackground="orange", command=resetujZrobioneSocz, width=7, height=1, anchor='c')
btn.place(x=800, y=180)
lblszerprzed = Label(window, text="Szerokość przed:\n0mm", font=("Courier", 25), width=18, height=2, anchor='c')
lblszerprzed.place(x=750, y=260)
global lblszerprzedmin, lblszerprzedmax, lblszerprzedsrd, lblszerpomin, lblszerpomax
lblszerprzedmin = Label(window, text="Przed min: 0mm", font=("Courier", 25), width=18, height=1, anchor='c')
lblszerprzedmin.place(x=750, y=340)
lblszerprzedmax = Label(window, text="Przed max: 0mm", font=("Courier", 25), width=18, height=1, anchor='c')
lblszerprzedmax.place(x=750, y=380)
lblszerprzedsrd = Label(window, text="Przed średnia: 00.00mm", font=("Courier", 25), width=22, height=1, anchor='c')
lblszerprzedsrd.place(x=750, y=420)

lblszerpo = Label(window, text="Szerokość po:\n0mm", font=("Courier", 25), width=18, height=2, anchor='c')
lblszerpo.place(x=750, y=460)
lblszerpomin = Label(window, text="Po min: 0mm", font=("Courier", 25), width=18, height=1, anchor='c')
lblszerpomin.place(x=750, y=540)
lblszerpomax = Label(window, text="Po max: 0mm", font=("Courier", 25), width=18, height=1, anchor='c')
lblszerpomax.place(x=750, y=580)
def resetujMinMax():
    global lblszerprzedmin, lblszerprzedmax, lblszerprzedsrd, lblszerpomin, lblszerpomax
    global szerprzedsuma, szerprzedilosc, szerprzedmin, szerprzedmax, szerpomin, szerpomax
    szerprzedsuma = 0
    szerprzedilosc = 0
    lblszerprzedsrd['text'] = 'Przed średnia: {}mm'.format(0)
    szerprzedmax = 0
    lblszerprzedmax['text'] = 'Przed max: {}mm'.format(str(0))
    szerprzedmin = 100
    lblszerprzedmin['text'] = 'Przed min: {}mm'.format(str(0))
    szerpomax = 100
    lblszerpomax['text'] = 'Po max: {}mm'.format(str(0))
    szerpomin = 0
    lblszerpomin['text'] = 'Po min: {}mm'.format(str(0))            
btn = Button(window, text="RESETUJ", font=("Courier", 40), bg="yellow", activebackground="orange", command=resetujMinMax, width=7, height=1, anchor='c')
btn.place(x=800, y=620)
global lblczasstartstart, lblczasstartstop
lblczasstartstart = Label(window, text="Czas cyklu:\n0s", font=("Courier", 25), width=18, height=2, anchor='c')
lblczasstartstart.place(x=1100, y=100)
lblczasstartstop = Label(window, text="Czas maszyny:\n0s", font=("Courier", 25), width=18, height=2, anchor='c')
lblczasstartstop.place(x=1100, y=200)

def odejmijNowaTacke():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("UPDATE dane SET wartosc = wartosc - 1 WHERE nazwa = 'tackiNowe'")
    global lbltackiZrobione
    for row in c.execute("SELECT wartosc FROM dane WHERE nazwa='tackiNowe'"):
        lbltackinowe['text'] = str(row[0])
    conn.commit()
    conn.close()
btn = Button(window, text="-", font=("Courier", 75), bg="red", activebackground="pink", command=odejmijNowaTacke, width=2, height=1)
btn.place(x=0, y=350)

conn = sqlite3.connect('data.db')
c = conn.cursor()
for row in c.execute("SELECT wartosc FROM dane WHERE nazwa='tackiNowe'"):
    lbltackinowe = Label(window, text=str(row[0]), font=("Courier", 75), width=2, anchor='c')
    lbltackinowe.place(x=150, y=350)
conn.commit()
conn.close()
    
def dodajNowaTacke():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("UPDATE dane SET wartosc = wartosc + 1 WHERE nazwa = 'tackiNowe'")
    global lbltackiNowe
    for row in c.execute("SELECT wartosc FROM dane WHERE nazwa='tackiNowe'"):
        lbltackinowe['text'] = str(row[0])
    conn.commit()
    conn.close()
btn = Button(window, text="+", font=("Courier", 75), bg="green", activebackground="lime", command=dodajNowaTacke, width=2, height=1)
btn.place(x=300, y=350)

lbl = Label(window, text="Zrobione tacki", font=("Courier", 30), width=30, anchor='w')
lbl.place(x=0, y=500)

def odejmijZrobionaTacke():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("UPDATE dane SET wartosc = wartosc - 1 WHERE nazwa = 'tackiZrobione'")
    global lbltackiZrobione
    for row in c.execute("SELECT wartosc FROM dane WHERE nazwa='tackiZrobione'"):
        lbltackiZrobione['text'] = str(row[0])
    conn.commit()
    conn.close()

def zerujZrobioneTacki():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("UPDATE dane SET wartosc = 0 WHERE nazwa = 'tackiZrobione'")
    global lbltackiZrobione
    for row in c.execute("SELECT wartosc FROM dane WHERE nazwa='tackiZrobione'"):
        lbltackiZrobione['text'] = str(row[0])
    conn.commit()
    conn.close()

btn = Button(window, text="-", font=("Courier", 75), bg="red", activebackground="pink", command=odejmijZrobionaTacke, width=2, height=1)
btn.place(x=0, y=550)
conn = sqlite3.connect('data.db')
c = conn.cursor()
for row in c.execute("SELECT wartosc FROM dane WHERE nazwa='tackiZrobione'"):
    lbltackiZrobione = Label(window, text=str(row[0]), font=("Courier", 75), width=2, anchor='c')
    lbltackiZrobione.place(x=150, y=550)
conn.commit()
conn.close()
def dodajZrobionaTacke():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("UPDATE dane SET wartosc = wartosc + 1 WHERE nazwa = 'tackiZrobione'")
    global lbltackiZrobione
    for row in c.execute("SELECT wartosc FROM dane WHERE nazwa='tackiZrobione'"):
        lbltackiZrobione['text'] = str(row[0])
    conn.commit()
    conn.close()
        
btn = Button(window, text="+", font=("Courier", 75), bg="green", activebackground="lime", command=dodajZrobionaTacke, width=2, height=1)
btn.place(x=300, y=550)

def zaladujTacke():
    global silnik1, silnk2
    if silnik1.stan() or silnik2.stan():
        return
    silnik1.jedzDoDolu()
    if silnik1.stanKraniecGora():
       time.sleep(2.6+2)
    else:
        time.sleep(2.6)
    silnik1.stop()
    dodajNowaTacke()
    
btn = Button(window, text="Załaduj\nTackę", font=("Courier", 30), bg="lightgray", activebackground="gray", command=zaladujTacke, width=11, height=2)
btn.place(x=1600, y=850)

def otworzChwytak():
    requests.get('http://192.168.1.151/api/dc/twofg/grip_external/0/39/20/10')
btn = Button(window, text="Otworz\nChwytak", font=("Courier", 30), bg="red", activebackground="pink", command=otworzChwytak, width=11, height=2)
btn.place(x=1600, y=700)

def start():
    global soczewka, watekglowny
    soczewka = -1
    watekglowny = threading.Thread(target=glownyWatek)
    watekglowny.daemon = True
    watekglowny.start()
btn = Button(window, text="START\nOD NOWA", font=("Courier", 30), bg="lime", activebackground="light green", command=start, width=16, height=2)
btn.place(x=0, y=15)

def startOd():
    show_keypad()
btn = Button(window, text="START OD\nWYBRANEJ SOCZEWKI", font=("Courier", 30), bg="lime", activebackground="light green", command=startOd, width=16, height=2)
btn.place(x=0, y=130)

def podniesNowe():
    global silnik1
    silnik1.jedzDoGory()
btn = Button(window, text="Podnieś\nNowe", font=("Courier", 30), bg="red", activebackground="pink", command=podniesNowe, width=11, height=2)
btn.place(x=1600, y=0)

def zatrzymajNowe():
    global silnik1
    silnik1.stop()
btn = Button(window, text="Zatrzymaj\nNowe", font=("Courier", 30), bg="red", activebackground="pink", command=zatrzymajNowe, width=11, height=2)
btn.place(x=1600, y=100)

def opuscNowe():
    global silnik1
    silnik1.jedzDoDolu()
btn = Button(window, text="Opuść\nNowe", font=("Courier", 30), bg="red", activebackground="pink", command=opuscNowe, width=11, height=2)
btn.place(x=1600, y=200)

def podniesZrobione():
    global silnik2
    silnik2.jedzDoGory()
btn = Button(window, text="Podnieś\nZrobione", font=("Courier", 30), bg="red", activebackground="pink", command=podniesZrobione, width=11, height=2)
btn.place(x=1600, y=300)

def zatrzymajZrobione():
    global silnik2
    silnik2.stop()
btn = Button(window, text="Zatrzymaj\nZrobione", font=("Courier", 30), bg="red", activebackground="pink", command=zatrzymajZrobione, width=11, height=2)
btn.place(x=1600, y=400)

def opuscZrobione():
    global silnik2
    silnik2.jedzDoDolu()
btn = Button(window, text="Opuść\nZrobione", font=("Courier", 30), bg="red", activebackground="pink", command=opuscZrobione, width=11, height=2)
btn.place(x=1600, y=500)

def wyjmowanieSoczewek():
    global trwaWyjmowanie
    trwaWyjmowanie = True
    opuscZrobione()
    time.sleep(5)
    zatrzymajZrobione()
    global oknoRozladunek
    oknoRozladunek.place(x=200, y=300)
    
btn = Button(window, text="CHCĘ\nWYJĄĆ\nTACKI", font=("Courier", 50), bg="green", activebackground="lime", command=wyjmowanieSoczewek, width=11, height=3)
btn.place(x=0, y=700)

def punktKalibracyjny():
    client.publish("cobot/polecenia","punkt kalibracyjny")
    
btn = Button(window, text="PUNKT\nKALIBRACYJNY", font=("Courier", 50), bg="pink", activebackground="red", command=punktKalibracyjny, width=12, height=2)
btn.place(x=800, y=800)

def stopProgram():
    os._exit(0)
    
btn = Button(window, text="STOP", font=("Courier", 50), bg="red", activebackground="pink", command=stopProgram, width=12, height=1)
btn.place(x=800, y=1000)

def aktualizujOkno():
    global lbltemp, lblstan, watekglowny
    while True:
        lbltemp['text']='Temp: '+str(temperatura())
        if watekglowny.is_alive():
            lblstan['text']='Pracuję'
        else:
            lblstan['text']='Nie pracuję'
        time.sleep(1)
twindow = threading.Thread(target=aktualizujOkno)
twindow.daemon = True
twindow.start()
global pomin
pomin = {0, 10, 87, 77, 38, 49}
def create_keypad(root):
    global pomin
    keypad = Frame(root)
    lbl = Label(keypad, text="ROBOT", font=("Courier", 75), width=2, anchor='c')
    lbl.grid(row=0, column=3, columnspan=5, sticky='news')
    for x in range(8):
        for y in range(11):
            val = x*11+y
            if val in pomin:
                continue
            text = str(val)
            b = Button(keypad, text='⭕', command=lambda numer=val:zapiszSoczewke(numer), font=("Courier", 35), bg='white', activebackground='gray')
            b.grid(row=x+1, column=y, sticky='news')
    lbl = Label(keypad, text=" ", font=("Courier", 40), width=2, anchor='c')
    lbl.grid(row=9, column=0, columnspan=5, sticky='news')
    x = Button(keypad, text='❌ Anuluj', command=hide_keypad, font=("Courier", 35), bg='white', activebackground='gray')
    x.grid(row=10, column=5, columnspan=3, sticky='news')
    x = Button(keypad, text='✔️ OK', command=potwierdzBranieSoczewki, font=("Courier", 35), bg='white', activebackground='gray')
    x.grid(row=10, column=3, columnspan=2, sticky='news')
    return keypad

def create_rozladunek(root):
    okno = Frame(root)
    lbl = Label(okno, text="CZY ZOSTAŁY WYJĘTE\nWSZYSTKIE TACKI?", font=("Courier", 75), width=25, anchor='c', bg='blue')
    lbl.grid(row=0, column=0, columnspan=1, sticky='news')
    x = Button(okno, text='TAK', command=koniecRozladunku, font=("Courier", 50), bg='white', activebackground='gray')
    x.grid(row=1, column=0, columnspan=1, sticky='news')
    return okno

def koniecRozladunku():
    global trwaWyjmowanie, oknoRozladunek
    trwaWyjmowanie = False
    oknoRozladunek.place_forget()
    zerujZrobioneTacki()
    
def wezSoczewke():
    global soczewka, pomin, msgmqtt,  lblsoczewka, trwaWyjmowanie, maszynaPusta
    lblsoczewka['text'] = "Numer soczewki: "+str(soczewka)
    client.publish("cobot/polecenia","wez soczewke:"+str(soczewka))
    while not msgmqtt == 'nie wykryto soczewki' and not msgmqtt == 'soczewka zabrana':
        time.sleep(0.1)
    if msgmqtt == 'nie wykryto soczewki':
        msgmqtt = ''
        nastepnaSoczewka()
        if soczewka < 87:
            wezSoczewke()
        return
    while not msgmqtt == 'soczewka odlozona':
        time.sleep(0.1)
    msgmqtt = ''

def wlozSoczewkeZeSlupka():
    global msgmqtt, maszynaPusta, soczewka
    client.publish("cobot/polecenia","zabierz ze slupka")
    while not msgmqtt == 'soczewka wlozona':
        time.sleep(0.1)
    maszynaPusta = False

def wyjmijSoczewkeZMaszyny():
    global msgmqtt, maszynaPusta, soczewka, ostatniaSoczewka
    #print('wyjmij z maszyny i odloz na miejsce:', ostatniaSoczewka)
    client.publish("cobot/polecenia","wyjmij z maszyny:"+str(ostatniaSoczewka))
    while not msgmqtt == 'soczewka wyjeta':
        time.sleep(0.1)
    maszynaPusta = True
    global lblzrobsocz, zrobioneSocz
    zrobioneSocz += 1
    lblzrobsocz['text'] = "Zrobione soczewki:\n"+str(zrobioneSocz)

global wybranaSoczewka, soczewka, ostatniaSoczewka
wybranaSoczewka = None
soczewka = -1
ostatniaSoczewka = -1
def zapiszSoczewke(numer):
    global wybranaSoczewka
    wybranaSoczewka = numer

def potwierdzBranieSoczewki():
    global wybranaSoczewka, soczewka, watekglowny
    if wybranaSoczewka == None:
        return
    hide_keypad()
    soczewka = wybranaSoczewka
    watekglowny = threading.Thread(target=glownyWatek)
    watekglowny.daemon = True
    watekglowny.start()
    
def show_keypad():
    global keypad, wybranaSoczewka
    wybranaSoczewka = None
    keypad.place(x=500, y=100)

def hide_keypad():
    global keypad
    keypad.place_forget()

def wezNowaTacke():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    tackiNowe = 0
    for row in c.execute("SELECT wartosc FROM dane WHERE nazwa='tackiNowe'"):
        tackiNowe = int(row[0])
    conn.commit()
    conn.close()
    if tackiNowe < 1:
        return False
    global client
    client.publish("cobot/polecenia","wez nowa tacke")
    while not msgmqtt == 'podaj tacke':
        time.sleep(0.1)
    silnik1.jedzDoGory()
    while silnik1.stan():
        time.sleep(0.1)
    if silnik1.stanKraniecGora():
        return False
    odejmijNowaTacke()
    client.publish("cobot/polecenia","tacka podana")
    while not msgmqtt == 'podnies tacki':
        time.sleep(0.1)
    silnik2.jedzDoGory()
    while silnik2.stan():
        time.sleep(0.1)
    client.publish("cobot/polecenia","tacki podniesione")
    while not msgmqtt == 'tacka oddana':
        time.sleep(0.1)
    silnik2.jedzDoDolu()
    time.sleep(1)
    silnik2.stop()
    return True

def schowajZrobionaTacke():
    global silnik2
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    zrobioneTacki = 0
    for row in c.execute("SELECT wartosc FROM dane WHERE nazwa='tackiZrobione'"):
        zrobioneTacki = int(row[0])
    conn.commit()
    conn.close()
    if zrobioneTacki == 0:
        client.publish("cobot/polecenia","jedz nad zrobione")
        while not msgmqtt == 'jestem na miejscu':
            time.sleep(0.1)
        silnik2.jedzDoGory()
        while silnik2.stan():
            time.sleep(0.1)
    else:   
        silnik2.jedzDoGory()
        time.sleep(1.75)
        silnik2.stop()
    przelaczElektromagnesy(True)
    silnik2.jedzDoDolu()
    time.sleep(8)
    silnik2.stop()
    przelaczElektromagnesy(False)
    dodajZrobionaTacke()

def poprzedniaSoczewka(numer):
    numer -= 1
    while numer in pomin and numer >= 0:
        numer -= 1
    if numer < 0:
        exit()
        return
    return numer

def nastepnaSoczewka():
    global soczewka, pomin, lblsoczewka
    soczewka += 1
    while soczewka in pomin:
        soczewka += 1
    lblsoczewka['text'] = "Numer soczewki: "+str(soczewka)

def glownyWatek():
    global soczewka, maszynaPusta, msgmqtt, ostatniaSoczewka
    while True:
        if soczewka == 88:
            client.publish("cobot/polecenia","czekaj na maszyne")
            while not msgmqtt == 'koniec obrobki soczewki':
                time.sleep(0.1)
            wyjmijSoczewkeZMaszyny()
            nastepnaSoczewka()
            continue
        if soczewka > 88:
            while trwaWyjmowanie:
                time.sleep(0.1)
            schowajZrobionaTacke()
            if not wezNowaTacke():
                break
            time.sleep(3)
            soczewka = 0
            nastepnaSoczewka()
        if soczewka == -1:
            if not wezNowaTacke():
                break
            time.sleep(3)
            soczewka = 0
            nastepnaSoczewka()
        wezSoczewke()
        if maszynaPusta:
            wlozSoczewkeZeSlupka()
        else:
            #print('czekam na maszyne')
            client.publish("cobot/polecenia","czekaj na maszyne")
            while not msgmqtt == 'koniec obrobki soczewki':
                time.sleep(0.1)
            #print('maszyna skonczyla')
            time.sleep(2)
            wyjmijSoczewkeZMaszyny()
            wlozSoczewkeZeSlupka()
        ostatniaSoczewka = soczewka
        nastepnaSoczewka()
    lblsoczewka['text'] = 'BŁĄD! Brak tacek'

global watekglowny
watekglowny = threading.Thread(target=glownyWatek)
watekglowny.daemon = True

global keypad, oknoRozladunek
keypad = create_keypad(window)
oknoRozladunek = create_rozladunek(window)
window.mainloop()
