"""DTOs: lo que entra y sale por HTTP."""

from pydantic import BaseModel

class NotaNueva(BaseModel): #lo que envia el navegador get
    texto: str

class NotaOut(BaseModel): #lo que devuelve la api
    id: int
    texto: str