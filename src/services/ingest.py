"""Caso de uso: convertir archivos en trozos que se pueden buscar."""

from dataclasses import replace

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.domain.documents import Chunk, ChunkRepository, DocumentReader

SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=1000, # caracteres por trozo, si se reduce es mas preciso
    chunk_overlap=150, # solapamiento para no cortar ideas a la mitad 
)

def split_chunks(pages: list[Chunk]) -> list[Chunk]:
    """Parte cada página en trozos más pequeños, que conservan su archivo y su página."""
    return [replace(page, text=piece) for page in pages for piece in SPLITTER.split_text(page.text)]

class IngestService:
    def __init__(self, read: DocumentReader, repo: ChunkRepository) -> None:
        self._read = read
        self._repo = repo

    def ingest(self, files: list[tuple[str, bytes]]) -> int:
        """Recibe [(nombre, contenido)] y devuelve cueantos trozos guardo. 
        Lanza DocumentError si un archivo no sirve. Todo se lee antes de guardar"""
        pages = [page for name, data in files for page in self._read(name, data)]
        chunks = split_chunks(pages)
        if chunks:
            if chunks:
                self._repo.add(chunks) #aqui se calculan los embeddings: llamada al proveedor
            return len(chunks)
        
