"""La arquitectura es la dirección de los imports. Python no la vigila: este test sí."""

import ast
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent.parent / "src"

PROVIDERS = {"openai", "google", "langchain_openai", "langchain_google_genai"}
STORAGE = {"langchain_chroma", "chromadb", "pypdf"}
WEB = {"fastapi", "starlette", "httpx"}
WIRING = {"src.config", "src.container"}

FORBIDDEN = {
    "services": PROVIDERS | STORAGE | WEB | WIRING | {"src.clients", "src.repositories", "src.api"},
    "clients": {"fastapi", "src.services", "src.api", "src.container"},
    "repositories": {"fastapi", "src.services", "src.api", "src.container"},
    "api": PROVIDERS | STORAGE | {"src.clients", "src.repositories"},
}


def imports(layer: str) -> set[str]:
    found = set()
    for path in (SRC / layer).glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            for name in names:
                parts = name.split(".")
                found.add(".".join(parts[:2]) if parts[0] == "src" else parts[0])
        return found


def test_el_dominio_es_python_puro():
    allowed = set(sys.stdlib_module_names) | {"pydantic", "src.domain"}
    assert imports("domain") <= allowed


@pytest.mark.parametrize("layer", sorted(FORBIDDEN))
def test_los_imports_apuntan_hacia_el_dominio(layer):
    assert imports(layer) & FORBIDDEN[layer] == set()
