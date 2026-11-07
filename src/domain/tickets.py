"""Dominio: el esquema que el modelo debe llenar al clasificar un ticket."""
from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    )

class Ticket(BaseModel):
    """Clasificacion de un ticket de soporte."""

    categoria: Literal["facturacion", "tecnico", "otro"]
    urgencia: int = Field(ge=1, le=5, description="1 = baja, 5 = critica")
    resumen: str = Field(description="Una frase con el problema")