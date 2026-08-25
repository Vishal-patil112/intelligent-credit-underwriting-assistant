from __future__ import annotations

from datetime import datetime, timezone

from app.agents import classify_document, extract_document
from app.db.repository import (
    add_audit, get_application, list_documents, save_analysis, update_application_status, update_document,
)
from app.db.session import SessionLocal
from app.llm import GeminiClient
from app.schemas.analysis import GenericDocumentExtraction
from app.schemas.application import ApplicationRecord, ApplicationStatus
from app.schemas.document import DocumentType
from app.schemas.metrics import FinancialMetrics
from app.schemas.profile import CanonicalBorrowerProfile
from app.services.document_service import parse_document
from app.services.financial_service import calculate_metrics
from app.services.policy_service import apply_policy
from app.services.profile_service import build_profile
from app.services.recommendation_service import build_recommendation
from app.services.reconciliation_service import detect_anomalies
from app.services.risk_service import calculate_risk


def _application_record(row) -> ApplicationRecord:
    return ApplicationRecord(**row.payload, application_id=row.id, status=row.status, created_at=row.created_at, updated_at=row.updated_at)


def load_case(state):
    with SessionLocal() as db:
        app = get_application(db, state['application_id'])
        if not app:
            raise ValueError('Application not found')
        docs = list_documents(db, app.id)
        update_application_status(db, app.id, ApplicationStatus.ANALYZING.value)
        add_audit(db, app.id, 'ANALYSIS_STARTED', workflow_node='load_case')
        return {
            'application': _application_record(app).model_dump(mode='json'),
            'documents': [
                {'document_id': d.id, 'file_name': d.file_name, 'storage_uri': d.storage_uri, 'document_type': d.document_type,
                 'status': d.status, 'media_type': d.media_type, 'file_hash': d.file_hash, 'file_size_bytes': d.file_size_bytes}
                for d in docs
            ],
            'workflow_errors': [],
        }


def check_documents(state):
    return {'route': 'continue' if state.get('documents') else 'request_documents'}


def request_documents(state):
    application_id = state['application_id']
    with SessionLocal() as db:
        update_application_status(db, application_id, ApplicationStatus.DOCUMENTS_PENDING.value)
        add_audit(db, application_id, 'REQUEST_MORE_DOCUMENTS', workflow_node='request_documents', metadata={'reason': 'No documents uploaded'})
    return {'recommendation': {'application_id': application_id, 'status': 'REQUEST_MORE_DOCUMENTS', 'explanation': 'No documents uploaded.'}}


def classify_documents(state):
    llm = GeminiClient()
    parsed, classifications = [], []
    with SessionLocal() as db:
        for doc in state['documents']:
            parsed_doc = parse_document(doc['storage_uri'])
            classification = classify_document(doc['document_id'], doc['file_name'], parsed_doc.text, llm)
            parsed.append({'document_id': doc['document_id'], 'text': parsed_doc.text, 'parser': parsed_doc.parser})
            classifications.append(classification.model_dump(mode='json'))
            update_document(db, doc['document_id'], parsed_text=parsed_doc.text, document_type=classification.document_type.value, status='CLASSIFIED')
            add_audit(db, state['application_id'], 'DOCUMENT_CLASSIFIED', document_id=doc['document_id'], workflow_node='classify_documents',
                      metadata={'document_type': classification.document_type.value, 'confidence': classification.confidence, 'classifier': classification.classifier})
    return {'parsed_documents': parsed, 'classifications': classifications}


def extract_documents(state):
    llm = GeminiClient()
    class_by_id = {c['document_id']: c for c in state['classifications']}
    extractions = []
    with SessionLocal() as db:
        for parsed in state['parsed_documents']:
            classification = class_by_id[parsed['document_id']]
            doc_type = DocumentType(classification['document_type'])
            extraction = extract_document(parsed['document_id'], doc_type, parsed['text'], llm)
            extractions.append(extraction.model_dump(mode='json'))
            update_document(db, parsed['document_id'], status='EXTRACTED')
            add_audit(db, state['application_id'], 'EXTRACTION_COMPLETED', document_id=parsed['document_id'], workflow_node='extract_documents',
                      metadata={'extractor': extraction.extractor, 'confidence': extraction.extraction_confidence})
    return {'extractions': extractions}


def build_financial_profile(state):
    application = ApplicationRecord.model_validate(state['application'])
    extractions = [GenericDocumentExtraction.model_validate(x) for x in state['extractions']]
    profile = build_profile(application, extractions)
    return {'profile': profile.model_dump(mode='json')}


def calculate_financial_metrics(state):
    profile = CanonicalBorrowerProfile.model_validate(state['profile'])
    metrics = calculate_metrics(profile)
    return {'metrics': metrics.model_dump(mode='json')}


def anomaly_detection(state):
    application = ApplicationRecord.model_validate(state['application'])
    profile = CanonicalBorrowerProfile.model_validate(state['profile'])
    extractions = [GenericDocumentExtraction.model_validate(x) for x in state['extractions']]
    anomalies = detect_anomalies(application, profile, extractions)
    with SessionLocal() as db:
        for anomaly in anomalies:
            add_audit(db, state['application_id'], 'ANOMALY_DETECTED', workflow_node='anomaly_detection',
                      metadata=anomaly.model_dump(mode='json'))
    return {'anomalies': [a.model_dump(mode='json') for a in anomalies]}


def calculate_risk_node(state):
    from app.schemas.risk import Anomaly
    profile = CanonicalBorrowerProfile.model_validate(state['profile'])
    metrics = FinancialMetrics.model_validate(state['metrics'])
    anomalies = [Anomaly.model_validate(x) for x in state['anomalies']]
    risk = calculate_risk(profile, metrics, anomalies)
    with SessionLocal() as db:
        add_audit(db, state['application_id'], 'RISK_CALCULATED', workflow_node='calculate_risk', metadata={'score': float(risk.score), 'grade': risk.risk_grade.value})
    return {'risk': risk.model_dump(mode='json')}


def apply_policy_node(state):
    profile = CanonicalBorrowerProfile.model_validate(state['profile'])
    metrics = FinancialMetrics.model_validate(state['metrics'])
    present = {DocumentType(c['document_type']) for c in state['classifications']}
    policy = apply_policy(profile, metrics, present)
    with SessionLocal() as db:
        add_audit(db, state['application_id'], 'POLICY_EVALUATED', workflow_node='apply_policy', metadata={'overall_result': policy.overall_result.value})
    return {'policy': policy.model_dump(mode='json')}


def generate_recommendation_node(state):
    from app.schemas.risk import Anomaly, PolicyEvaluation, RiskAssessment
    profile = CanonicalBorrowerProfile.model_validate(state['profile'])
    metrics = FinancialMetrics.model_validate(state['metrics'])
    anomalies = [Anomaly.model_validate(x) for x in state['anomalies']]
    risk = RiskAssessment.model_validate(state['risk'])
    policy = PolicyEvaluation.model_validate(state['policy'])
    recommendation = build_recommendation(profile, metrics, anomalies, risk, policy, GeminiClient())
    with SessionLocal() as db:
        add_audit(db, state['application_id'], 'RECOMMENDATION_GENERATED', workflow_node='generate_recommendation',
                  metadata={'status': recommendation.status.value, 'recommended_amount': str(recommendation.recommended_amount) if recommendation.recommended_amount else None})
    return {'recommendation': recommendation.model_dump(mode='json')}


def persist_analysis(state):
    with SessionLocal() as db:
        save_analysis(db, state['application_id'], {
            'profile_json': state['profile'], 'metrics_json': state['metrics'], 'anomalies_json': state['anomalies'],
            'risk_json': state['risk'], 'policy_json': state['policy'], 'recommendation_json': state['recommendation'],
            'extraction_json': state['extractions'], 'completed_at': datetime.now(timezone.utc),
        })
        rec_status = state['recommendation']['status']
        update_application_status(db, state['application_id'], ApplicationStatus.HUMAN_REVIEW.value)
        add_audit(db, state['application_id'], 'ANALYSIS_COMPLETED', workflow_node='persist_analysis')
    return {}
