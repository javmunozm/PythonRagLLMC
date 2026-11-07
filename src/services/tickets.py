"""Caso de uso: clasificar un ticket de soporte con salida estructurada."""

from langchain_core.language_models import BaseChatModel

from src.domain.tickets import Ticket

class TicketService:
    def __init__(self, llm: BaseChatModel)-> None:
        self._classifier = llm.with_structured_output(Ticket) #el modelo llena el esquema
    
    def classify(self, texto: str) -> Ticket:
        """El modelo responde con JSON que cumple el esquema; Pydantic lo valida."""
        return self._classifier.invoke(texto)