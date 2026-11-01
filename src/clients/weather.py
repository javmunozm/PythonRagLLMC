"""Infraestructura: la API pública de Open-Meteo. Cumple el contrato
TemperatureReader."""

import httpx

from src.domain.weather import WeatherError

BASE_URL = "https://api.open-meteo.com/v1"


def current_temperature(lat: float, lon: float, client: httpx.Client | None = None) -> float:
    http = client or httpx.Client(base_url=BASE_URL, timeout=10)
    try:
        params = {"latitude": lat, "longitude": lon, "current": "temperature_2m"}
        r = http.get("/forecast", params=params)
        r.raise_for_status()
        return r.json()["current"]["temperature_2m"]
    except (httpx.HTTPError, KeyError, ValueError) as e:
        raise WeatherError(f"Open-meteo no respondio bien ({type(e).__name__})") from e
    finally:
        if client is None:
            http.close()
