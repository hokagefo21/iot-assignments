# Задание 3.2. Термометр с вентилятором
# DHT22 -> GPIO 4, светодиод ("вентилятор") -> GPIO 2
# Каждые 2 с печатаем t и влажность; выше 30 °C включаем вентилятор
import dht
import time
from machine import Pin

THRESHOLD = 30.0

sensor = dht.DHT22(Pin(4))
fan = Pin(2, Pin.OUT)

while True:
    try:
        sensor.measure()        # сначала запускаем измерение
        t = sensor.temperature()
        h = sensor.humidity()
        fan_on = t > THRESHOLD  # ровно 30 °C - выключен
        fan.value(1 if fan_on else 0)
        state = "ВКЛ" if fan_on else "ВЫКЛ"
        print("t = {:.1f} C | влажность = {:.1f} % | вентилятор: {}".format(
            t, h, state))
    except OSError as e:
        print("Ошибка чтения DHT22:", e)
    time.sleep(2)  # DHT22 нельзя опрашивать чаще раза в 2 с
