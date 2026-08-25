from __future__ import annotations

import json
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class GeminiClient:
    """Thin Gemini adapter. Deterministic business logic never depends on this client."""

    def __init__(self):
        self.enabled = settings.gemini_configured
        self.model = settings.gemini_model
        self._client = None
        if self.enabled:
            from google import genai
            self._client = genai.Client(api_key=settings.gemini_api_key)

    def generate_json(self, prompt: str) -> dict:
        if not self.enabled or self._client is None:
            raise RuntimeError('Gemini is not configured')
        from google.genai import types
        response = self._client.models.generate_content(
        model=self.model,
        contents=prompt,
        config=types.GenerateContentConfig(
        temperature=settings.llm_temperature,
        response_mime_type="application/json",
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True, ),
        ),
        )
        text = (response.text or '').strip()
        return json.loads(text)

    def generate_text(self, prompt: str) -> str:
        if not self.enabled or self._client is None:
            raise RuntimeError('Gemini is not configured')
        from google.genai import types
        response = self._client.models.generate_content(
        model=self.model,
        contents=prompt,
        config=types.GenerateContentConfig(
        temperature=settings.llm_temperature,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True,
        ), ),
        )
        return (response.text or '').strip()
