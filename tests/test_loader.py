import pytest

from src.domain.documents import Chunk, DocumentError
from src.repositories.loader import load_bytes
from tests.fakes import tiny_pdf

def test_pdf_con_texto():
    chunks = load_bytes("rrhh.pdf", tiny_pdf("Vacaciones: 15 dias habiles"))
    assert chunks == [Chunk("Vacaciones: 15 dias habiles", source="rrhh.pdf", page=1)]

@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig", "cp1252"])
def test_txt_en_cualquier_codificacion_habitial(encoding):
    chunks = load_bytes("politica.txt", "Politica: 15 dias habiles".encode(encoding))
    assert chunks == [Chunk("Politica: 15 dias habiles", source="politica.txt")]

@pytest.mark.parametrize(
    ("name", "data", "motivo"),
    [
        ("virus.exe", b"MZ", "formato no soportado"),
        ("roto.pdf", b"esto no es un pdf", "no se pudo leer"),
        ("escaneado.pdf", tiny_pdf(""), "texto extraible"),
        ("vacio.txt", b"    \n", "vacio"),
    ],
)
def test_archivos_que_se_rechazan(name, data, motivo):
    with pytest.raises(DocumentError, match=motivo):
        load_bytes(name, data)