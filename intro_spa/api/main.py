"""API: traduce HTTP a casos de uso y errores de dominio a códigos. Ninguna
regla vive aquí."""

from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from intro_spa.api.schemas import NotaNueva, NotaOut
from intro_spa.container import get_service
from intro_spa.domain.notas import NotaInvalida, NotaNoEncontrada
from intro_spa.services.notas_service import NotasSerice

app = FastAPI(title="Notas")

ServiceDep = Annotated[NotasSerice, Depends(get_service)]

@app.get("/api/notas")
def listar(service: ServiceDep) -> list[NotaOut]:
    return [NotaOut(id=nota.id, texto=nota.texto) for nota in service.listar()]

@app.post("/api/notas", status_code=201)
def crear(body: NotaNueva, service: ServiceDep) -> NotaOut:
    try:
        nota = service.crear(body.texto)
    except NotaInvalida as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return NotaOut(id=nota.id, texto=nota.texto)

@app.delete("/api/notas/{nota_id}", status_code=204)
def borrar(nota_id: int, service: ServiceDep) -> None:
    try:
        service.borrar(nota_id)
    except NotaNoEncontrada as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

# Todo lo que no sea /api/... se busca en web/ ("/" entrega index.html)
WEB_DIR = Path(__file__).resolve().parent.parent / "web"
app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="spa")