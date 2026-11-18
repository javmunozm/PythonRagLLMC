import httpx
import pytest
from langchain_core.exceptions import ModelError
from langchain_openai import OpenAIEmbeddings

from src.api.errors import to_http
from tests.fakes import broken_embeddings, broken_llm


def caida(request):
    raise httpx.ConnectError("sin red")


def lenta(request):
    raise httpx.ReadTimeout("lenta")


FALLOS = [
    (lambda r: httpx.Response(429, json={"error": {"message": "rate limit"}}), 429),
    (lambda r: httpx.Response(401, json={"error": {"message": "bad key"}}), 502),
    (lambda r: httpx.Response(404, json={"error": {"message": "no model"}}), 502),
    (lambda r: httpx.Response(500, json={"error": {"message": "boom"}}), 502),
    (caida, 503),
    (lenta, 504),
]


@pytest.mark.parametrize(("handler", "status"), FALLOS)
def test_cada_fallo_del_proveedor_tiene_su_codigo(handler, status):
    with pytest.raises(ModelError) as error:  # la clase base común a todos los proveedores
        broken_llm(handler).invoke("hola")
    assert to_http(error.value)[0] == status


@pytest.mark.parametrize(("handler", "status"), FALLOS)
def test_los_embeddings_tambien_tienen_su_codigo(handler, status):
    with pytest.raises(Exception) as error:  # los embeddings lanzan las excepciones del SDK
        broken_embeddings(handler).embed_query("hola")
    assert to_http(error.value)[0] == status


def test_conexion_rechazada_de_verdad_da_503():
    """Sin red simulada: el SDK de openai usa su propio cliente HTTP (httpx2)."""
    embeddings = OpenAIEmbeddings(
        model="m",
        api_key="sk-test",
        base_url="http://127.0.0.1:9/v1",  # puerto cerrado en tu propio equipo: rechaza al instante
        max_retries=0,
        check_embedding_ctx_length=False,
    )
    with pytest.raises(Exception) as error:
        embeddings.embed_query("hola")
    assert to_http(error.value)[0] == 503
