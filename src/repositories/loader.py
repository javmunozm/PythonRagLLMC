"""Infraestructura: convierte archivos (PDF, TXT, MD) en trozos. Cumple
DocumentReader."""

import io
from pathlib import Path
from pypdf import PdfReader

from src.domain.documents import Chunk, DocumentError

def load_pdf(name: str, data: bytes) -> list[Chunk]:
    """Un trozo por pagina, con el archivo y el numero de pagina."""
    try:
        pages = [page.extract_text() or "" for page in PdfReader(io.BytesIO(data)).pages]
    except Exception as e:
        raise DocumentError(f"{name}: no se pudo leer el PDF ({type(e).__name__})") from e
    chunks = [
        Chunk(text, source=name, page=number) for number, text in enumerate(pages, start=1)
        if text.strip()
    ]
    if not chunks:
        raise DocumentError(f"{name}: el PDF no tiene texto extraible (¿esta escaneado?)")
    return chunks

def load_text(name: str, data: bytes) -> list[Chunk]:
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = data.decode("cp1252", errors="replace") #el ANSI del bloc  de notas
    if not text.strip():
        raise DocumentError(f"{name}: el archivo esta vacio")
    return [Chunk(text, source=name)]

def load_bytes(name: str, data: bytes) -> list[Chunk]:
    match Path(name).suffix.lower():
        case ".pdf":
            return load_pdf(name, data)
        case ".txt" | ".md":
            return load_text(name, data)
        case _:
            raise DocumentError(f"{name}: formato no soportado (usa PDF, TXT o MD)")
        
    