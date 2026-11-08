import pytest

from src.domain.documents import Chunk, DocumentError
from src.repositories.loader import load_bytes
from src.services.ingest import IngestService, split_chunks

FILES = [("politica.txt", b"Teletrabajo: 2 dias."), ("horario.md", b"de 9 a 18 horas")]

def test_split_chunks_conserva_el_origen():
    chunks = split_chunks([Chunk("palabra " * 1000, source="x.pdf", page=3)])
    assert len(chunks) > 1
    assert all(len(c.text) <= 1000 for c in chunks)
    assert {(c.source, c.page) for c in chunks} == {("x.pdf", 3)}

def test_ingest_guarda_y_se_puede_buscar(empty_repo):
    assert IngestService(load_bytes, empty_repo).ingest(FILES) == 2
    found =empty_repo.search("teletrabajo", k=5)
    assert {chunk.source for chunk in found} == {"politica.txt", "horario.md"}

def test_reindexar_no_duplica(empty_repo, vector_store):
    service = IngestService(load_bytes, empty_repo)
    for _ in range(2):
        service.ingest(FILES)
    assert len(vector_store.store) == 2

def test_un_archivo_malo_no_deja_la_carga_a_medias(empty_repo, vector_store):
    with pytest.raises(DocumentError, match="virus.exe"):
        IngestService(load_bytes, empty_repo).ingest([*FILES, ("virus.exe",b"MZ")])
    assert len(vector_store.store) == 0