from app.config import Settings


def test_default_llm_provider_is_gemini() -> None:
    settings = Settings(_env_file=None)
    assert settings.llm_provider == "gemini"
    assert settings.gemini_model


def test_temperature_is_deterministic_by_default() -> None:
    settings = Settings(_env_file=None)
    assert settings.llm_temperature == 0.0
