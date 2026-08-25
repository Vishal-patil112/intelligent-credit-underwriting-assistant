from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field, model_validator

from app.schemas.common import StrictBaseModel


class UnderwriterAction(str, Enum):
    APPROVE = 'APPROVE'
    CONDITIONALLY_APPROVE = 'CONDITIONALLY_APPROVE'
    REJECT = 'REJECT'
    REQUEST_MORE_DOCUMENTS = 'REQUEST_MORE_DOCUMENTS'
    ESCALATE = 'ESCALATE'
    OVERRIDE_AI_RECOMMENDATION = 'OVERRIDE_AI_RECOMMENDATION'


class UnderwriterDecisionRequest(StrictBaseModel):
    action: UnderwriterAction
    comments: str | None = Field(default=None, max_length=4000)
    conditions: list[str] = Field(default_factory=list)
    override_reason: str | None = Field(default=None, max_length=4000)

    @model_validator(mode='after')
    def require_override_reason(self):
        if self.action == UnderwriterAction.OVERRIDE_AI_RECOMMENDATION and not self.override_reason:
            raise ValueError('override_reason is required when overriding the AI recommendation')
        return self


class UnderwriterDecisionRecord(UnderwriterDecisionRequest):
    application_id: str
    user_id: str
    timestamp: datetime
    model_version: str | None = None
    policy_version: str | None = None
