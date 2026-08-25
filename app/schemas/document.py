from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field

from app.schemas.common import Confidence, StrictBaseModel


class DocumentType(str, Enum):
    LOAN_APPLICATION = 'LOAN_APPLICATION'
    BANK_STATEMENT = 'BANK_STATEMENT'
    INCOME_STATEMENT = 'INCOME_STATEMENT'
    BALANCE_SHEET = 'BALANCE_SHEET'
    FINANCIAL_STATEMENT = 'FINANCIAL_STATEMENT'
    TAX_RETURN = 'TAX_RETURN'
    CREDIT_REPORT = 'CREDIT_REPORT'
    EXISTING_LOAN_STATEMENT = 'EXISTING_LOAN_STATEMENT'
    COLLATERAL_DOCUMENT = 'COLLATERAL_DOCUMENT'
    BUSINESS_REGISTRATION = 'BUSINESS_REGISTRATION'
    IDENTITY_DOCUMENT = 'IDENTITY_DOCUMENT'
    UNKNOWN = 'UNKNOWN'


class DocumentStatus(str, Enum):
    UPLOADED = 'UPLOADED'
    PARSED = 'PARSED'
    CLASSIFIED = 'CLASSIFIED'
    EXTRACTED = 'EXTRACTED'
    VALIDATED = 'VALIDATED'
    FAILED = 'FAILED'


class DocumentRecord(StrictBaseModel):
    document_id: str
    application_id: str
    file_name: str = Field(min_length=1, max_length=255)
    storage_uri: str
    file_hash: str = Field(min_length=16, max_length=128)
    media_type: str | None = None
    file_size_bytes: int = Field(ge=0)
    document_type: DocumentType = DocumentType.UNKNOWN
    status: DocumentStatus = DocumentStatus.UPLOADED
    created_at: datetime


class DocumentClassification(StrictBaseModel):
    document_id: str
    document_type: DocumentType
    confidence: Confidence
    reason: str = Field(min_length=1, max_length=1000)
    classifier: str
    model_version: str | None = None
