"""Dominio: la entidad, sus reglas y el contrato del repositorio. No importa
nada de fuera."""

from dataclasses import dataclass
from typing import Protocol

LARGO_MAXIMO = 200

class NotaInvalida(ValueError):
    """El texto no cumple la regla de negocio."""

class NotaNoEncontrada(LookupError):
    '''No existe una nota con ese id.'''

@dataclass(frozen=True)
class Nota: #la entidad: tiene identidad (id)
    id: int
    texto: str

def limpiar_teto(texto: str) -> str:
    '''Regla de negocio: una nota tiene texto, sin espacios sobrantes y de hasta 200 caracteres.'''
    texto = texto.strip()
    if not texto or len(texto) > LARGO_MAXIMO:
        raise NotaInvalida(f"La nota debe tener entre 1 y {LARGO_MAXIMO} caracteres")
    return texto

class RepositorioNotas(Protocol): # la interfaz la define el dominio; la implementa infraestructura
    def listar(self) -> list[Nota]: ...
    def agregar(self, texto: str) -> Nota: ...
    def borrar(self, nota_id: int) -> bool: ...
