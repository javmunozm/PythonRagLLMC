"""Dominio: qué ciudades conoce el asistente y qué necesita para saber su
temperatura."""

import unicodedata
from collections.abc import Callable

CITIES = {
    "santiago": (-33.45, -70.66),
    "valparaiso": (-33.05, -71.62),
    "concepcion": (-36.83, -73.05),
    "chillan": (-36.61, -72.10),
}


class WeatherError(RuntimeError):
    "El servicio de clima fallo, no resspondio o respondio algo inesperado"


# Contrato: (latitud, longitud) -> ºC, o lanza weatherError, lo cumple clients/weather.py
TemperatureReader = Callable[[float, float], float]


def normalize(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().strip().lower()


def find_city(name: str) -> tuple[float, float] | None:
    return CITIES.get(normalize(name))
