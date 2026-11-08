"""Indexa todos los PDF/TXT/MD de una carpeta src.scripts.ingest data/docs"""
import sys
from pathlib import Path

from src.container import get_ingest_service
from src.domain.documents import SUPPORTED_FORMATS

def main(folder: str) -> None:
    paths = [p for p in sorted(Path(folder).iterdir()) if p.suffix.lower() in SUPPORTED_FORMATS]
    chunks = get_ingest_service().ingest([(p.name, p.read_bytes()) for p in paths])
    print(f"{len(paths)} archivos -> {chunks} trozos indexados")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/docs")