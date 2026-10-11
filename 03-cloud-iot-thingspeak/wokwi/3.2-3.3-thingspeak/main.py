import network, time

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("Wokwi-GUEST", "")
print("Подключение к Wi-Fi", end="")
while not wlan.isconnected():
    print(".", end="")
    time.sleep(0.1)
print(" готово:", wlan.ifconfig()[0])

# ---- Задания 3.2 и 3.3: отправка в ThingSpeak каждые 20 с ----
import dht
import urequests
from machine import Pin

try:
    from config import WRITE_API_KEY      # ключ хранится в отдельном файле
except ImportError:
    WRITE_API_KEY = "XXXXXXXXXXXXXXXX"    # вставьте свой Write API Key

URL = "https://api.thingspeak.com/update"
INTERVAL = 20        # бесплатный ThingSpeak принимает не чаще 1 раза в 15 с
ALARM_T = 30.0       # порог тревоги, °C

sensor = dht.DHT22(Pin(4))
sent = 0

while True:
    try:
        sensor.measure()
        t = sensor.temperature()
        h = sensor.humidity()
        alarm = 1 if t > ALARM_T else 0             # field3 = 1 при t > 30 °C

        r = urequests.get("{}?api_key={}&field1={:.1f}&field2={:.1f}&field3={}"
                          .format(URL, WRITE_API_KEY, t, h, alarm))
        entry = r.text.strip()                      # номер записи, 0 = отклонено
        r.close()

        if entry != "0":
            sent += 1
        print("t={:.1f} C h={:.1f} % тревога={} -> запись №{} (всего: {})"
              .format(t, h, alarm, entry, sent))
    except OSError as e:
        print("Ошибка:", e)
    time.sleep(INTERVAL)
