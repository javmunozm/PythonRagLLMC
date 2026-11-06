import httpx
import pytest

from src.clients.llm_http import LLMError, ask_gemini, ask_openai, post_json

OPENAI_OK = {
    "output": [
        {
            "type": "message",
            "content": [{"type": "output_text", "text": "Hola"}],
        }
    ]
}

GEMINI_OK = {
    "candidates": [
        {"content": {"parts": [{"text": "Hola"}]}}
    ]
}


def client_with(
    *responses,
) -> tuple[httpx.Client, list[httpx.Request], list[float]]:
    """Cliente cuya 'red' devuelve estas respuestas en orden. Anota peticiones y esperas."""
    pending, requests, waits = list(responses), [], []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        item = pending.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    return httpx.Client(transport=httpx.MockTransport(handler)), requests, waits


def ask(client: httpx.Client, waits: list[float]) -> str:
    """Llama a post_json con un sleep falso, que solo anota cuánto habría esperado."""
    data = post_json(
        client,
        "https://api.test/v1/responses",
        {},
        {"input": "x"},
        sleep=waits.append,
    )
    return data["output"][0]["content"][0]["text"]


def test_reintenta_tras_429_y_respeta_retry_after():
    limite = httpx.Response(429, headers={"retry-after": "7"})
    client, requests, waits = client_with(
        limite, httpx.Response(200, json=OPENAI_OK)
    )
    assert ask(client, waits) == "Hola"
    assert len(requests) == 2
    assert waits == [7.0]


def test_reintenta_tras_un_5xx():
    client, _, waits = client_with(
        httpx.Response(503), httpx.Response(200, json=OPENAI_OK)
    )
    assert ask(client, waits) == "Hola"
    assert waits == [1.0]


def test_red_caida_no_revienta_devuelve_error_claro():
    client, _, waits = client_with(*[httpx.ConnectError("sin red")] * 3)
    with pytest.raises(LLMError, match="3 intentos"):
        ask(client, waits)
    assert waits == [1.0, 2.0]  # espera creciente entre intentos


def test_clave_invalida_no_se_reintenta():
    client, requests, waits = client_with(httpx.Response(401))
    with pytest.raises(LLMError, match="Credenciales"):
        ask(client, waits)
    assert len(requests) == 1


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(400, text="modelo desconocido"),
        httpx.Response(200, text="<html>no es JSON"),
    ],
)
def test_otros_errores_cortan_sin_reintentar(response):
    client, requests, waits = client_with(response)
    with pytest.raises(LLMError):
        ask(client, waits)
    assert len(requests) == 1


def test_peticion_a_openai_y_a_azure():
    client, requests, _ = client_with(httpx.Response(200, json=OPENAI_OK))
    azure = "https://mi-recurso.openai.azure.com/openai/v1/"
    answer = ask_openai(
        client, "Di hola", api_key="k", model="mi-deployment", base_url=azure
    )
    assert answer == "Hola"
    assert (
        str(requests[0].url)
        == "https://mi-recurso.openai.azure.com/openai/v1/responses"
    )
    assert requests[0].headers["authorization"] == "Bearer k"


def test_peticion_a_gemini():
    client, requests, _ = client_with(httpx.Response(200, json=GEMINI_OK))
    assert (
        ask_gemini(client, "Di hola", api_key="k", model="gemini-3.5-flash")
        == "Hola"
    )
    assert (
        requests[0].url.path
        == "/v1beta/models/gemini-3.5-flash:generateContent"
    )
    assert requests[0].headers["x-goog-api-key"] == "k"


def test_respuesta_con_forma_inesperada_y_pregunta_vacia():
    client, _, _ = client_with(httpx.Response(200, json={"candidates": []}))
    with pytest.raises(LLMError, match="forma esperada"):
        ask_gemini(client, "Di hola", api_key="k", model="m")
    with pytest.raises(ValueError):
        ask_openai(client, "   ", api_key="k", model="m")