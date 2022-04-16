from gpiozero import CPUTemperature


# z czujnika raspberry w C
def temperatura():
    return CPUTemperature().temperature
