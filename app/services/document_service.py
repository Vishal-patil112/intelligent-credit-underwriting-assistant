from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pymupdf
from PIL import Image
import pytesseract

from app.config import get_settings

settings = get_settings()
if settings.tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd


@dataclass
class ParsedPage:
    page: int
    text: str


@dataclass
class ParsedDocument:
    text: str
    pages: list[ParsedPage]
    parser: str


def parse_document(path: str | Path) -> ParsedDocument:
    path = Path(path)
    ext = path.suffix.lower()
    if ext == '.pdf':
        return _parse_pdf(path)
    if ext in {'.png', '.jpg', '.jpeg', '.tif', '.tiff'}:
        text = pytesseract.image_to_string(Image.open(path))
        return ParsedDocument(text=text, pages=[ParsedPage(page=1, text=text)], parser='tesseract')
    if ext == '.json':
        obj = json.loads(path.read_text(encoding='utf-8'))
        text = json.dumps(obj, indent=2, ensure_ascii=False)
        return ParsedDocument(text=text, pages=[ParsedPage(page=1, text=text)], parser='json')
    text = path.read_text(encoding='utf-8', errors='ignore')
    return ParsedDocument(text=text, pages=[ParsedPage(page=1, text=text)], parser='text')


def _parse_pdf(path: Path) -> ParsedDocument:
    pages: list[ParsedPage] = []
    parser = "pymupdf"

    with pymupdf.open(path) as doc:
        for idx, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()

            if not text:
                pix = page.get_pixmap(
                    matrix=pymupdf.Matrix(2, 2),
                    alpha=False,
                )

                image = Image.frombytes(
                    "RGB",
                    [pix.width, pix.height],
                    pix.samples,
                )

                text = pytesseract.image_to_string(image)
                parser = "pymupdf+tesseract"

            pages.append(
                ParsedPage(
                    page=idx,
                    text=text,
                )
            )

    full_text = "\n\n".join(
        f"[PAGE {page.page}]\n{page.text}"
        for page in pages
    )

    return ParsedDocument(
        text=full_text,
        pages=pages,
        parser=parser,
    )
