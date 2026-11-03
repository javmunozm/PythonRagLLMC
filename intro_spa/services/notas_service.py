"""Aplicación: los casos de uso. Orquesta dominio y repositorio; no sabe de
HTTP ni de SQL."""

from intro_spa.domain.notas import (
    Nota, 
    NotaNoEncontrada,
    RepositorioNotas,
    limpiar_teto)

class NotasSerice:
    def __init__(self, repo: RepositorioNotas) -> None: # Recibe la interfaz, no una clase concreta
        self._repo = repo

    def listar(self) -> list[Nota]:
        return self._repo.listar()

    def crear(self, texto: str) -> Nota:
        return self._repo.agregar(limpiar_teto(texto))

    def borrar(self, nota_id: int) -> None:
        if not self._repo.borrar(nota_id):
            raise NotaNoEncontrada(f"No existe la nota {nota_id}")