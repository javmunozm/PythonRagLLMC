"""Traduce los errores a respuestas HTTP claras: pase lo que pase, la API responde JSON."""
import logging
from collections.abc import Generator, Iterator
from contextlib import contextmanager

import httpx
from fastapi import HTTPException
from langchain_core import exceptions as lc

from src.domain.documents import DocumentError

logger = logging.getLogger(__name__)


def _chain(exc: BaseException | None) -> Iterator[BaseException]:
    """La ecepcion y sus causas: los SDK suelen envolver el error original"""
    while exc is not None:
        yield exc
        exc = exc.__cause__ or exc.__context__

def _is_timeout(e: BaseException) -> bool:
    #no heredan de httpx.*: se reconocen tambien por el nombre de la clase.
    return isinstance(e, (httpx.TimeoutException, lc.ModelTimeoutError, TimeoutError)) or (
        "Timeout" in type(e).__name__
    )

def _is_connection(e: BaseException) -> bool:
    return isinstance(e, (httpx.TransportError, lc.ModelConnectionError, ConnectionError)) or (
        "Connect" in type(e).__name__
    )

def to_http(exc: BaseException) -> tuple[int, str]:
    """(código HTTP, mensaje para el cliente). Sirve igual para OpenAI, Azure y Gemini."""
    for e in _chain(exc):
        status = getattr(e, "status_code", None) or getattr(e, "code", None)
        if status == 429 or isinstance(e, lc.ModelRateLimitError):
            return (
                429,
                "El proveedor de IA esta limitando las peticiones. Reintente en unos segundos.",
            )
        if _is_timeout(e):
            return 504, "El proveedor de IA tardo demasiado en responder."
        if _is_connection(e):
            return 503, "No se pudo conectar con el proveedor de IA."
        if status in (401, 403, 404):
            return (
                502,
                "El servidor esta mal configurado para su proveedor de IA (clave, URL o modelo).",
            )
        if isinstance(status, int) and status >= 400:
            return 502, "El proveedor de IA rechazo la peticion o fallo."
    return 500, "Error interno."

@contextmanager
def errors_as_http() -> Generator[None]:
    """with errors_as_http(): ... -> cualquier fallo sale como HTTPException con JSON."""
    try:
        yield
    except HTTPException:
        raise
    except DocumentError as exc: #error de dominio: el archivo que mando el cliente no sirve
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc: #lo demas: fallo el proveedor de IA (o hay un bug)
        status, detail = to_http(exc)
        logger.error(
            "fallo_proveedor",
            exc_info=exc,
            extra={"data": {"status": status, "error": type(exc).__name__}},
        ),
        headers = {"Retry-After": "10"} if status == 429 else None
        raise HTTPException(status_code=status, detail=detail, headers=headers) from exc
        