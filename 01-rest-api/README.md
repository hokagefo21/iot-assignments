# IoT Greenhouse API

Простой REST API для IoT-системы «Умная теплица»: принимает показания виртуального датчика, сохраняет их в базу данных и отдаёт историю измерений.

**Стек:** Python 3.10+, FastAPI, SQLAlchemy, SQLite.
**Сценарий:** умная теплица, температура (правило: выше 30 °C включить вентилятор).

## Путь данных

```
Postman (виртуальный датчик) -> POST /api/devices/{id}/readings -> FastAPI (валидация + правило) -> SQLite
                                                                                                   |
Postman (клиент)            <- GET /api/devices/{id}/readings  <- JSON-ответ <---------------------+
```

1. Postman отправляет JSON с показанием, как это делал бы ESP32.
2. FastAPI проверяет тело запроса по схеме (`app/schemas.py`). Если данные неверные, сразу возвращается 422.
3. API проверяет, что устройство существует. Если нет, возвращается 404.
4. Показание сохраняется в таблицу `sensor_readings` со ссылкой на устройство (`device_id`).
5. Правило автоматизации (`app/rules.py`) смотрит на значение и добавляет в ответ `warning` и `action`.
6. GET-запрос читает сохранённые записи из БД и возвращает их в JSON.

## Запуск

```bash
python -m venv venv
# Windows: venv\Scripts\activate    Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API будет доступен на http://127.0.0.1:8000, интерактивная документация (Swagger) на http://127.0.0.1:8000/docs.
База `iot.db` и таблицы создаются автоматически при первом запуске.

Автотесты (повторяют весь сценарий защиты):

```bash
pytest -q
```

## Структура базы данных

Файл миграции: [`migrations/001_init.sql`](migrations/001_init.sql)

| devices | | sensor_readings | |
|---|---|---|---|
| id | PK | id | PK |
| name | текст, обязательно | device_id | FK -> devices.id |
| type | текст, обязательно | sensor_type | текст, обязательно |
| location | текст | value | число, обязательно |
| created_at | дата | unit | текст |
| | | created_at | дата |

Связь **один-ко-многим**: одно устройство имеет много показаний. При удалении устройства его показания удаляются каскадно.

## Endpoint-ы

| Метод | URL | Что делает | Коды |
|---|---|---|---|
| POST | `/api/devices` | создать устройство | 201, 422 |
| GET | `/api/devices` | список устройств | 200 |
| GET | `/api/devices/{id}` | одно устройство | 200, 404 |
| POST | `/api/devices/{id}/readings` | сохранить показание + проверить правило | 201, 404, 422 |
| GET | `/api/devices/{id}/readings?limit=100` | история показаний (новые сверху) | 200, 404 |

### Примеры

Создать устройство:

```json
POST /api/devices
{ "name": "Temperature Sensor #1", "type": "temperature", "location": "Greenhouse, sector 1" }
```

Отправить показание:

```json
POST /api/devices/1/readings
{ "sensor_type": "temperature", "value": 32.1, "unit": "C" }
```

Ответ, если сработало правило:

```json
{
  "saved": true,
  "reading": { "id": 2, "device_id": 1, "sensor_type": "temperature", "value": 32.1, "unit": "C", "created_at": "..." },
  "warning": "High temperature",
  "action": "TURN_ON_FAN"
}
```

## Правило автоматизации

`temperature > 30` -> `warning: "High temperature"`, `action: "TURN_ON_FAN"`.
Ровно 30 °C считается нормой. Для других типов датчиков правило не срабатывает.

## Валидация и ошибки

| Ситуация | Ответ | HTTP |
|---|---|---|
| Запрос корректный | JSON с записью | 200 / 201 |
| Устройство не найдено | `{"detail": "Device 99999 not found"}` | 404 |
| Нет `sensor_type`, пустой `sensor_type`, `value` не число (в том числе `"25.5"` строкой) | `{"message": "Validation failed", "errors": [...]}` | 422 |

## Демонстрация в Postman

Импортируйте `postman/IoT_Greenhouse_API.postman_collection.json` (Import -> File) и выполняйте запросы по порядку 1-8.
Запрос 1 сам запоминает `id` созданного устройства в переменную `deviceId`, остальные используют её.
В каждом запросе есть тесты (вкладка Test Results), поэтому можно нажать **Run collection** и показать, что всё зелёное.

Посмотреть, что показание сохранилось в БД:

```bash
sqlite3 iot.db "SELECT * FROM sensor_readings;"
```

или открыть `iot.db` в DB Browser for SQLite / DBeaver.

Пример вывода всего сценария лежит в [`demo-output.txt`](demo-output.txt).
