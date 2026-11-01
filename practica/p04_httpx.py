import asyncio

import httpx

URL = "https://api.open-meteo.com/v1/forecast"
CIUDADES = {
    "Santiago": (-33.45, -70.66),
    "Valparaíso": (-33.05, -71.62),
    "Chillán": (-36.61, -72.10),
}


def una_peticion() -> None:
    params = {"latitude": -33.45, "longitude": -70.66, "current": "temperature_2m"}
    try:
        r = httpx.get(URL, params=params, timeout=10)
        r.raise_for_status()  # lanza HTTPStatusError si es 4xx/5xx (EnsureSuccessStatusCode)
        print(r.status_code, r.json()["current"]["temperature_2m"], "°C")
    except httpx.HTTPStatusError as e:  # respondio, pero con 4xx/5xx
        print("La API respondio", e.response.status_code)
    except httpx.TimeoutException:  # no respondio a tiempo
        print("Timeout")
    except httpx.RequestError as e:  # DNS, conexion, proxy...
        print("Error de red:", type(e).__name__)


async def temperatura(client: httpx.AsyncClient, ciudad: str) -> str:
    lat, lon = CIUDADES[ciudad]
    params = {"latitude": lat, "longitude": lon, "current": "temperature_2m"}
    r = await client.get("/forecast", params=params)
    r.raise_for_status()
    return f"{ciudad}: {r.json()['current']['temperature_2m']} °C"


async def en_paralelo() -> None:
    async with httpx.AsyncClient(
        base_url="https://api.open-meteo.com/v1", timeout=10
    ) as client:  # las peticiones salen a la vez (Promise.all / Task.WhenAll)
        resultados = await asyncio.gather(*(temperatura(client, c) for c in CIUDADES))
        print(resultados)


if __name__ == "__main__":
    una_peticion()
    try:
        asyncio.run(en_paralelo())
    except httpx.HTTPError as e:
        print("Sin red para la version async:", type(e).__name__)
