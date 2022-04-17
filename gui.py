import tkinter as tk
import sqlite3
import requests
import os
import time
import threading
import elementyGlobalne
from silnik import silnik1, silnik2
import termometr
import watki


class Gui(tk.Tk):
    pelnyEkran = True
    zrobioneSoczewki = 0
    szerokoscPrzedSuma = 0
    szerokoscPrzedIlosc = 0
    szerokoscPrzedMax = 0
    szerokoscPrzedMin = 100
    szerokoscPoMax = 100
    szerokoscPoMin = 0

    def __init__(self):
        super().__init__()
        self.keypad = self.create_keypad()
        self.oknoRozladunek = self.create_rozladunek()
        self.title("Program do maszyny podającej soczewki wykonanej przez Pawła Sołtysa")
        self.geometry("1920x1080")
        self.bind("<F11>", self.toggle_fullscreen)
        self.button = tk.Button(
            self,
            text="PEŁNY EKRAN",
            font=("Courier", 50),
            bg="green",
            activebackground="lime",
            command=self.toggle_fullscreen,
            width=11,
            height=1
        )
        self.button.place(x=0, y=1000)
        self.labelTemperatura = tk.Label(
            self,
            text="Temp: 0",
            font=("Courier", 30),
            width=12,
            anchor='e'
        )
        self.labelTemperatura.place(x=1600, y=1000)
        self.labelSoczewka = tk.Label(
            self,
            text="Numer soczewki: 0",
            font=("Courier", 30),
            width=18,
            anchor='w'
        )
        self.labelSoczewka.place(x=0, y=250)
        self.label = tk.Label(
            self,
            text="Załadowane tacki do obrobienia",
            font=("Courier", 30),
            width=30,
            anchor='w'
        )
        self.label.place(x=0, y=300)
        self.labelStan = tk.Label(
            self,
            text="-",
            font=("Courier", 40),
            width=11,
            anchor='w'
        )
        self.labelStan.place(x=500, y=0)
        self.labelZrobioneSoczewki = tk.Label(
            self,
            text="Zrobione soczewki:\n0",
            font=("Courier", 25), width=18,
            height=2,
            anchor='c'
        )
        self.labelZrobioneSoczewki.place(x=750, y=100)
        self.button = tk.Button(
            self, text="RESETUJ",
            font=("Courier", 40),
            bg="yellow",
            activebackground="orange",
            command=self.resetujZrobioneSoczewki,
            width=7,
            height=1,
            anchor='c'
        )
        self.button.place(x=800, y=180)
        self.labelSzerokoscPrzed = tk.Label(
            self,
            text="Szerokość przed:\n0mm",
            font=("Courier", 25),
            width=18,
            height=2,
            anchor='c'
        )
        self.labelSzerokoscPrzed.place(x=750, y=260)
        self.labelSzerokoscPrzedMin = tk.Label(
            self,
            text="Przed min: 0mm",
            font=("Courier", 25),
            width=18,
            height=1,
            anchor='c'
        )
        self.labelSzerokoscPrzedMin.place(x=750, y=340)
        self.labelSzerokoscPrzedMax = tk.Label(
            self,
            text="Przed max: 0mm",
            font=("Courier", 25),
            width=18,
            height=1,
            anchor='c'
        )
        self.labelSzerokoscPrzedMax.place(x=750, y=380)
        self.labelSzerokoscPrzedSrednia = tk.Label(
            self,
            text="Przed średnia: 00.00mm",
            font=("Courier", 25),
            width=22,
            height=1,
            anchor='c'
        )
        self.labelSzerokoscPrzedSrednia.place(x=750, y=420)
        self.labelSzerokoscPo = tk.Label(
            self,
            text="Szerokość po:\n0mm",
            font=("Courier", 25),
            width=18,
            height=2,
            anchor='c'
        )
        self.labelSzerokoscPo.place(x=750, y=460)
        self.labelSzerokoscPoMin = tk.Label(
            self,
            text="Po min: 0mm",
            font=("Courier", 25),
            width=18,
            height=1,
            anchor='c'
        )
        self.labelSzerokoscPoMin.place(x=750, y=540)
        self.labelSzerokoscPoMax = tk.Label(
            self,
            text="Po max: 0mm",
            font=("Courier", 25),
            width=18,
            height=1,
            anchor='c'
        )
        self.labelSzerokoscPoMax.place(x=750, y=580)
        self.button = tk.Button(
            self,
            text="RESETUJ",
            font=("Courier", 40),
            bg="yellow",
            activebackground="orange",
            command=self.resetujMinMax,
            width=7,
            height=1,
            anchor='c'
        )
        self.button.place(x=800, y=620)
        self.labelCzasStartStart = tk.Label(
            self,
            text="Czas cyklu:\n0s",
            font=("Courier", 25),
            width=18,
            height=2,
            anchor='c'
        )
        self.labelCzasStartStart.place(x=1100, y=100)
        self.labelCzasStartStop = tk.Label(
            self,
            text="Czas maszyny:\n0s",
            font=("Courier", 25),
            width=18,
            height=2,
            anchor='c'
        )
        self.labelCzasStartStop.place(x=1100, y=200)
        self.button = tk.Button(
            self,
            text="-",
            font=("Courier", 75),
            bg="red",
            activebackground="pink",
            command=lambda: self.zmienNoweTacki(-1),
            width=2,
            height=1
        )
        self.button.place(x=0, y=350)
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        for row in c.execute("SELECT wartosc FROM dane WHERE nazwa='tackiNowe'"):
            self.labelTackiNowe = tk.Label(
                self,
                text=str(row[0]),
                font=("Courier", 75),
                width=2,
                anchor='c'
            )
            self.labelTackiNowe.place(x=150, y=350)
        conn.commit()
        conn.close()
        self.button = tk.Button(
            self,
            text="+",
            font=("Courier", 75),
            bg="green",
            activebackground="lime",
            command=lambda: self.zmienNoweTacki(1),
            width=2,
            height=1
        )
        self.button.place(x=300, y=350)
        self.label = tk.Label(
            self,
            text="Zrobione tacki",
            font=("Courier", 30),
            width=30,
            anchor='w'
        )
        self.label.place(x=0, y=500)
        self.button = tk.Button(
            self,
            text="-",
            font=("Courier", 75),
            bg="red",
            activebackground="pink",
            command=lambda: self.zmienZrobioneTacki(-1),
            width=2,
            height=1
        )
        self.button.place(x=0, y=550)
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        for row in c.execute("SELECT wartosc FROM dane WHERE nazwa='tackiZrobione'"):
            self.labelTackiZrobione = tk.Label(
                self,
                text=str(row[0]),
                font=("Courier", 75),
                width=2,
                anchor='c'
            )
            self.labelTackiZrobione.place(x=150, y=550)
        conn.commit()
        conn.close()
        self.button = tk.Button(
            self,
            text="+",
            font=("Courier", 75),
            bg="green",
            activebackground="lime",
            command=lambda: self.zmienZrobioneTacki(1),
            width=2,
            height=1
        )
        self.button.place(x=300, y=550)
        self.button = tk.Button(
            self,
            text="Załaduj\nTackę",
            font=("Courier", 30),
            bg="lightgray", activebackground="gray",
            command=self.zaladujTacke,
            width=11,
            height=2
        )
        self.button.place(x=1600, y=850)
        self.button = tk.Button(
            self,
            text="Otworz\nChwytak",
            font=("Courier", 30),
            bg="red", activebackground="pink",
            command=self.otworzChwytak,
            width=11,
            height=2
        )
        self.button.place(x=1600, y=700)
        self.button = tk.Button(
            self,
            text="START\nOD NOWA",
            font=("Courier", 30),
            bg="lime",
            activebackground="light green",
            command=self.start,
            width=16,
            height=2
        )
        self.button.place(x=0, y=15)
        self.button = tk.Button(
            self,
            text="START OD\nWYBRANEJ SOCZEWKI",
            font=("Courier", 30),
            bg="lime",
            activebackground="light green",
            command=self.startOd,
            width=16,
            height=2
        )
        self.button.place(x=0, y=130)
        self.button = tk.Button(
            self,
            text="Podnieś\nNowe",
            font=("Courier", 30),
            bg="red",
            activebackground="pink",
            command=self.podniesNowe,
            width=11,
            height=2
        )
        self.button.place(x=1600, y=0)
        self.button = tk.Button(
            self,
            text="Zatrzymaj\nNowe",
            font=("Courier", 30),
            bg="red",
            activebackground="pink",
            command=self.zatrzymajNowe,
            width=11,
            height=2
        )
        self.button.place(x=1600, y=100)
        self.button = tk.Button(
            self,
            text="Opuść\nNowe",
            font=("Courier", 30),
            bg="red",
            activebackground="pink",
            command=self.opuscNowe,
            width=11,
            height=2
        )
        self.button.place(x=1600, y=200)
        self.button = tk.Button(
            self,
            text="Podnieś\nZrobione",
            font=("Courier", 30),
            bg="red",
            activebackground="pink",
            command=self.podniesZrobione,
            width=11,
            height=2
        )
        self.button.place(x=1600, y=300)
        self.button = tk.Button(
            self,
            text="Zatrzymaj\nZrobione",
            font=("Courier", 30),
            bg="red",
            activebackground="pink",
            command=self.zatrzymajZrobione,
            width=11,
            height=2
        )
        self.button.place(x=1600, y=400)
        self.button = tk.Button(
            self,
            text="Opuść\nZrobione",
            font=("Courier", 30),
            bg="red",
            activebackground="pink",
            command=self.opuscZrobione,
            width=11,
            height=2
        )
        self.button.place(x=1600, y=500)
        self.button = tk.Button(
            self,
            text="CHCĘ\nWYJĄĆ\nTACKI",
            font=("Courier", 50),
            bg="green",
            activebackground="lime",
            command=self.wyjmowanieSoczewek,
            width=11,
            height=3
        )
        self.button.place(x=0, y=700)
        self.button = tk.Button(
            self,
            text="PUNKT\nKALIBRACYJNY",
            font=("Courier", 50),
            bg="pink",
            activebackground="red",
            command=self.punktKalibracyjny,
            width=12,
            height=2
        )
        self.button.place(x=800, y=800)
        self.button = tk.Button(
            self,
            text="STOP",
            font=("Courier", 50),
            bg="red",
            activebackground="pink",
            command=self.stopProgram,
            width=12,
            height=1
        )
        self.button.place(x=800, y=1000)

    def toggle_fullscreen(self, event=None):
        self.pelnyEkran = not self.pelnyEkran
        self.attributes("-fullscreen", self.pelnyEkran)

    def resetujZrobioneSoczewki(self, event=None):
        self.zrobioneSocz = 0
        self.labelZrobioneSoczewki['text'] = "Zrobione soczewki:\n" + str(self.zrobioneSocz)

    def resetujMinMax(self, event=None):
        self.szerokoscPrzedSuma = 0
        self.szerokoscPrzedIlosc = 0
        self.labelSzerokoscPrzedSrednia['text'] = 'Przed średnia: {}mm'.format(0)
        self.szerokoscPrzedMax = 0
        self.labelSzerokoscPrzedMax['text'] = 'Przed max: {}mm'.format(str(0))
        self.szerokoscPrzedMin = 100
        self.labelSzerokoscPrzedMin['text'] = 'Przed min: {}mm'.format(str(0))
        self.szerokoscPoMax = 100
        self.labelSzerokoscPoMax['text'] = 'Po max: {}mm'.format(str(0))
        self.szerokoscPoMin = 0
        self.labelSzerokoscPoMin['text'] = 'Po min: {}mm'.format(str(0))

    def zmienNoweTacki(self, liczba, event=None):
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        c.execute("UPDATE dane SET wartosc = wartosc + ? WHERE nazwa = 'tackiNowe'", (liczba,))
        for row in c.execute("SELECT wartosc FROM dane WHERE nazwa='tackiNowe'"):
            self.labelTackiNowe['text'] = str(row[0])
        conn.commit()
        conn.close()

    def zmienZrobioneTacki(self, liczba, event=None):
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        if liczba == 0:
            c.execute("UPDATE dane SET wartosc = 0 WHERE nazwa = 'tackiZrobione'")
        else:
            c.execute("UPDATE dane SET wartosc = wartosc + ? WHERE nazwa = 'tackiZrobione'",
                      (liczba,))
        for row in c.execute("SELECT wartosc FROM dane WHERE nazwa='tackiZrobione'"):
            self.labelTackiZrobione['text'] = str(row[0])
        conn.commit()
        conn.close()

    def zaladujTacke(self, event=None):
        if silnik1.stan() or silnik2.stan():
            return
        silnik1.jedzDoDolu()
        if silnik1.stanKraniecGora():
            time.sleep(2.6 + 2)
        else:
            time.sleep(2.6)
        silnik1.stop()
        self.dodajNowaTacke()

    def otworzChwytak(self, event=None):
        requests.get('http://192.168.1.151/api/dc/twofg/grip_external/0/39/20/10')

    def start(self, event=None):
        elementyGlobalne.soczewka = -1
        watki.watekglowny = threading.Thread(target=watki.glownyWatek)
        watki.watekglowny.daemon = True
        watki.watekglowny.start()

    def startOd(self, event=None):
        self.show_keypad()

    def podniesNowe(self, event=None):
        silnik1.jedzDoGory()

    def zatrzymajNowe(self, event=None):
        silnik1.stop()

    def opuscNowe(self, event=None):
        silnik1.jedzDoDolu()

    def podniesZrobione(self, event=None):
        silnik2.jedzDoGory()

    def zatrzymajZrobione(self, event=None):
        silnik2.stop()

    def opuscZrobione(self, event=None):
        silnik2.jedzDoDolu()

    def wyjmowanieSoczewek(self, event=None):
        elementyGlobalne.trwaWyjmowanie = True
        self.opuscZrobione()
        time.sleep(5)
        self.zatrzymajZrobione()
        self.oknoRozladunek.place(x=200, y=300)

    def punktKalibracyjny(self, event=None):
        elementyGlobalne.client.publish("cobot/polecenia", "punkt kalibracyjny")

    def stopProgram(self, event=None):
        os._exit(0)

    def show_keypad(self, event=None):
        elementyGlobalne.wybranaSoczewka = None
        self.keypad.place(x=500, y=100)

    def create_keypad(self):
        keypad = tk.Frame(self)
        lbl = tk.Label(
            keypad,
            text="ROBOT",
            font=("Courier", 75),
            width=2,
            anchor='c'
        )
        lbl.grid(row=0, column=3, columnspan=5, sticky='news')
        for x in range(8):
            for y in range(11):
                val = x * 11 + y
                if val in elementyGlobalne.pomin:
                    continue
                b = tk.Button(
                    keypad,
                    text='⭕',
                    command=lambda numer=val: self.zapiszSoczewke(numer),
                    font=("Courier", 35),
                    bg='white',
                    activebackground='gray'
                )
                b.grid(row=x + 1, column=y, sticky='news')
        lbl = tk.Label(
            keypad,
            text=" ",
            font=("Courier", 40),
            width=2,
            anchor='c'
        )
        lbl.grid(row=9, column=0, columnspan=5, sticky='news')
        x = tk.Button(
            keypad,
            text='❌ Anuluj',
            command=self.hide_keypad,
            font=("Courier", 35),
            bg='white',
            activebackground='gray'
        )
        x.grid(row=10, column=5, columnspan=3, sticky='news')
        x = tk.Button(
            keypad,
            text='✔️ OK',
            command=self.potwierdzBranieSoczewki,
            font=("Courier", 35),
            bg='white',
            activebackground='gray'
        )
        x.grid(row=10, column=3, columnspan=2, sticky='news')
        return keypad

    def hide_keypad(self):
        self.keypad.place_forget()

    def create_rozladunek(self):
        okno = tk.Frame(self)
        lbl = tk.Label(
            okno,
            text="CZY ZOSTAŁY WYJĘTE\nWSZYSTKIE TACKI?",
            font=("Courier", 75),
            width=25,
            anchor='c',
            bg='blue'
        )
        lbl.grid(row=0, column=0, columnspan=1, sticky='news')
        x = tk.Button(
            okno,
            text='TAK',
            command=self.koniecRozladunku,
            font=("Courier", 50),
            bg='white',
            activebackground='gray'
        )
        x.grid(row=1, column=0, columnspan=1, sticky='news')
        return okno

    def potwierdzBranieSoczewki(self, event=None):
        if elementyGlobalne.wybranaSoczewka is None:
            return
        self.hide_keypad()
        elementyGlobalne.soczewka = elementyGlobalne.wybranaSoczewka
        watki.watekglowny = threading.Thread(target=watki.glownyWatek)
        watki.watekglowny.daemon = True
        watki.watekglowny.start()

    def zapiszSoczewke(self, numer, event=None):
        elementyGlobalne.wybranaSoczewka = numer

    def koniecRozladunku(self, event=None):
        elementyGlobalne.trwaWyjmowanie = False
        self.oknoRozladunek.place_forget()
        self.zmienZrobioneTacki(0)

    def aktualizujOkno(self):
        self.labelTemperatura['text'] = 'Temp: ' + str(termometr.temperatura())
        if watki.watekglowny.is_alive():
            self.labelStan['text'] = 'Pracuję'
        else:
            self.labelStan['text'] = 'Nie pracuję'


guiGlowne = Gui()


def odswiezOkno():
    while True:
        guiGlowne.aktualizujOkno()
        time.sleep(1)


twindow = threading.Thread(target=odswiezOkno)
twindow.daemon = True
twindow.start()
