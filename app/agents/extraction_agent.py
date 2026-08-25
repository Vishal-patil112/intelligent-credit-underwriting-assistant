from __future__ import annotations

import re
import logging
from typing import Any

from app.llm import GeminiClient
from app.schemas.analysis import GenericDocumentExtraction, GenericExtractedField
from app.schemas.document import DocumentType
from app.services.normalization_service import normalize_date, normalize_number, scalar
logger = logging.getLogger(__name__)

FIELDS: dict[DocumentType, list[str]] = {
    DocumentType.BANK_STATEMENT: [
        'account_holder', 'account_number_masked', 'bank_name', 'opening_balance', 'closing_balance',
        'average_monthly_inflow', 'average_monthly_outflow', 'average_monthly_balance', 'minimum_balance',
        'negative_balance_days', 'bounced_transactions', 'recurring_emi', 'observed_lender_payments'
    ],
    DocumentType.FINANCIAL_STATEMENT: [
        'business_name', 'revenue', 'previous_revenue', 'ebitda', 'net_profit', 'cash_balance',
        'current_assets', 'current_liabilities', 'total_assets', 'total_liabilities', 'total_debt',
        'receivables', 'inventory', 'equity'
    ],
    DocumentType.INCOME_STATEMENT: ['business_name', 'revenue', 'previous_revenue', 'ebitda', 'net_profit'],
    DocumentType.BALANCE_SHEET: ['business_name', 'cash_balance', 'current_assets', 'current_liabilities', 'total_assets', 'total_liabilities', 'total_debt', 'equity'],
    DocumentType.TAX_RETURN: ['business_name', 'tax_identifier', 'reported_turnover', 'taxable_income', 'tax_paid', 'filing_date'],
    DocumentType.CREDIT_REPORT: ['bureau_score', 'active_facilities', 'total_outstanding_debt', 'total_monthly_obligation', 'delinquencies_12m', 'serious_defaults', 'hard_enquiries_6m', 'utilization_percentage'],
    DocumentType.EXISTING_LOAN_STATEMENT: ['lender', 'loan_type', 'outstanding_principal', 'emi', 'total_outstanding', 'total_monthly_obligation', 'days_past_due'],
    DocumentType.COLLATERAL_DOCUMENT: ['collateral_type', 'asset_description', 'owner_name', 'estimated_value', 'encumbrance', 'valuation_date'],
}

ALIASES = {
    'annual_revenue': 'revenue', 'sales': 'revenue', 'turnover': 'revenue', 'previous_annual_revenue': 'previous_revenue',
    'cash_and_equivalents': 'cash_balance', 'cash': 'cash_balance', 'credit_score': 'bureau_score',
    'outstanding_debt': 'total_outstanding_debt', 'monthly_obligation': 'total_monthly_obligation',
    'average_balance': 'average_monthly_balance', 'avg_monthly_balance': 'average_monthly_balance',
    'monthly_inflow': 'average_monthly_inflow', 'monthly_outflow': 'average_monthly_outflow',
    'property_value': 'estimated_value', 'collateral_value': 'estimated_value', 'owner': 'owner_name',
}

MONEY_FIELDS = {
    'opening_balance','closing_balance','average_monthly_inflow','average_monthly_outflow','average_monthly_balance','minimum_balance','recurring_emi',
    'revenue','previous_revenue','ebitda','net_profit','cash_balance','current_assets','current_liabilities','total_assets','total_liabilities','total_debt','receivables','inventory','equity',
    'reported_turnover','taxable_income','tax_paid','total_outstanding_debt','total_monthly_obligation','outstanding_principal','emi','total_outstanding','estimated_value'
}
INT_FIELDS = {'negative_balance_days','bounced_transactions','observed_lender_payments','bureau_score','active_facilities','delinquencies_12m','serious_defaults','hard_enquiries_6m','days_past_due'}
PERCENT_FIELDS = {'utilization_percentage'}
BOOL_FIELDS = {'encumbrance'}
DATE_FIELDS = {'filing_date','valuation_date'}


def extract_document(document_id: str, document_type: DocumentType, text: str, llm: GeminiClient | None = None) -> GenericDocumentExtraction:
    expected = FIELDS.get(document_type, [])
    if llm and llm.enabled and expected:
        prompt = f"""Extract underwriting fields from the document. Return JSON only.
Document type: {document_type.value}
Allowed fields only: {expected}
Output format: {{"fields": {{"field_name": {{"value": value, "confidence": 0.0-1.0, "page": 1, "source_text": "short supporting text"}}}}}}
Do not calculate financial ratios. Do not invent missing values. Use null for missing values.
Document:\n{text[:30000]}"""
        try:
            raw = llm.generate_json(prompt)
            fields = _coerce_fields(raw.get('fields', {}), expected)
            if fields:
                confidence = sum(v.confidence for v in fields.values()) / len(fields)
                return GenericDocumentExtraction(document_id=document_id, document_type=document_type,
                    fields=fields, extraction_confidence=confidence, extractor='gemini', model_version=llm.model)
        except Exception as exc:
            logger.warning(
                "gemini_extraction_failed_falling_back "
                "document_id=%s document_type=%s error=%s",
                document_id,
                document_type.value,
                type(exc).__name__,
            )

    fields = _heuristic_extract(text, expected)
    confidence = sum(v.confidence for v in fields.values()) / len(fields) if fields else 0.3
    warnings = [] if fields else ['No structured fields found by heuristic extraction']
    return GenericDocumentExtraction(document_id=document_id, document_type=document_type,
        fields=fields, extraction_confidence=confidence, extractor='heuristic-key-value-v1', warnings=warnings)


def _heuristic_extract(text: str, expected: list[str]) -> dict[str, GenericExtractedField]:
    result: dict[str, GenericExtractedField] = {}
    expected_set = set(expected)
    for line in text.splitlines():
        if ':' not in line:
            continue
        raw_key, raw_value = line.split(':', 1)
        key = re.sub(r'[^a-z0-9]+', '_', raw_key.lower()).strip('_')
        key = ALIASES.get(key, key)
        if key not in expected_set:
            continue
        value = _coerce_value(key, raw_value.strip())
        if value is not None:
            result[key] = GenericExtractedField(value=scalar(value), confidence=0.93, page=1, source_text=line[:3000])
    return result


def _coerce_fields(raw_fields: dict[str, Any], expected: list[str]) -> dict[str, GenericExtractedField]:
    result = {}
    for key, obj in raw_fields.items():
        key = ALIASES.get(key, key)
        if key not in expected:
            continue
        if not isinstance(obj, dict):
            obj = {'value': obj}
        value = _coerce_value(key, obj.get('value'))
        if value is None:
            continue
        result[key] = GenericExtractedField(value=scalar(value), confidence=float(obj.get('confidence', 0.8) or 0.8),
            page=int(obj.get('page', 1) or 1), source_text=str(obj.get('source_text', ''))[:3000] or None)
    return result


def _coerce_value(key: str, value: Any):
    if value is None or value == '':
        return None
    if key in MONEY_FIELDS or key in PERCENT_FIELDS:
        return normalize_number(value)
    if key in INT_FIELDS:
        number = normalize_number(value)
        return int(number) if number is not None else None
    if key in BOOL_FIELDS:
        raw = str(value).strip().lower()
        if raw in {'true','yes','y','1','encumbered'}: return True
        if raw in {'false','no','n','0','none','unencumbered'}: return False
        return None
    if key in DATE_FIELDS:
        return normalize_date(value)
    return str(value).strip() or None
