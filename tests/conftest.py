# """Fixtures compartidas por todos los tests (versión del capítulo 9).
# El capítulo 11 reemplaza este archivo completo para añadir la fixture
# `client` de la API.
# """

# import pytest
# from langchain_core.embeddings import DeterministicFakeEmbedding
# from langchain_core.vectorstores import InMemoryVectorStore

# from src.domain.documents import Chunk
# from src.repositories.chunks import VectorChunkRepository

# @pytest.fixture
# def vector_store() -> InMemoryVectorStore:
#     """Base vectorial en memoria con embeddings falsos: mismo texto = mismo vector."""
#     return InMemoryVectorStore(embedding=DeterministicFakeEmbedding(size=256))

# @pytest.fixture
# def empty_repo(vector_store):
#     return VectorChunkRepository(vector_store) #el repositorio real sobre la base falsa

# @pytest.fixture
# def repo(empty_repo):
#     empty_repo.add(
#         [
#             Chunk("Las vacaciones son 15 dias habiles al año.",
#                   source="rrhh.pdf", page=2),
#             Chunk("El horario es de 9 a 18 horas.", source="rrhh.pdf", page=1)
#         ]
#     )
#     return empty_repo
"""Fixtures compartidas por todos los tests (versión final, capítulo 11)."""
import pytest
from fastapi.testclient import TestClient
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.vectorstores import InMemoryVectorStore
from langgraph.checkpoint.memory import InMemorySaver

from src.api.main import app
from src.container import get_agent_service, get_ask_service, get_ingest_service
from src.domain.documents import Chunk
from src.repositories.chunks import VectorChunkRepository
from src.repositories.loader import load_bytes
from src.services.agent import AgentService
from src.services.ask import AskService
from src.services.ingest import IngestService
from tests.fakes import PRICES, fake_llm, with_usage


@pytest.fixture
def vector_store():
    """Base vectorial en memoria con embeddings falsos: mismo texto = mismo vector."""
    return InMemoryVectorStore(embedding=DeterministicFakeEmbedding(size=256))

@pytest.fixture
def empty_repo(vector_store):
    return VectorChunkRepository(vector_store) # el repositorio real sobre la base falsa

@pytest.fixture
def repo(empty_repo):
    empty_repo.add(
        [
        Chunk("Las vacaciones son 15 días hábiles al año.",source="rrhh.pdf", page=2),
        Chunk("El horario es de 9 a 18 horas.", source="rrhh.pdf", page=1),
        ]
    )
    return empty_repo
@pytest.fixture
def client(repo):
    """API completa con servicios armados a mano: sin red, sin claves, sin costo."""
    def ask_service(): # uno por petición: el modelo falso gasta cada respuesta al darla
        return AskService(repo, fake_llm(with_usage("15 días [1][2]", 1200, 300)), PRICES)
    
    agent = AgentService(fake_llm("Hola", "Hola de nuevo"), [], InMemorySaver(), PRICES)
    app.dependency_overrides[get_ingest_service] = lambda: IngestService(load_bytes, repo)
    app.dependency_overrides[get_ask_service] = ask_service
    app.dependency_overrides[get_agent_service] = lambda: agent
    yield TestClient(app)
    app.dependency_overrides.clear()