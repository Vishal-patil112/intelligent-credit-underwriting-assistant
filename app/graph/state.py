from __future__ import annotations

from typing import Any, TypedDict


class UnderwritingState(TypedDict, total=False):
    application_id: str
    application: dict[str, Any]
    documents: list[dict[str, Any]]
    parsed_documents: list[dict[str, Any]]
    classifications: list[dict[str, Any]]
    extractions: list[dict[str, Any]]
    profile: dict[str, Any]
    metrics: dict[str, Any]
    anomalies: list[dict[str, Any]]
    risk: dict[str, Any]
    policy: dict[str, Any]
    recommendation: dict[str, Any]
    route: str
    workflow_errors: list[dict[str, Any]]
