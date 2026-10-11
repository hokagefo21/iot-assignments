import network, time

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("Wokwi-GUEST", "")
print("Подключение к Wi-Fi", end="")
while not wlan.isconnected():
    print(".", end="")
    time.sleep(0.1)
print(" готово:", wlan.ifconfig()[0])

# ---- Задание 3.4: ThingSpeak (телеметрия) + MQTT (команды насосу) ----
import dht
import machine
import ubinascii
import urequests
from machine import Pin
from umqtt.simple import MQTTClient

try:
    from config import WRITE_API_KEY
except ImportError:
    WRITE_API_KEY = "XXXXXXXXXXXXXXXX"    # вставьте свой Write API Key

TS_URL = "https://api.thingspeak.com/update"
SEND_EVERY_MS = 20000
PING_EVERY_MS = 30000
ALARM_T = 30.0

BROKER = "broker.hivemq.com"
CMD_TOPIC = b"college/kainazar/cmd"
CLIENT_ID = b"esp32-kainazar-" + ubinascii.hexlify(machine.unique_id())

sensor = dht.DHT22(Pin(4))
pump = Pin(2, Pin.OUT)                     # светодиод изображает насос
pump.value(0)


def on_message(topic, msg):
    cmd = msg.decode().strip().lower()
    if cmd == "pump_on":
        pump.value(1)
        print("Команда pump_on: насос ВКЛЮЧЁН")
    elif cmd == "pump_off":
        pump.value(0)
        print("Команда pump_off: насос ВЫКЛЮЧЕН")
    else:
        print("Неизвестная команда:", cmd)


def mqtt_connect():
    c = MQTTClient(CLIENT_ID, BROKER, port=1883, keepalive=60)
    c.set_callback(on_message)
    c.connect()
    c.subscribe(CMD_TOPIC)                 # только свой топик, а не "#"
    print("MQTT: подписка на", CMD_TOPIC.decode())
    return c


def send_to_thingspeak():
    sensor.measure()
    t = sensor.temperature()
    h = sensor.humidity()
    alarm = 1 if t > ALARM_T else 0
    r = urequests.get("{}?api_key={}&field1={:.1f}&field2={:.1f}&field3={}"
                      .format(TS_URL, WRITE_API_KEY, t, h, alarm))
    entry = r.text.strip()
    r.close()
    print("t={:.1f} C h={:.1f} % тревога={} -> запись №{}"
          .format(t, h, alarm, entry))


client = mqtt_connect()
last_send = time.ticks_ms() - SEND_EVERY_MS    # первая отправка сразу
last_ping = time.ticks_ms()

while True:
    try:
        client.check_msg()                 # не блокирует: проверяет новые команды
        now = time.ticks_ms()
        if time.ticks_diff(now, last_send) >= SEND_EVERY_MS:
            last_send = now
            try:
                send_to_thingspeak()
            except OSError as e:           # ошибка HTTP/датчика не рвёт MQTT
                print("ThingSpeak/DHT22:", e)
        if time.ticks_diff(now, last_ping) >= PING_EVERY_MS:
            last_ping = now
            client.ping()                  # держим соединение с брокером
    except OSError as e:
        print("Ошибка:", e, "- переподключение к MQTT")
        time.sleep(2)
        try:
            client = mqtt_connect()
        except OSError:
            pass
    time.sleep_ms(100)
