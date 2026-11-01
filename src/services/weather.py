"""Caso de uso: decir con palabras qué temperatura hace en una ciudad."""

from src.domain.weather import TemperatureReader, WeatherError, find_city


def weather_report(city: str, get_temperature: TemperatureReader) -> str:
    """Siempre devuelve una frase: la temperatura o por que no se logro saber"""
    coords = find_city(city)
    if coords is None:
        return f"No conozco la ciudad {city}."
    try:
        return f"{get_temperature(*coords)} ºC en {city}"
    except WeatherError:
        return "El servicio de clima no esta disponible ahora."
