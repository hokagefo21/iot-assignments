"""Проверка таблицы из задания 2 и схемы из задания 6 без подключения к брокеру.

Используется та же функция сопоставления топиков, что и в библиотеке paho-mqtt.
Запуск: pip install paho-mqtt && python topic_match_check.py
"""
from paho.mqtt.client import topic_matches_sub

PREFIX = "lab/<ГРУППА>/<N>/"

# ---- Задание 2 ----
topics = {
    "A": "greenhouse/sector1/air/temperature",
    "B": "greenhouse/sector2/air/temperature",
    "C": "greenhouse/sector1/soil/humidity",
    "D": "greenhouse/sector1/irrigation/state",
    "E": "greenhouse/outdoor/soil/temperature",
}
subs = [
    "greenhouse/#",
    "greenhouse/+/air/temperature",
    "greenhouse/sector1/+",
    "greenhouse/+/+/temperature",
    "greenhouse/sector1/#",
]
print("Задание 2")
for s in subs:
    got = [k for k, t in topics.items() if topic_matches_sub(PREFIX + s, PREFIX + t)]
    print(f"  {s:32} -> {', '.join(got) if got else 'ничего'}")

# ---- Задание 6 ----
scheme = {
    "t1": "telemetry/sector1/air/temperature",
    "t2": "telemetry/sector2/air/temperature",
    "st1": "telemetry/sector1/sensor/status",
    "cmd1": "command/sector1/irrigation/set",
    "cmd2": "command/sector2/irrigation/set",
}
agronomist = "telemetry/#"
controller2 = "command/sector2/irrigation/set"
print("\nЗадание 6")
for name, sub in [("панель агронома", agronomist), ("контроллер отсека 2", controller2)]:
    got = [k for k, t in scheme.items() if topic_matches_sub(PREFIX + sub, PREFIX + t)]
    print(f"  {name:20} ({sub}) получает: {', '.join(got)}")

assert not topic_matches_sub(PREFIX + controller2, PREFIX + scheme["cmd1"]), "контроллер видит чужие команды"
assert not any(topic_matches_sub(PREFIX + agronomist, PREFIX + scheme[c]) for c in ("cmd1", "cmd2"))
print("\nПроверка пройдена: контроллер отсека 2 не видит команды отсека 1, агроном не получает команды.")
