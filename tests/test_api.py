import json

import httpx
import pytest

from src.api.main import app
from src.container import get_ask_service
from src.domain.answers import NO_ANSWER
from src.services.ask import AskService
from tests.fakes import PRICES, broken_llm, fake_llm, tiny_pdf


def test_health_y_pagina(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert "<title>Asistente de documentos</title>" in client.get("/").text

def test_ask_devuelve_respuesta_fuentes_y_costo(client):
    r = client.post("/ask", json={"question": "¿Vacaciones?", "k": 2})
    assert r.status_code == 200
    assert r.json() == {
        "answer": "15 días [1][2]",
        "sources": ["rrhh.pdf p.1", "rrhh.pdf p.2"],
        "grounded": True,
        "usage": {"input_tokens": 1200, "output_tokens": 300, "cost_usd":0.00225},
    }
    assert len(r.headers["x-request-id"]) == 12

@pytest.mark.parametrize(
    "body",
    [
        {"question": "ab"},# menos de 3 caracteres
        {"question": "a" * 2001}, # mas de 2000
        {"question": "¿Vacaciones?", "k": 0},
        {"question": "¿Vacaciones?", "k": 11},
        {"question": "¿Vacaciones?", "rol": "admin"}, #campo desconocido
        {},
    ],
)
def test_ask_rechaza_entradas_fuera_de_limites(client, body): 
    assert client.post("/ask", json=body).status_code == 422

def test_ask_stream_envia_eventos_ndjson(client):
    r = client.post("/ask/stream", json={"question": "¿Vacaciones?", "k": 2})
    events = [json.loads(line) for line in r.text.splitlines()]
    assert "".join(e["text"] for e in events if e["type"] == "token") == "15 días [1][2]"
    assert events[-1]["type"] == "done"
    assert events[-1]["sources"] == ["rrhh.pdf p.1", "rrhh.pdf p.2"]
    assert events[-1]["grounded"] is True

def test_ingest_txt_y_pdf(client):
    files = [
        ("files", ("politica.txt", "Teletrabajo dos días por semana.", "text/plain")),
        ("files", ("rrhh2.pdf", tiny_pdf("Vacaciones: 15 dias"), "application/pdf")),
    ]
    r = client.post("/ingest", files=files)
    assert r.json() == {"files": ["politica.txt", "rrhh2.pdf"], "chunks": 2}

def test_ingest_dos_veces_no_duplica(client, vector_store):
    files = [("files", ("politica.txt", "Teletrabajo dos días por semana.", "text/plain"))]
    client.post("/ingest", files=files)
    client.post("/ingest", files=files)
    assert len(vector_store.store) == 3  # los 2 de la fixture + 1, no + 2


@pytest.mark.parametrize(
    ("name", "data", "status"),
    [
        ("x.exe", b"MZ", 400),
        ("roto.pdf", b"esto no es un pdf", 400),
        ("escaneado.pdf", tiny_pdf(""), 400),
        ("grande.txt", b"a" * (10 * 1024 * 1024 + 1), 413),
    ],
    ids=["exe", "pdf-roto", "pdf-escaneado", "grande"],  # sin ids, pytest usa los 10 MB como nombre
)
def test_ingest_rechaza_archivos_invalidos(client, name, data, status):
    r = client.post("/ingest", files=[("files", (name, data, "application/octet-stream"))])
    assert r.status_code == status
    assert name in r.json()["detail"]


def test_agent_sin_thread_id_crea_conversaciones_separadas(client):
    ana = client.post("/agent", json={"message": "Soy Ana"}).json()
    pedro = client.post("/agent", json={"message": "Soy Pedro"}).json()
    assert ana["answer"] == "Hola"
    assert ana["thread_id"] != pedro["thread_id"]


def test_agent_rechaza_thread_id_invalido(client):
    r = client.post("/agent", json={"message": "Hola", "thread_id": "../otro usuario"})
    assert r.status_code == 422


def caida(request):
    raise httpx.ConnectError("sin red")


def use_llm(repo, llm) -> None:
    """Cambia el modelo del servicio de preguntas para este test."""
    app.dependency_overrides[get_ask_service] = lambda: AskService(repo, llm, PRICES)


@pytest.mark.parametrize(
    ("handler", "status"),
    [
        (lambda r: httpx.Response(429, json={"error": {"message": "rate limit"}}), 429),
        (caida, 503),
    ],
)
def test_si_el_proveedor_falla_la_api_responde_json_claro(client, repo, handler, status):
    use_llm(repo, broken_llm(handler))
    r = client.post("/ask", json={"question": "¿Vacaciones?"})
    assert r.status_code == status
    assert "proveedor de IA" in r.json()["detail"]


def test_si_el_proveedor_falla_en_streaming_llega_un_evento_de_error(client, repo):
    use_llm(repo, broken_llm(caida))
    r = client.post("/ask/stream", json={"question": "¿Vacaciones?"})
    assert json.loads(r.text.splitlines()[-1])["type"] == "error"


def test_sin_documentos_responde_no_lo_se_sin_gastar(client, repo, vector_store):
    vector_store.delete(list(vector_store.store))  # deja la base vacía
    use_llm(repo, fake_llm())  # si se llamara al LLM, fallaría
    r = client.post("/ask", json={"question": "¿Vacaciones?"})
    assert r.json()["answer"] == NO_ANSWER
    assert r.json()["usage"]["cost_usd"] == 0