from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.repository import add_simulation, get_analysis, get_application, list_audit, list_documents
from app.db.session import get_db
from app.graph import underwriting_graph
from app.schemas.analysis import AnalysisBundle
from app.schemas.document import DocumentType
from app.schemas.metrics import FinancialMetrics
from app.schemas.profile import CanonicalBorrowerProfile
from app.schemas.recommendation import UnderwritingRecommendation
from app.schemas.risk import Anomaly, PolicyEvaluation, RiskAssessment
from app.schemas.simulation import LoanSimulationRequest, LoanSimulationResult
from app.services.simulator_service import simulate
from app.api.dependencies import bind_application_id

router = APIRouter(
    prefix="/applications/{application_id}",
    tags=["underwriting"],
    dependencies=[Depends(bind_application_id)],
)


def _analysis_or_404(db: Session, application_id: str):
    row = get_analysis(db, application_id)
    if not row:
        raise HTTPException(status_code=404, detail='Analysis has not been run')
    return row


@router.post('/analyze')
def analyze(application_id: str, db: Session = Depends(get_db)):
    if not get_application(db, application_id):
        raise HTTPException(status_code=404, detail='Application not found')
    try:
        result = underwriting_graph.invoke({'application_id': application_id})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Underwriting workflow failed: {type(exc).__name__}: {exc}') from exc
    return {'application_id': application_id, 'status': result.get('recommendation', {}).get('status', 'COMPLETED'), 'recommendation': result.get('recommendation')}


@router.get('/analysis', response_model=AnalysisBundle)
def get_analysis_bundle(application_id: str, db: Session = Depends(get_db)):
    row = _analysis_or_404(db, application_id)
    return AnalysisBundle(application_id=application_id,
        profile=CanonicalBorrowerProfile.model_validate(row.profile_json), metrics=FinancialMetrics.model_validate(row.metrics_json),
        anomalies=[Anomaly.model_validate(x) for x in row.anomalies_json], risk=RiskAssessment.model_validate(row.risk_json),
        policy=PolicyEvaluation.model_validate(row.policy_json), recommendation=UnderwritingRecommendation.model_validate(row.recommendation_json),
        completed_at=row.completed_at)


@router.get('/profile', response_model=CanonicalBorrowerProfile)
def get_profile(application_id: str, db: Session = Depends(get_db)):
    return CanonicalBorrowerProfile.model_validate(_analysis_or_404(db, application_id).profile_json)


@router.get('/metrics', response_model=FinancialMetrics)
def get_metrics(application_id: str, db: Session = Depends(get_db)):
    return FinancialMetrics.model_validate(_analysis_or_404(db, application_id).metrics_json)


@router.get('/anomalies', response_model=list[Anomaly])
def get_anomalies(application_id: str, db: Session = Depends(get_db)):
    return [Anomaly.model_validate(x) for x in _analysis_or_404(db, application_id).anomalies_json]


@router.get('/risk', response_model=RiskAssessment)
def get_risk(application_id: str, db: Session = Depends(get_db)):
    return RiskAssessment.model_validate(_analysis_or_404(db, application_id).risk_json)


@router.get('/policy', response_model=PolicyEvaluation)
def get_policy(application_id: str, db: Session = Depends(get_db)):
    return PolicyEvaluation.model_validate(_analysis_or_404(db, application_id).policy_json)


@router.get('/recommendation', response_model=UnderwritingRecommendation)
def get_recommendation(application_id: str, db: Session = Depends(get_db)):
    return UnderwritingRecommendation.model_validate(_analysis_or_404(db, application_id).recommendation_json)


@router.get('/audit')
def get_audit(application_id: str, db: Session = Depends(get_db)):
    return [
        {'event_id': x.id, 'application_id': x.application_id, 'document_id': x.document_id, 'event_type': x.event_type,
         'workflow_node': x.workflow_node, 'actor': x.actor, 'metadata': x.metadata_json, 'timestamp': x.created_at}
        for x in list_audit(db, application_id)
    ]


@router.post('/simulate', response_model=LoanSimulationResult)
def simulate_loan(application_id: str, scenario: LoanSimulationRequest, db: Session = Depends(get_db)):
    analysis = _analysis_or_404(db, application_id)
    profile = CanonicalBorrowerProfile.model_validate(analysis.profile_json)
    present = {DocumentType(x.document_type) for x in list_documents(db, application_id)}
    result = simulate(profile, scenario, present)
    add_simulation(db, application_id, scenario.model_dump(mode='json'), result.model_dump(mode='json'))
    return result
