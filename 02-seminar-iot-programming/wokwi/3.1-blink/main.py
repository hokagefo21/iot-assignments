# Задание 3.1. Мигание: период 0,5 с (0,25 с горит, 0,25 с нет)
# Светодиод на GPIO 2 через резистор 220 Ом
from machine import Pin
import time

led = Pin(2, Pin.OUT)

while True:
    led.value(1)       # включить
    time.sleep(0.25)
    led.value(0)       # выключить
    time.sleep(0.25)
