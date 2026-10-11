"""Автотесты: повторяют сценарий защиты из задания (пункты 1-7)."""
import os
import tempfile

# Отдельная временная БД для тестов, чтобы не трогать рабочую iot.db
_db_file = os.path.join(tempfile.mkdtemp(), "test.db")
os.environ["DATABASE_URL"] = f"sqlite:///{_db_file}"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


def make_client():
    return TestClient(app)


def create_device(client, **overrides):
    body = {"name": "Temperature Sensor #1", "type": "temperature", "location": "Greenhouse, sector 1"}
    body.update(overrides)
    r = client.post("/api/devices", json=body)
    assert r.status_code == 201, r.text
    return r.json()


def test_create_and_get_devices():
    with make_client() as client:
        device = create_device(client)
        assert device["id"] > 0 and device["created_at"]

        r = client.get("/api/devices")
        assert r.status_code == 200
        assert any(d["id"] == device["id"] for d in r.json())

        r = client.get(f"/api/devices/{device['id']}")
        assert r.status_code == 200
        assert r.json()["name"] == "Temperature Sensor #1"


def test_normal_reading_is_saved_and_returned_in_history():
    with make_client() as client:
        device = create_device(client)
        r = client.post(f"/api/devices/{device['id']}/readings",
                        json={"sensor_type": "temperature", "value": 24.5, "unit": "C"})
        assert r.status_code == 201
        body = r.json()
        assert body["saved"] is True
        assert body["warning"] is None and body["action"] is None

        r = client.get(f"/api/devices/{device['id']}/readings")
        assert r.status_code == 200
        history = r.json()
        assert len(history) == 1 and history[0]["value"] == 24.5


def test_automation_rule_threshold():
    with make_client() as client:
        device = create_device(client)
        url = f"/api/devices/{device['id']}/readings"

        hot = client.post(url, json={"sensor_type": "temperature", "value": 32.1, "unit": "C"}).json()
        assert hot["warning"] == "High temperature" and hot["action"] == "TURN_ON_FAN"

        # ровно 30 °C - норма, правило не срабатывает
        border = client.post(url, json={"sensor_type": "temperature", "value": 30, "unit": "C"}).json()
        assert border["action"] is None

        # высокое значение другого типа датчика правило не трогает
        other = client.post(url, json={"sensor_type": "humidity", "value": 80, "unit": "%"}).json()
        assert other["action"] is None


def test_device_not_found_returns_404():
    with make_client() as client:
        assert client.get("/api/devices/99999").status_code == 404
        assert client.get("/api/devices/99999/readings").status_code == 404
        r = client.post("/api/devices/99999/readings", json={"sensor_type": "temperature", "value": 20})
        assert r.status_code == 404


def test_validation_returns_422():
    with make_client() as client:
        device = create_device(client)
        url = f"/api/devices/{device['id']}/readings"

        bad_bodies = [
            {"value": 25},                                   # нет sensor_type
            {"sensor_type": "", "value": 25},                # пустой sensor_type
            {"sensor_type": "temperature", "value": "hot"},  # value не число
            {"sensor_type": "temperature", "value": "25.5"}, # число строкой тоже не принимаем
            {"sensor_type": "temperature"},                  # нет value
        ]
        for body in bad_bodies:
            r = client.post(url, json=body)
            assert r.status_code == 422, body
            assert r.json()["message"] == "Validation failed"

        assert client.post("/api/devices", json={"type": "temperature"}).status_code == 422

        # невалидные запросы ничего не записали в БД
        assert client.get(url).json() == []
