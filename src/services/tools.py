"""Las herramientas del agente. Cada fábrica recibe su dependencia y devuelve
la tool lista."""

from langchain.tools import tool

from src.domain.answers import data_block
from src.domain.documents import ChunkRepository
from src.domain.weather import TemperatureReader
from src.services.weather import weather_report

def make_search_tool(repo: ChunkRepository, k: int =4):
    @tool
    def buscar_documentos(consulta: str) -> str:
        """Busca en los documentos internos indexados. Usala para preguntas sobre su cotenido."""
        chunks = repo.search(consulta, k)
        return data_block(chunks) if chunks else "No se encontraron documentos relevantes."
    return buscar_documentos

def make_weather_tool(get_temperature: TemperatureReader):
    @tool
    def clima_actual(ciudad: str) -> str:
        """Temperatura actual de una ciudad de Chile (Santiago,Valparaiso, Chillan o Concepcion)"""
        return weather_report(ciudad, get_temperature) 
    return clima_actual

