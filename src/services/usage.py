"""Cuenta los tokens que gasta un caso de uso y les pone precio."""

from langchain_core.callbacks import UsageMetadataCallbackHandler

from src.domain.costs import Prices, Usage

class UsageMeter:
    """Uno por peticion: se entrega como callback en cada llamada al llm y al final de el total"""

    def __init__(self, prices: Prices) -> None:
        self._prices = prices
        self._tracker = UsageMetadataCallbackHandler() #langchain le avisa tras cada llamada

    @property
    def callbacks(self) -> list[UsageMetadataCallbackHandler]:
        return [self._tracker]

    def total(self) -> Usage:
        calls = self._tracker.usage_metadata.values()
        tokens_in = sum(u.get("input_tokens", 0) for u in calls)
        tokens_out = sum(u.get("output_tokens", 0) for u in calls)
        return Usage(tokens_in, tokens_out,  self._prices.cost(tokens_in, tokens_out))