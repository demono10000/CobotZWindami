import time
from inputs import get_gamepad
from silnik import silnik1, silnik2
import elektromagnes
import cobot


def padController():
    while True:
        events = get_gamepad()
        for event in events:
            # print(event.code, event.state)
            if(event.code == "ABS_HAT0Y"):
                if(event.state == -1):
                    silnik2.jedzDoGory()
                elif(event.state == 1):
                    silnik2.jedzDoDolu()
                else:
                    silnik2.stop()
            elif(event.code == "BTN_WEST"):
                if(event.state == 1):
                    silnik1.jedzDoGory()
                else:
                    silnik1.stop()
            elif(event.code == "BTN_SOUTH"):
                if(event.state == 1):
                    silnik1.jedzDoDolu()
                else:
                    silnik1.stop()
            elif(event.code == "BTN_EAST"):
                if(event.state == 1):
                    elektromagnes.przelaczElektromagnesy(True)
                else:
                    elektromagnes.przelaczElektromagnesy(False)
            elif(event.code == "BTN_NORTH"):
                if(event.state == 1):
                    cobot.wezNowaTacke()
            elif(event.code == "BTN_TL"):
                if(event.state == 1):
                    cobot.schowajZrobionaTacke()
        time.sleep(0.01)
