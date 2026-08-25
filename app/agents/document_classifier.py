from __future__ import annotations

import re

from app.llm import GeminiClient
from app.schemas.document import DocumentClassification, DocumentType


RULES: list[tuple[DocumentType, tuple[str, ...]]] = [
    (DocumentType.BANK_STATEMENT, ('bank statement', 'account number', 'opening balance', 'closing balance', 'monthly inflow')),
    (DocumentType.FINANCIAL_STATEMENT, ('financial statement', 'profit and loss', 'balance sheet', 'ebitda', 'current assets')),
    (DocumentType.TAX_RETURN, ('tax return', 'taxable income', 'reported turnover', 'tax paid', 'gst return')),
    (DocumentType.CREDIT_REPORT, ('credit report', 'bureau score', 'credit score', 'hard enquiries', 'delinquencies')),
    (DocumentType.EXISTING_LOAN_STATEMENT, ('loan statement', 'outstanding principal', 'monthly obligation', 'emi', 'lender')),
    (DocumentType.COLLATERAL_DOCUMENT, ('collateral', 'property valuation', 'estimated value', 'encumbrance', 'valuation date')),
    (DocumentType.BUSINESS_REGISTRATION, ('certificate of incorporation', 'business registration', 'registration number')),
    (DocumentType.IDENTITY_DOCUMENT, ('identity document', 'aadhaar', 'passport', 'pan card')),
]


def classify_document(document_id: str, file_name: str, text: str, llm: GeminiClient | None = None) -> DocumentClassification:
    haystack = f'{file_name}\n{text[:8000]}'.lower().replace('_', ' ')
    best_type = DocumentType.UNKNOWN
    best_score = 0
    matches: list[str] = []
    for doc_type, clues in RULES:
        found = [clue for clue in clues if clue in haystack]
        if len(found) > best_score:
            best_score = len(found); best_type = doc_type; matches = found
    if best_score >= 1:
        confidence = min(0.65 + 0.08 * best_score, 0.97)
        return DocumentClassification(
            document_id=document_id, document_type=best_type, confidence=confidence,
            reason=f"Matched deterministic clues: {', '.join(matches[:4])}", classifier='rules-v1'
        )

    if llm and llm.enabled:
        prompt = f"""Classify this small-business underwriting document into exactly one of:
{', '.join(t.value for t in DocumentType)}.
Return JSON only with keys document_type, confidence, reason.
Filename: {file_name}
Document text:\n{text[:12000]}"""
        try:
            result = llm.generate_json(prompt)
            doc_type = DocumentType(str(result.get('document_type', 'UNKNOWN')).upper())
            return DocumentClassification(document_id=document_id, document_type=doc_type,
                confidence=float(result.get('confidence', 0.7)), reason=str(result.get('reason', 'Gemini classification'))[:1000],
                classifier='gemini', model_version=llm.model)
        except Exception as exc:
            return DocumentClassification(document_id=document_id, document_type=DocumentType.UNKNOWN,
                confidence=0.2, reason=f'Classification fallback after Gemini error: {type(exc).__name__}', classifier='fallback')

    return DocumentClassification(document_id=document_id, document_type=DocumentType.UNKNOWN,
        confidence=0.2, reason='No deterministic clue and Gemini is not configured', classifier='fallback')
