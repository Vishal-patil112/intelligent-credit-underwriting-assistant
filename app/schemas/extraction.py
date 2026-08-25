from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import Field

from app.schemas.common import Confidence, StrictBaseModel
from app.schemas.document import DocumentType

T = TypeVar('T')


class EvidenceSource(StrictBaseModel):
    document_id: str
    document_type: DocumentType
    page: int | None = Field(default=None, ge=1)
    section: str | None = Field(default=None, max_length=200)
    source_text: str | None = Field(default=None, max_length=3000)
    bounding_box: list[float] | None = None


class ExtractedField(StrictBaseModel, Generic[T]):
    value: T | None = None
    confidence: Confidence
    source: EvidenceSource
    notes: str | None = Field(default=None, max_length=1000)


class BaseDocumentExtraction(StrictBaseModel):
    document_id: str
    document_type: DocumentType
    schema_version: str = '1.0'
    extraction_confidence: Confidence
    model_version: str | None = None
    warnings: list[str] = Field(default_factory=list)
