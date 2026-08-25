from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

Confidence = Annotated[float, Field(ge=0.0, le=1.0)]
NonNegativeMoney = Annotated[Decimal, Field(ge=0)]
PositiveMoney = Annotated[Decimal, Field(gt=0)]
Percentage = Annotated[Decimal, Field(ge=0, le=100)]


class StrictBaseModel(BaseModel):
    """Base model used throughout the project to prevent silent schema drift."""

    model_config = ConfigDict(
        extra='forbid',
        validate_assignment=True,
        str_strip_whitespace=True,
        use_enum_values=False,
    )


class CurrencyCode(str, Enum):
    INR = 'INR'
    USD = 'USD'
    EUR = 'EUR'
    GBP = 'GBP'
    AED = 'AED'


class Severity(str, Enum):
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    CRITICAL = 'CRITICAL'


class DataQualityStatus(str, Enum):
    AVAILABLE = 'AVAILABLE'
    MISSING = 'MISSING'
    STALE = 'STALE'
    LOW_CONFIDENCE = 'LOW_CONFIDENCE'
    CONFLICT = 'CONFLICT'


class Period(StrictBaseModel):
    start_date: date | None = None
    end_date: date | None = None


class VersionInfo(StrictBaseModel):
    name: str
    version: str
    effective_from: datetime | None = None
