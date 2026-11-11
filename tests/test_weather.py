import httpx
import pytest

from src.clients.weather import current_temperature
from src.domain.weather import WeatherError
from src.scripts import clima
from src.services.weather import weather_report


def fake_api(request: httpx.Request) -> httpx.Response:
    """Responde como open-meteo, sin llamar a la api"""
    assert request.url.path == "/v1/forecast"
    assert request.url.params["current"] == "temperature_2m"
    return httpx.Response(200, json={"current": {"temperature_2m": 18.5}})


@pytest.fixture  # constructor
def http():
    with httpx.Client(base_url="https://api.test/v1", transport=httpx.MockTransport(fake_api)) as c:
        yield c  # no se que es yield, me imagino como un falso return para eliminar


def test_cliente_de_clima(http):
    assert current_temperature(-33.45, -70.66, client=http) == 18.5


@pytest.mark.parametrize(
    # [Theory] + [InlineData]: un test, varios casos
    "respuesta",
    [httpx.Response(503), httpx.Response(200, json={"otra": "forma"}), httpx.Response(200)],
)
def test_cliente_clima_traduce_sus_fallos_a_un_error_de_dominio(respuesta):
    transport = httpx.MockTransport(lambda request: respuesta)
    with (
        httpx.Client(base_url="https://api.test/1", transport=transport) as http,
        pytest.raises(WeatherError),
    ):
        current_temperature(0, 0, client=http)


def test_clima_acepta_tildes_y_mayusculas():
    def siempre_18(lat, lon):
        return 18.5

    assert weather_report("Chillán", siempre_18) == "18.5 °C en Chillán"
    assert weather_report(" CONCEPCIÓN ", siempre_18).startswith("18.5")


def test_clima_ciudad_desconocida():
    assert "No conozco" in weather_report("Lima", lambda lat, lon: 18.5)


def test_clima_con_la_api_caida_devuelve_texto():
    def caida(lat, lon):
        raise WeatherError("sin red")

    assert "no esta disponible" in weather_report("Santiago", caida)


def test_script_de_consola(monkeypatch, capsys):
    monkeypatch.setattr(clima, "current_temperature", lambda lat, lon: 18.5)
    clima.main("Santiago")
    assert capsys.readouterr().out == "18.5 °C en Santiago\n"
