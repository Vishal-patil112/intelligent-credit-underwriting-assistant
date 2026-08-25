"""Central runtime configuration for the end-to-end hackathon solution."""
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / '.env', env_file_encoding='utf-8', case_sensitive=False, extra='ignore'
    )

    app_name: str = 'Intelligent Small Business Credit Underwriting Assistant'
    app_version: str = '1.0.0'
    app_env: Literal['local', 'test', 'dev', 'staging', 'prod'] = 'local'
    log_level: str = 'INFO'

    api_host: str = '0.0.0.0'
    api_port: int = 8000

    llm_provider: str = 'gemini'
    gemini_api_key: str | None = Field(default=None, repr=False)
    gemini_model: str = 'gemini-3.5-flash-lite'
    llm_temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_llm_retries: int = Field(default=2, ge=0, le=10)
    llm_fallback_enabled: bool = True

    database_url: str = f"sqlite:///{(PROJECT_ROOT / 'data' / 'underwriting.db').as_posix()}"
    upload_directory: Path = PROJECT_ROOT / 'data' / 'uploads'
    max_upload_mb: int = Field(default=20, ge=1, le=100)
    tesseract_cmd: str | None = None

    credit_policy_path: Path = PROJECT_ROOT / 'config' / 'credit_policy.yaml'
    risk_scorecard_path: Path = PROJECT_ROOT / 'config' / 'risk_scorecard.yaml'
    revenue_mismatch_tolerance: float = Field(default=0.20, ge=0, le=1)
    low_confidence_threshold: float = Field(default=0.65, ge=0, le=1)
    collateral_max_age_days: int = Field(default=365, ge=1)

    @property
    def gemini_configured(self) -> bool:
        return bool(self.gemini_api_key and self.gemini_api_key.strip())

    def ensure_runtime_directories(self) -> None:
        self.upload_directory.mkdir(parents=True, exist_ok=True)
        (PROJECT_ROOT / 'data').mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
