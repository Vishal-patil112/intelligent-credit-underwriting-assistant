from decimal import Decimal
from app.services.normalization_service import normalize_date, normalize_number


def test_money_normalization():
    assert normalize_number('₹ 12,50,000') == Decimal('1250000')
    assert normalize_number('(20,000)') == Decimal('-20000')
    assert normalize_number('1.5 crore') == Decimal('15000000.0')


def test_date_normalization():
    assert normalize_date('31/03/2026').isoformat() == '2026-03-31'
