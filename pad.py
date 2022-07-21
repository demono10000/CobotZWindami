import time
from inputs import get_gamepad
from silnik import silnik1, silnik2
import elektromagnes
# import cobot


def padController():
    while True:
        events = get_gamepad()
        for event in events:
            # print(event.code, event.state)
            if(event.code == "ABS_HAT0Y"):
                ruszSilnik(silnik2, event.state)
            elif(event.code == "BTN_WEST"):
                ruszSilnik(silnik1, -event.state)
            elif(event.code == "BTN_SOUTH"):
                ruszSilnik(silnik1, event.state)
            elif(event.code == "BTN_EAST"):
                elektromagnes.przelaczElektromagnesy(event.state)
            """ elif(event.code == "BTN_NORTH" and event.state == 1):
                cobot.wezNowaTacke()
            elif(event.code == "BTN_TL" and event.state == 1):
                cobot.schowajZrobionaTacke() """
        time.sleep(0.01)


def ruszSilnik(silnik, wartosc):
    if wartosc == -1:
        silnik.jedzDoGory()
    elif wartosc == 1:
        silnik.jedzDoDolu()
    else:
        silnik.stop()
