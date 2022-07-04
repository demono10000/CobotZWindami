#! /usr/bin/env python
import piny
import database
import mqtt
import gui


def main():
    piny
    database.stworzBaze()
    mqtt.inicjalizacja()
    gui.stworzGUI()
    gui.guiGlowne.mainloop()


if __name__ == '__main__':
    main()
