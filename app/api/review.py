from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db.repository import add_audit, add_decision, get_application, latest_decision, update_application_status
from app.db.session import get_db
from app.schemas.application import ApplicationStatus
from app.schemas.review import UnderwriterDecisionRequest
from app.api.dependencies import bind_application_id

router = APIRouter(
    prefix="/applications/{application_id}",
    tags=["human-review"],
    dependencies=[Depends(bind_application_id)],
)


@router.post('/decision')
def submit_decision(application_id: str, decision: UnderwriterDecisionRequest,
                    x_user_id: str = Header(default='hackathon-underwriter'), db: Session = Depends(get_db)):
    if not get_application(db, application_id):
        raise HTTPException(status_code=404, detail='Application not found')
    row = add_decision(db, application_id, decision.model_dump(mode='json'), x_user_id)
    event = 'UNDERWRITER_OVERRIDE' if decision.action.value == 'OVERRIDE_AI_RECOMMENDATION' else 'FINAL_DECISION'
    add_audit(db, application_id, event, actor=x_user_id, metadata={'action': decision.action.value, 'comments': decision.comments, 'override_reason': decision.override_reason})
    update_application_status(db, application_id, ApplicationStatus.DECIDED.value)
    return {'decision_id': row.id, 'application_id': application_id, 'action': decision.action.value, 'user_id': x_user_id, 'timestamp': row.created_at}


@router.get('/decision')
def get_latest_decision(application_id: str, db: Session = Depends(get_db)):
    row = latest_decision(db, application_id)
    if not row:
        raise HTTPException(status_code=404, detail='No underwriter decision recorded')
    return {'decision_id': row.id, 'application_id': row.application_id, 'action': row.action, 'comments': row.comments,
            'conditions': row.conditions_json, 'override_reason': row.override_reason, 'user_id': row.user_id, 'timestamp': row.created_at}
