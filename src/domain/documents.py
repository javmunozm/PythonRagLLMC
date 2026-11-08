"""Dominio: qué es un trozo de documento, cómo se identifica y qué contratos
necesita.
Python puro: aquí no se importa LangChain, FastAPI ni ninguna otra capa.
"""
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

SUPPORTED_FORMATS = {".pdf",".txt", ".md"}

class DocumentError(ValueError):
    """El archivo no se puede convertir en texto: formato, PDF dañado, escaneado, vacío."""
@dataclass(frozen=True)
class Chunk:
    """Un trozo de texto y de donde salio. Al cargar hay uno por pagina, al indexar se parten."""

    text: str
    source: str # nombre del archivo
    page: int | None = None 

    @property
    def label(self) -> str:
        """Como se cita: 'nombre_documento.pdf p.2' o politica.txt"""
        return self.source if self.page is None else f"{self.source} p.{self.page}"


def chunk_ids(chunks: list[Chunk]) -> list[str]:
    """Id estable por trozo (archivo:pagina:n): reindexar un archivo lo reemplaza, no lo duplica."""
    seen: Counter[str] = Counter()
    ids = []
    for chunk in chunks:
        key = f"{chunk.source}:{chunk.page or 0}"
        ids.append(f"{key}:{seen[key]}")
        seen[key] += 1
    return ids

# --- Contratos: el dominio dice Que necesita; infraestructura decide COMO ---
# Un contrato de una sola operación es una función: (nombre, contenido) -> trozos.
# En C# sería un Func<string, byte[], List<Chunk>>. Lo cumple repositories/loader.py

DocumentReader = Callable[[str, bytes], list[Chunk]]

class ChunkRepository(Protocol): #lo cumple repositories/chunks.py
    def add(self, chunks: list[Chunk]) -> None: ...
    def search(self, query: str, k: int) -> list[Chunk]: ...
    
