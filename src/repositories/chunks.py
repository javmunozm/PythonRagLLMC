"""Infraestructura: dónde se guardan y se buscan los trozos (la base
vectorial)."""

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore

from src.config import get_settings
from src.domain.documents import Chunk, chunk_ids

def get_vector_store(embeddings: Embeddings) -> Chroma:
    s = get_settings()
    return Chroma(
        collection_name=s.collection_name,
        embedding_function=embeddings,
        persist_directory=s.chroma_dir, # se guarda localmente, sobrevive reinicios
    )

def to_document(chunk: Chunk) -> Document:
    metadata = {"source": chunk.source}
    if chunk.page is not None:
        metadata["page"] = chunk.page # .txt y .md no llevan pagina
    return Document(page_content=chunk.text, metadata=metadata)

def to_chunk(doc: Document) -> Chunk:
    return Chunk(doc.page_content, doc.metadata.get("source", "?"), doc.metadata.get("page"))

class VectorChunkRepository: #cumple ChunkRepository sin heredar de el (Protocol)
    """Traduce entre Chunk (dominio) y Document (LangChain) sobre cualquier VectorStore."""

    def __init__(self, store: VectorStore) -> None:
        self._store = store

    def add(self, chunks: list[Chunk]) -> None:
        docs = [to_document(chunk) for chunk in chunks]
        self._store.add_documents(docs, ids=chunk_ids(chunks)) #calcula embeddings y guarda

    def search(self, query: str, k: int) -> list[Chunk]:
        return [to_chunk(doc) for doc in self._store.similarity_search(query, k=k)]