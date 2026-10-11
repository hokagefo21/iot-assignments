"""Правило автоматизации для сценария «Умная теплица».

Одно правило: если температура выше порога, API возвращает предупреждение
и команду включить вентилятор. Ровно 30 °C считается нормой (строго больше).
"""
TEMPERATURE_THRESHOLD = 30.0


def check_rules(sensor_type: str, value: float) -> tuple[str | None, str | None]:
    """Возвращает (warning, action). Если всё в норме, оба значения None."""
    if sensor_type.lower() == "temperature" and value > TEMPERATURE_THRESHOLD:
        return "High temperature", "TURN_ON_FAN"
    return None, None
