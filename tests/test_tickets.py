import pytest
from langchain_core.messages import AIMessage
from pydantic import ValidationError

from src.domain.tickets import Ticket
from src.services.tickets import TicketService
from tests.fakes import fake_llm

def respuesta(**args) -> AIMessage:
    return AIMessage(content="", tool_calls=[{"name": "Ticket", "args":args, "id": "c1"}])

def test_ticket_valido():
    llm = fake_llm(respuesta(categoria="tecnico", urgencia=5, resumen="No puede entrar"))

def test_ticket_que_no_cumple_el_esquema_se_rechaza():
    llm = fake_llm(respuesta(categoria="urgente", urgencia=9, resumen="x"))
    with pytest.raises(ValidationError, match="categoria"):
        TicketService(llm).classify("texto")
