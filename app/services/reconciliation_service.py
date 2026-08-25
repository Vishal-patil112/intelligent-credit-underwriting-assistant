from __future__ import annotations

import re
from datetime import date
from decimal import Decimal
from uuid import uuid4

from app.config import get_settings
from app.schemas.analysis import GenericDocumentExtraction
from app.schemas.application import ApplicationRecord
from app.schemas.common import Severity
from app.schemas.document import DocumentType
from app.schemas.profile import CanonicalBorrowerProfile
from app.schemas.risk import Anomaly
from app.services.normalization_service import normalize_date

settings = get_settings()


def _new_anomaly(kind: str, severity: Severity, description: str, evidence_ids=None, confidence=1.0) -> Anomaly:
    return Anomaly(anomaly_id=f'ANM-{uuid4().hex[:10].upper()}', anomaly_type=kind, severity=severity,
                   description=description, confidence=confidence, evidence_ids=evidence_ids or [], requires_review=True)


def _field(extractions, doc_type, key):
    for ex in extractions:
        if ex.document_type == doc_type and key in ex.fields:
            return ex.fields[key].value
    return None


def detect_anomalies(application: ApplicationRecord, profile: CanonicalBorrowerProfile,
                     extractions: list[GenericDocumentExtraction]) -> list[Anomaly]:
    anomalies: list[Anomaly] = []
    revenues = []
    sources = []
    for label, value in (
        ('application', application.declared_annual_revenue),
        ('financial_statement', _field(extractions, DocumentType.FINANCIAL_STATEMENT, 'revenue')),
        ('tax_return', _field(extractions, DocumentType.TAX_RETURN, 'reported_turnover')),
    ):
        if value is not None:
            revenues.append(Decimal(str(value))); sources.append(label)
    bank_inflow = profile.banking.average_monthly_inflow
    if bank_inflow is not None:
        revenues.append(bank_inflow * 12); sources.append('annualized_bank_inflow')
    if len(revenues) >= 2:
        high, low = max(revenues), min(revenues)
        diff = (high - low) / high if high else Decimal('0')
        if diff > Decimal(str(settings.revenue_mismatch_tolerance)):
            anomalies.append(_new_anomaly('REVENUE_MISMATCH', Severity.HIGH,
                f'Revenue observations differ by {float(diff)*100:.1f}% across {", ".join(sources)}.'))

    app_debt = application.declared_existing_obligations
    credit_debt = profile.credit.total_outstanding
    if app_debt is not None and credit_debt is not None and Decimal(app_debt) > 0:
        diff = abs(Decimal(credit_debt) - Decimal(app_debt)) / max(Decimal(credit_debt), Decimal(app_debt))
        if diff > Decimal('0.20'):
            anomalies.append(_new_anomaly('LIABILITY_MISMATCH', Severity.HIGH,
                f'Declared debt and credit-report debt differ materially ({float(diff)*100:.1f}%).'))

    if profile.existing_debt.observed_lender_payments is not None and profile.credit.active_facilities is not None:
        if profile.existing_debt.observed_lender_payments > profile.credit.active_facilities:
            anomalies.append(_new_anomaly('POTENTIAL_HIDDEN_LIABILITY', Severity.HIGH,
                'Banking activity suggests more recurring lender payments than active facilities in the credit report.'))

    if (profile.banking.bounced_transactions or 0) >= 3:
        anomalies.append(_new_anomaly('REPEATED_BOUNCES', Severity.MEDIUM,
            f'{profile.banking.bounced_transactions} bounced/returned transactions were observed.'))
    if (profile.credit.serious_defaults or 0) > 0:
        anomalies.append(_new_anomaly('SERIOUS_DEFAULT', Severity.CRITICAL, 'Recent serious default is present in credit information.'))

    if profile.collateral.valuation_date:
        val_date = normalize_date(profile.collateral.valuation_date)
        if val_date and (date.today() - val_date).days > settings.collateral_max_age_days:
            anomalies.append(_new_anomaly('STALE_COLLATERAL_VALUATION', Severity.MEDIUM,
                f'Collateral valuation is older than {settings.collateral_max_age_days} days.'))

    for ex in extractions:
        if ex.extraction_confidence < settings.low_confidence_threshold:
            anomalies.append(_new_anomaly('LOW_EXTRACTION_CONFIDENCE', Severity.MEDIUM,
                f'{ex.document_type.value} extraction confidence is {ex.extraction_confidence:.2f}.', [ex.document_id], ex.extraction_confidence))

    return anomalies
