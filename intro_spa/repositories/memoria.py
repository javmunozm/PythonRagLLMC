"""Infraestructura: dónde se guardan las notas. Hoy en memoria; mañana, otra
clase con SQL."""

from itertools import count

from intro_spa.domain.notas import Nota

class RepositorioNotasEnMemoria: #cumple repositorioNotas sin heredar de el (Protocol)
    def __init__(self) -> None:
        self._notas: dict[int, Nota] = {}
        self._ids = count(1)

    def listar(self) -> list[Nota]:
        return list(self._notas.values())

    def agregar(self, texto: str) -> Nota:
        nota = Nota(id=next(self._ids), texto=texto)
        self._notas[nota.id] = nota
        return nota

    def borrar(self, nota_id: int) -> bool:
        return self._notas.pop(nota_id, None) is not None