"""Fixtures compartidas por todos los tests (versión del capítulo 9).
El capítulo 11 reemplaza este archivo completo para añadir la fixture
`client` de la API.
"""

import pytest
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.vectorstores import InMemoryVectorStore

from src.domain.documents import Chunk
from src.repositories.chunks import VectorChunkRepository

@pytest.fixture
def vector_store() -> InMemoryVectorStore:
    """Base vectorial en memoria con embeddings falsos: mismo texto = mismo vector."""
    return InMemoryVectorStore(embedding=DeterministicFakeEmbedding(size=256))

@pytest.fixture
def empty_repo(vector_store):
    return VectorChunkRepository(vector_store) #el repositorio real sobre la base falsa

@pytest.fixture
def repo(empty_repo):
    empty_repo.add(
        [
            Chunk("Las vacaciones son 15 dias habiles al año.",
                  source="rrhh.pdf", page=2),
            Chunk("El horario es de 9 a 18 horas.", source="rrhh.pdf", page=1)
        ]
    )
    return empty_repo