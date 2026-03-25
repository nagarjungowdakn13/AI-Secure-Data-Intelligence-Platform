from __future__ import annotations

from pathlib import Path
from typing import Tuple

from docx import Document
from pypdf import PdfReader


class ExtractionService:
    SUPPORTED_TYPES = {
        ".txt": "text",
        ".log": "log",
        ".sql": "sql",
        ".pdf": "file",
        ".docx": "file",
    }

    def extract(self, path: Path, original_name: str) -> Tuple[str, str]:
        suffix = path.suffix.lower()
        if suffix not in self.SUPPORTED_TYPES:
            raise ValueError(f"Unsupported file type: {suffix}")

        if suffix == ".pdf":
            return self._extract_pdf(path), "file"
        if suffix == ".docx":
            return self._extract_docx(path), "file"

        return path.read_text(encoding="utf-8", errors="ignore"), self.SUPPORTED_TYPES[suffix]

    def _extract_pdf(self, path: Path) -> str:
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()

    def _extract_docx(self, path: Path) -> str:
        document = Document(str(path))
        return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()
