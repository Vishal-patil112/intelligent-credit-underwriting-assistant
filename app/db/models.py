from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ApplicationModel(Base):
    __tablename__ = 'applications'
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    business_name: Mapped[str] = mapped_column(String(255), index=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class DocumentModel(Base):
    __tablename__ = 'documents'
    __table_args__ = (UniqueConstraint('application_id', 'file_hash', name='uq_application_file_hash'),)
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    application_id: Mapped[str] = mapped_column(ForeignKey('applications.id', ondelete='CASCADE'), index=True)
    file_name: Mapped[str] = mapped_column(String(255))
    storage_uri: Mapped[str] = mapped_column(Text)
    file_hash: Mapped[str] = mapped_column(String(128), index=True)
    media_type: Mapped[str | None] = mapped_column(String(150), nullable=True)
    file_size_bytes: Mapped[int] = mapped_column(Integer)
    document_type: Mapped[str] = mapped_column(String(50), default='UNKNOWN')
    status: Mapped[str] = mapped_column(String(40), default='UPLOADED')
    parsed_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AnalysisModel(Base):
    __tablename__ = 'analyses'
    application_id: Mapped[str] = mapped_column(ForeignKey('applications.id', ondelete='CASCADE'), primary_key=True)
    profile_json: Mapped[dict] = mapped_column(JSON)
    metrics_json: Mapped[dict] = mapped_column(JSON)
    anomalies_json: Mapped[list] = mapped_column(JSON)
    risk_json: Mapped[dict] = mapped_column(JSON)
    policy_json: Mapped[dict] = mapped_column(JSON)
    recommendation_json: Mapped[dict] = mapped_column(JSON)
    extraction_json: Mapped[list] = mapped_column(JSON)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class UnderwriterDecisionModel(Base):
    __tablename__ = 'underwriter_decisions'
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    application_id: Mapped[str] = mapped_column(ForeignKey('applications.id', ondelete='CASCADE'), index=True)
    action: Mapped[str] = mapped_column(String(60))
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    conditions_json: Mapped[list] = mapped_column(JSON, default=list)
    override_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_id: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AuditEventModel(Base):
    __tablename__ = 'audit_events'
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    application_id: Mapped[str] = mapped_column(ForeignKey('applications.id', ondelete='CASCADE'), index=True)
    document_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    workflow_node: Mapped[str | None] = mapped_column(String(100), nullable=True)
    actor: Mapped[str] = mapped_column(String(100), default='system')
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class SimulationModel(Base):
    __tablename__ = 'simulations'
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    application_id: Mapped[str] = mapped_column(ForeignKey('applications.id', ondelete='CASCADE'), index=True)
    scenario_json: Mapped[dict] = mapped_column(JSON)
    result_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
