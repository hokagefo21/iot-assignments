-- Миграция 001: таблицы устройств и показаний датчиков
-- СУБД: SQLite (для PostgreSQL замените INTEGER PRIMARY KEY AUTOINCREMENT на SERIAL PRIMARY KEY
-- и DATETIME на TIMESTAMPTZ)
-- Применить вручную: sqlite3 iot.db < migrations/001_init.sql
-- (приложение создаёт эти же таблицы само при первом запуске)

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS devices (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR(100) NOT NULL,
    type        VARCHAR(50)  NOT NULL,
    location    VARCHAR(100),
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sensor_readings (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id    INTEGER      NOT NULL,
    sensor_type  VARCHAR(50)  NOT NULL,
    value        REAL         NOT NULL,
    unit         VARCHAR(20),
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    -- связь device -> readings (один ко многим); при удалении устройства удаляются и его показания
    FOREIGN KEY (device_id) REFERENCES devices (id) ON DELETE CASCADE
);

-- Индекс ускоряет выборку истории показаний одного устройства
CREATE INDEX IF NOT EXISTS ix_sensor_readings_device_id ON sensor_readings (device_id);
