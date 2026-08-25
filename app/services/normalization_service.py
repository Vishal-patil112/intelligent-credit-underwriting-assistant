from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation


def normalize_whitespace(value: str | None) -> str | None:
    return re.sub(r'\s+', ' ', value or '').strip() or None


def normalize_name(value: str | None) -> str | None:
    value = normalize_whitespace(value)
    return value.title() if value else None


def normalize_number(value):
    if value is None or value == '':
        return None
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))
    raw = str(value).strip()
    negative = raw.startswith('(') and raw.endswith(')')
    raw = raw.strip('()').replace(',', '').replace('₹', '').replace('$', '').replace('€', '').replace('£', '').strip()
    multiplier = Decimal('1')
    lower = raw.lower()
    if lower.endswith('crore') or lower.endswith('cr'):
        multiplier = Decimal('10000000'); raw = re.sub(r'(?i)\s*(crore|cr)$', '', raw)
    elif lower.endswith('lakh') or lower.endswith('lac'):
        multiplier = Decimal('100000'); raw = re.sub(r'(?i)\s*(lakh|lac)$', '', raw)
    elif lower.endswith('million'):
        multiplier = Decimal('1000000'); raw = re.sub(r'(?i)\s*million$', '', raw)
    raw = raw.replace('%', '').strip()
    try:
        result = Decimal(raw) * multiplier
        return -result if negative else result
    except (InvalidOperation, ValueError):
        return None


def normalize_percentage(value):
    return normalize_number(value)


def normalize_date(value) -> date | None:
    if value is None or value == '':
        return None
    if isinstance(value, date):
        return value
    raw = str(value).strip()
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%b %d, %Y', '%d %b %Y', '%m/%d/%Y'):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            pass
    return None


def scalar(value):
    """Convert Decimal/date recursively into JSON-friendly values."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, list):
        return [scalar(v) for v in value]
    if isinstance(value, dict):
        return {k: scalar(v) for k, v in value.items()}
    return value
