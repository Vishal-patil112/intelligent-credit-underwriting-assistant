from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import (
    AnalysisModel, ApplicationModel, AuditEventModel, DocumentModel,
    SimulationModel, UnderwriterDecisionModel,
)


def new_id(prefix: str) -> str:
    return f'{prefix}-{uuid4().hex[:12].upper()}'


def create_application(db: Session, payload: dict) -> ApplicationModel:
    row = ApplicationModel(
        id=new_id('APP'), business_name=payload['business_name'], status='DOCUMENTS_PENDING', payload=payload
    )
    db.add(row); db.commit(); db.refresh(row)
    return row


def get_application(db: Session, application_id: str) -> ApplicationModel | None:
    return db.get(ApplicationModel, application_id)


def list_applications(db: Session) -> list[ApplicationModel]:
    return list(db.scalars(select(ApplicationModel).order_by(ApplicationModel.created_at.desc())))


def update_application_status(db: Session, application_id: str, status: str) -> None:
    row = db.get(ApplicationModel, application_id)
    if row:
        row.status = status; row.updated_at = datetime.now(timezone.utc); db.commit()


def add_document(db: Session, **kwargs) -> DocumentModel:
    document_id = kwargs.pop('id', None) or new_id('DOC')
    row = DocumentModel(id=document_id, **kwargs)
    db.add(row)
    try:
        db.commit(); db.refresh(row); return row
    except IntegrityError:
        db.rollback(); raise


def get_document(db: Session, document_id: str) -> DocumentModel | None:
    return db.get(DocumentModel, document_id)


def list_documents(db: Session, application_id: str) -> list[DocumentModel]:
    return list(db.scalars(select(DocumentModel).where(DocumentModel.application_id == application_id).order_by(DocumentModel.created_at)))


def find_document_by_hash(db: Session, application_id: str, file_hash: str) -> DocumentModel | None:
    return db.scalar(select(DocumentModel).where(DocumentModel.application_id == application_id, DocumentModel.file_hash == file_hash))


def update_document(db: Session, document_id: str, **updates) -> None:
    row = db.get(DocumentModel, document_id)
    if row:
        for key, value in updates.items(): setattr(row, key, value)
        db.commit()


def save_analysis(db: Session, application_id: str, data: dict) -> AnalysisModel:
    row = db.get(AnalysisModel, application_id)
    if row is None:
        row = AnalysisModel(application_id=application_id, **data); db.add(row)
    else:
        for key, value in data.items(): setattr(row, key, value)
        row.completed_at = datetime.now(timezone.utc)
    db.commit(); db.refresh(row); return row


def get_analysis(db: Session, application_id: str) -> AnalysisModel | None:
    return db.get(AnalysisModel, application_id)


def add_audit(db: Session, application_id: str, event_type: str, *, document_id: str | None = None,
              workflow_node: str | None = None, actor: str = 'system', metadata: dict | None = None) -> AuditEventModel:
    row = AuditEventModel(id=new_id('AUD'), application_id=application_id, document_id=document_id,
                          event_type=event_type, workflow_node=workflow_node, actor=actor,
                          metadata_json=metadata or {})
    db.add(row); db.commit(); db.refresh(row); return row


def list_audit(db: Session, application_id: str) -> list[AuditEventModel]:
    return list(db.scalars(select(AuditEventModel).where(AuditEventModel.application_id == application_id).order_by(AuditEventModel.created_at)))


def add_decision(db: Session, application_id: str, data: dict, user_id: str) -> UnderwriterDecisionModel:
    row = UnderwriterDecisionModel(id=new_id('DEC'), application_id=application_id, action=str(data['action']),
        comments=data.get('comments'), conditions_json=data.get('conditions', []), override_reason=data.get('override_reason'), user_id=user_id)
    db.add(row); db.commit(); db.refresh(row); return row


def latest_decision(db: Session, application_id: str) -> UnderwriterDecisionModel | None:
    return db.scalar(select(UnderwriterDecisionModel).where(UnderwriterDecisionModel.application_id == application_id)
                     .order_by(UnderwriterDecisionModel.created_at.desc()).limit(1))


def add_simulation(db: Session, application_id: str, scenario: dict, result: dict) -> SimulationModel:
    row = SimulationModel(id=new_id('SIM'), application_id=application_id, scenario_json=scenario, result_json=result)
    db.add(row); db.commit(); db.refresh(row); return row
