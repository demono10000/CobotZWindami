#! /usr/bin/env python
import RPi.GPIO as GPIO
import sqlite3
import elementyGlobalne
import gui
import mqtt

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

mqtt

gui.guiGlowne.mainloop()
