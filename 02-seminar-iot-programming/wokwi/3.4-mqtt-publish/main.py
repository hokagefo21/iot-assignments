# Задание 3.4. Отправка температуры в MQTT
# ESP32 через Wi-Fi Wokwi-GUEST каждые 5 с публикует температуру DHT22
# на broker.hivemq.com в топик college/kainazar/temp
import network
import time
import dht
import machine
import ubinascii
from machine import Pin
from umqtt.simple import MQTTClient

BROKER = "broker.hivemq.com"
TOPIC = b"college/kainazar/temp"
# Уникальный Client ID из серийного номера чипа
CLIENT_ID = b"esp32-kainazar-" + ubinascii.hexlify(machine.unique_id())

sensor = dht.DHT22(Pin(4))

# --- Wi-Fi ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("Wokwi-GUEST", "")
print("Подключение к Wi-Fi", end="")
while not wlan.isconnected():
    print(".", end="")
    time.sleep(0.1)
print(" готово:", wlan.ifconfig()[0])

# --- MQTT ---
def mqtt_connect():
    client = MQTTClient(CLIENT_ID, BROKER, port=1883, keepalive=60)
    client.connect()
    print("Подключено к MQTT-брокеру", BROKER)
    return client

client = mqtt_connect()

while True:
    try:
        sensor.measure()
        t = sensor.temperature()
        payload = "{:.1f}".format(t)
        client.publish(TOPIC, payload)
        print("Отправлено в", TOPIC.decode(), ":", payload)
    except OSError as e:
        # обрыв связи или ошибка датчика: переподключаемся
        print("Ошибка:", e, "- переподключение")
        time.sleep(2)
        try:
            client = mqtt_connect()
        except OSError:
            pass
    time.sleep(5)
