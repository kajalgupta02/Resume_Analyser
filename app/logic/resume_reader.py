"""Infrastructure adapter for extracting text from supported resume files."""

from __future__ import annotations

import os
from pathlib import Path

def load_resume_text(file_path: str | os.PathLike[str]) -> str:
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".docx":
        from docx import Document
        return "\n".join(paragraph.text for paragraph in Document(str(path)).paragraphs)
    if path.suffix.lower() == ".pdf":
        import fitz
        try:
            document = fitz.open(str(path))
        except Exception as exc:
            raise ValueError(f"Unable to open PDF file: {path}") from exc
        try:
            return "".join(page.get_text() for page in document)
        finally:
            document.close()
    raise ValueError(f"Unsupported file format: {path.suffix.lower()}")
