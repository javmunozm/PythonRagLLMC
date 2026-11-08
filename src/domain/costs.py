"""Dominio: cuánto cuesta una petición. El proveedor cobra por tokens de
entrada y de salida."""

from dataclasses import dataclass

@dataclass(frozen=True)
class Usage:
    """Lo que gasto un caso de uso: suma todas sus llamadas al LLM."""

    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0

@dataclass(frozen=True)
class Prices:
    """USD por millón de tokens del modelo configurado."""

    input_per_mtok: float
    output_per_mtok: float

    def cost(self, input_tokens: int, output_tokens: int) -> float:
        usd = (input_tokens * self.input_per_mtok + output_tokens * self.output_per_mtok)/ 1e6
        return round(usd, 6)