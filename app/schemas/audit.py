from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import Field

from app.schemas.common import StrictBaseModel


class AuditEventType(str, Enum):
    APPLICATION_CREATED = 'APPLICATION_CREATED'
    DOCUMENT_UPLOADED = 'DOCUMENT_UPLOADED'
    DOCUMENT_CLASSIFIED = 'DOCUMENT_CLASSIFIED'
    EXTRACTION_COMPLETED = 'EXTRACTION_COMPLETED'
    FIELD_OVERRIDDEN = 'FIELD_OVERRIDDEN'
    ANOMALY_DETECTED = 'ANOMALY_DETECTED'
    RISK_CALCULATED = 'RISK_CALCULATED'
    POLICY_EVALUATED = 'POLICY_EVALUATED'
    RECOMMENDATION_GENERATED = 'RECOMMENDATION_GENERATED'
    UNDERWRITER_OVERRIDE = 'UNDERWRITER_OVERRIDE'
    FINAL_DECISION = 'FINAL_DECISION'


class AuditEvent(StrictBaseModel):
    event_id: str
    application_id: str
    event_type: AuditEventType
    workflow_node: str | None = None
    timestamp: datetime
    actor: str
    version: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
