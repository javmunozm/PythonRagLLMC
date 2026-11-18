"""API: traduce HTTP a casos de uso y sus resultados a JSON. Ninguna regla vive aquí."""
import json
import logging
import time
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from src.api.errors import errors_as_http, to_http
from src.api.schemas import AgentRequest, AgentResponse, AskRequest, AskResponse, IngestResponse
from src.config import get_settings
from src.container import get_agent_service, get_ask_service, get_ingest_service
from src.domain.answers import Answer
from src.logging_config import setup_logging
from src.services.agent import AgentService
from src.services.ask import AskService
from src.services.ingest import IngestService

setup_logging(get_settings().log_level)
logger = logging.getLogger(__name__)

app =  FastAPI(title="Asistente de documentos")

#Alias de dependencias: cada endpoint pide el servicio que necesita
IngestDep = Annotated[IngestService, Depends(get_ingest_service)]
AskDep = Annotated[AskService, Depends(get_ask_service)]
AgentDep = Annotated[AgentService, Depends(get_agent_service)]

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Una linea de log por peticion, con un id que tambien vuelve al cliente."""
    request_id = uuid.uuid4().hex[:12]
    start = time.perf_counter()
    response = await call_next(request)
    data = {
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "ms": round((time.perf_counter() - start) * 1000),
    }
    logger.info("request", extra={"data": data})
    response.headers["x-request-id"] = request_id
    return response

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

@app.post("/ingest", response_model=IngestResponse)
def ingest(files: list[UploadFile], service: IngestDep) -> IngestResponse:
    max_mb = get_settings().max_upload_mb
    uploads = []
    for f in files:
        name = Path(f.filename or "").name # .name descarta rutas tipos ../
        data = f.file.read(max_mb * 1024 * 1024 + 1)
        if len(data) > max_mb * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"{name}: supera el limite de {max_mb} MB")
        uploads.append((name, data))
    with errors_as_http(): # archivo que no sirve -> 400, fallo al calcular embeddins -> 5xx
        chunks = service.ingest(uploads)
    logger.info("ingest", extra={"data": {"files": len(uploads), "chunks": chunks}})
    return IngestResponse(files=[name for name, _ in uploads], chunks=chunks)

def answer_fields(answer: Answer) -> dict:
    """Del objeto de dominio a los campos que viajan por HTTP."""
    return {"sources": answer.sources, "grounded": answer.grounded, "usage": asdict(answer.usage)}

def log_answer(answer: Answer) -> None:
    logger.info("ask", extra={"data": {"grounded": answer.grounded, **asdict(answer.usage)}})

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest, service: AskDep) -> AskResponse:
    with errors_as_http():
        answer = service.ask(req.question, req.k)
    log_answer(answer)
    return AskResponse(answer=answer.text, **answer_fields(answer))

def event(**data) -> str:
    """Una linea NDJSON: un objecto JSON y un salto de linea."""
    return json.dumps(data, ensure_ascii=False) + "\n"

@app.post("/ask/stream")
def ask_stream(req: AskRequest, service: AskDep) -> StreamingResponse:
    def generate():
        try:
            for item in service.stream(req.question, req.k):
                if isinstance(item, Answer): # lo ultimo que llega: la respuesta completa
                    log_answer(item)
                    yield event(type="done", **answer_fields(item))
                else:
                    yield event(type="token", text=item)
        except Exception as exc: # el 200 ya salio: el error viaja como un evento mas
            logger.error("fallo_proveedor", exc_info=exc)
            yield event(type="error", detail=to_http(exc)[1])
    return StreamingResponse(generate(), media_type="application/x-ndjson")

@app.post("/agent", response_model=AgentResponse)
def agent_chat(req: AgentRequest, service: AgentDep) -> AgentResponse:
    thread_id = req.thread_id or uuid.uuid4().hex # sin id = conversacion nueva, nunca compartida
    with errors_as_http():
        answer, usage = service.chat(req.message, thread_id)
    logger.info("agent", extra={"data": {"thread_id": thread_id, **asdict(usage)}})
    return AgentResponse(answer=answer, thread_id=thread_id, usage=asdict(usage))

#Lo Ultimo: lo que no coincide con ninguna ruta se busca en src/web/ ("/" entrega index.html)
WEB_DIR = Path(__file__).resolve().parent.parent / "web"
app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")