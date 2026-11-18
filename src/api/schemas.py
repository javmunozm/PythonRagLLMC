"""Los contratos HTTP: qué acepta y qué devuelve la API. Pydantic valida la entrada."""

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid") # un campo desconocido = error 422

class AskRequest(StrictModel):
    question: str = Field(min_length=3, max_length=2000)
    k: int = Field(default=4, ge=1, le=10)

class UsageOut(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0

class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    grounded: bool # True si la respuesta cita al menos un trozo recuperado
    usage: UsageOut

class AgentRequest(StrictModel):
    message: str = Field(min_length=1, max_length=2000)
    thread_id: str | None = Field(default=None, pattern=r"^[A-Za-z0-9_-]{1,64}$")

class AgentResponse(BaseModel):
    answer: str
    thread_id: str
    usage: UsageOut

class IngestResponse(BaseModel):
    files: list[str]
    chunks: int