# """Une las capas: el único archivo que elige las clases concretas (como
# Program.cs).
# Versión del capítulo 9 (RAG). El capítulo 10 reemplaza este archivo completo.
# """
# from functools import lru_cache

# from langchain_core.language_models import BaseChatModel

# from src.clients.llm import (
#     get_chat_model,
#     get_embeddings,
# )
# from src.config import get_settings
# from src.domain.costs import Prices
# from src.domain.documents import ChunkRepository
# from src.repositories.chunks import (
#     VectorChunkRepository,
#     get_vector_store,
# )
# from src.repositories.loader import load_bytes
# from src.services.ask import AskService
# from src.services.ingest import IngestService

# @lru_cache #singleton, como AddSingleton in C#
# def get_repo() -> ChunkRepository:
#     return VectorChunkRepository(get_vector_store(get_embeddings()))

# @lru_cache
# def get_llm() -> BaseChatModel:
#     return get_chat_model()

# def get_prices() -> Prices:
#     s = get_settings()
#     return Prices(s.price_input_per_mtok, s.price_output_per_mtok)

# @lru_cache
# def get_ingest_service() -> IngestService:
#     return IngestService(load_bytes, get_repo())

# @lru_cache
# def get_ask_service() -> AskService:
#     return AskService(get_repo(), get_llm(), get_prices())
"""Une las capas: el único archivo que elige las clases concretas (como
Program.cs).
La API y los scripts de consola piden aquí sus servicios; los tests
reemplazan estas funciones.
"""

from functools import lru_cache

from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.memory import InMemorySaver

from src.clients.llm import get_chat_model, get_embeddings
from src.clients.weather import current_temperature
from src.config import get_settings
from src.domain.costs import Prices
from src.domain.documents import ChunkRepository
from src.repositories.chunks import VectorChunkRepository, get_vector_store
from src.repositories.loader import load_bytes
from src.services.agent import AgentService
from src.services.ask import AskService
from src.services.ingest import IngestService
from src.services.tools import make_search_tool, make_weather_tool

@lru_cache #singleton
def get_repo() -> ChunkRepository:
    return VectorChunkRepository(get_vector_store(get_embeddings()))

@lru_cache
def get_llm() -> BaseChatModel:
    return get_chat_model()

def get_prices() -> Prices:
    s = get_settings()
    return Prices(s.price_input_per_mtok, s.price_output_per_mtok)

@lru_cache
def get_ingest_service() -> IngestService:
    return IngestService(load_bytes, get_repo())

@lru_cache
def get_ask_service() -> AskService:
    return AskService(get_repo(), get_llm(), get_prices())

@lru_cache
def get_agent_service() -> AgentService:
    tools = [make_search_tool(get_repo()),
             make_weather_tool(current_temperature)
             ]
    memory = InMemorySaver() #las conversaciones viven en la memoria, pero se pierden al reiniciar
    return AgentService(get_llm(), tools, memory, get_prices())