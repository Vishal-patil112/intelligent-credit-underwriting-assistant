from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.repository import add_audit, create_application, get_application, list_applications
from app.db.session import get_db
from app.schemas.application import ApplicationCreate, ApplicationRecord

router = APIRouter(prefix='/applications', tags=['applications'])


def _record(row) -> ApplicationRecord:
    return ApplicationRecord(**row.payload, application_id=row.id, status=row.status, created_at=row.created_at, updated_at=row.updated_at)


@router.post('', response_model=ApplicationRecord, status_code=201)
def create_application_endpoint(payload: ApplicationCreate, db: Session = Depends(get_db)):
    if not payload.consent_confirmed:
        raise HTTPException(status_code=422, detail='Customer consent must be confirmed before creating an application')
    row = create_application(db, payload.model_dump(mode='json'))
    add_audit(db, row.id, 'APPLICATION_CREATED', actor='api', metadata={'business_name': row.business_name})
    return _record(row)


@router.get('', response_model=list[ApplicationRecord])
def list_applications_endpoint(db: Session = Depends(get_db)):
    return [_record(row) for row in list_applications(db)]


@router.get('/{application_id}', response_model=ApplicationRecord)
def get_application_endpoint(application_id: str, db: Session = Depends(get_db)):
    row = get_application(db, application_id)
    if not row:
        raise HTTPException(status_code=404, detail='Application not found')
    return _record(row)
