#! /usr/bin/env python
import database
import mqtt
import gui
import piny


def main():
    piny.ustawPiny()
    database.stworzBaze()
    mqtt.inicjalizacja()
    gui.stworzGUI()
    gui.guiGlowne.mainloop()


if __name__ == '__main__':
    main()
