# Задание 3.3. Кнопка-переключатель
# Кнопка между GPIO 15 и GND (PULL_UP: отпущена = 1, нажата = 0)
# Каждое нажатие переключает светодиод на GPIO 2
from machine import Pin
import time

led = Pin(2, Pin.OUT)
button = Pin(15, Pin.IN, Pin.PULL_UP)

led_on = False
prev = button.value()

while True:
    cur = button.value()
    if prev == 1 and cur == 0:      # момент нажатия (1 -> 0)
        time.sleep_ms(30)           # антидребезг
        if button.value() == 0:     # нажатие настоящее
            led_on = not led_on
            led.value(led_on)
            print("Светодиод", "включён" if led_on else "выключен")
    prev = cur
    time.sleep_ms(10)
