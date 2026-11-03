import pytest
from fastapi.testclient import TestClient

from intro_spa.api.main import app
from intro_spa.container import get_service
from intro_spa.domain.notas import NotaInvalida, NotaNoEncontrada
from intro_spa.repositories.memoria import RepositorioNotasEnMemoria
from intro_spa.services.notas_service import NotasSerice

@pytest.fixture
def service():
    return NotasSerice(RepositorioNotasEnMemoria()) #un repositorio nuevo en cada test

def test_caso_de_uso_sin_http(service):
    nota = service.crear(" comprar pan ")
    assert (nota.id, nota.texto) == (1, "comprar pan") # la regla del dominio limpio el texto
    with pytest.raises(NotaInvalida):
        service.crear(" ")
    service.borrar(nota.id)
    with pytest.raises(NotaNoEncontrada):
        service.borrar(nota.id)

def test_api_traduce_errores_de_dominio_a_http(service):
    app.dependency_overrides[get_service] = lambda: service
    client = TestClient(app)
    assert client.post("/api/notas", json= {"texto": "hola"}).json() == {"id": 1, "texto": "hola"}
    assert client.post("/api/notas", json={"texto": "   "}).status_code == 422
    assert client.delete("/api/notas/99").status_code == 404
    assert "<title>Notas</title>" in client.get("/").text
    app.dependency_overrides.clear()