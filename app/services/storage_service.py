from __future__ import annotations

import hashlib
import re
from pathlib import Path

from app.config import get_settings

settings = get_settings()
ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.tif', '.tiff', '.txt', '.csv', '.json'}


def safe_filename(name: str) -> str:
    name = Path(name or 'document').name
    stem = re.sub(r'[^A-Za-z0-9._-]+', '_', name).strip('._') or 'document'
    return stem[:200]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_upload(file_name: str, data: bytes) -> None:
    ext = Path(file_name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f'Unsupported file extension: {ext or "<none>"}')
    if not data:
        raise ValueError('Uploaded file is empty')
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise ValueError(f'File exceeds {settings.max_upload_mb} MB limit')


def save_document(application_id: str, document_id: str, file_name: str, data: bytes) -> Path:
    folder = settings.upload_directory / application_id
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / f'{document_id}_{safe_filename(file_name)}'
    target.write_bytes(data)
    return target
