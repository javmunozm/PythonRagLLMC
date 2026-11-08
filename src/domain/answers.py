"""Dominio: cómo se le presentan los trozos al modelo y cuándo una respuesta
está fundamentada."""

import re 
from dataclasses import dataclass, field

from src.domain.costs import Usage
from src.domain.documents import Chunk

NO_ANSWER = "No lo se: la respuesta no esta en los documentos indexados."

@dataclass(frozen=True)
class Answer:
    text: str
    sources: list[str] = field(default_factory=list) #se aplica slo a las fuentes que cita el texto
    usage: Usage = Usage()

    @property
    def grounded(self) -> bool:
        """Fundamentada = cita al menos uno de los trozos recuperados."""
        return bool(self.sources)

def data_block(chunks: list[Chunk]) -> str:
    """Los trozos numeroados ([1] archivo p.N + texto) entre <documentos ></documentos>
    El numero es lo que cita el modelo, las etiquetas marcan donde empiezan y terminaan los datos.
    """
    parts = []
    for number, chunk in enumerate(chunks, start=1):
        text = re.sub(r"</?documentos>","", chunk.text)
        parts.append(f"[{number}] {chunk.label}\n{text}")
    return "<documentos>\n" + "\n\n".join(parts) + "\n</documentos>"

def cited_sources(text: str, chunks: list[Chunk]) -> list[str]:
    """Solo las fuentes citadas en la respuesta"""
    cited = {int(n) for n in re.findall(r"\[(\d+)\]", text)}
    return sorted({c.label for number, c in enumerate(chunks, start=1) if number in cited})

