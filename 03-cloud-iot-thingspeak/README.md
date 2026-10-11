# Практическая работа. Интеграция IoT-устройства с облачной платформой

- `Практическая_Облако_IoT_Кайназар.docx` - заполненный бланк (части 1-4).
- `wokwi/3.2-3.3-thingspeak/main.py` - отправка температуры, влажности и тревоги (field1-field3) в ThingSpeak каждые 20 с.
- `wokwi/3.4-thingspeak-mqtt/main.py` - то же + приём команд `pump_on` / `pump_off` из топика `college/kainazar/cmd`.

## Запуск

1. ThingSpeak: New Channel «Теплица_Кайназар», поля Field 1 «Температура», Field 2 «Влажность», Field 3 «Тревога». Скопируйте Write API Key.
2. Wokwi: New Project → ESP32 → MicroPython, вставьте `main.py` и `diagram.json`.
3. Добавьте в проект файл `config.py` (по образцу `config.example.py`) со своим ключом. Ключ не коммитьте: `config.py` в `.gitignore`.
4. Для 3.4: в HiveMQ WebSocket Client подключитесь к broker.hivemq.com, опубликуйте `pump_on` в `college/kainazar/cmd`.
