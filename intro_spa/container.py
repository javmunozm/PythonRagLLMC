"""Une las capas: el único archivo que elige las clases concretas (como
Program.cs)."""

from functools import lru_cache

from intro_spa.repositories.memoria import RepositorioNotasEnMemoria
from intro_spa.services.notas_service import NotasSerice

@lru_cache #singleton, como AddSingleton
def get_service() -> NotasSerice:
    return NotasSerice(RepositorioNotasEnMemoria())
