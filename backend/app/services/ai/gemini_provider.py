import json
import re
import logging
from typing import Dict, Any, Optional
import httpx
from .base import BaseAIProvider
from ...core.exceptions import AppException

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    """
    Google Gemini API Adapter using standard HTTPS REST calls.
    Default model: gemini-3.6-flash
    """

    def __init__(self, api_key: Optional[str], model: str = "gemini-3.6-flash", base_url: Optional[str] = None):
        self.api_key = api_key
        # Automatically upgrade deprecated model names (gemini-1.5-flash, gemini-2.5-flash) to active gemini-3.6-flash
        raw_model = (model or "gemini-3.6-flash").strip()
        if raw_model in ("gemini-1.5-flash", "gemini-2.5-flash"):
            self.model = "gemini-3.6-flash"
        else:
            self.model = raw_model
        self.base_url = (base_url or "https://generativelanguage.googleapis.com/v1beta").rstrip("/")

    def _clean_json_string(self, text: str) -> str:
        """Strip markdown code blocks if returned by the model."""
        clean = text.strip()
        if clean.startswith("```json"):
            clean = clean[7:]
        elif clean.startswith("```"):
            clean = clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]
        return clean.strip()

    def generate_structured_json(self, prompt: str, system_instruction: str) -> Dict[str, Any]:
        if not self.api_key or not self.api_key.strip():
            raise AppException(
                detail="Google Gemini API key is not configured. Set AI_API_KEY in environment variables.",
                status_code=503,
                error_code="AI_NOT_CONFIGURED",
            )

        payload = {
            "systemInstruction": {
                "parts": [{"text": system_instruction}]
            },
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json",
            }
        }

        candidate_models = [self.model]
        for alt in ("gemini-3.5-flash", "gemini-3.7-flash", "gemini-3.6-flash"):
            if alt not in candidate_models:
                candidate_models.append(alt)

        last_error = None
        for model_name in candidate_models:
            endpoint = f"{self.base_url}/models/{model_name}:generateContent?key={self.api_key}"
            try:
                with httpx.Client(timeout=30.0) as client:
                    response = client.post(endpoint, json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        candidates = data.get("candidates", [])
                        if not candidates:
                            continue
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if not parts or "text" not in parts[0]:
                            continue
                        raw_text = parts[0]["text"]
                        cleaned = self._clean_json_string(raw_text)
                        return json.loads(cleaned)
                    elif response.status_code in (429, 404, 500, 503):
                        logger.warning(f"Gemini model {model_name} returned {response.status_code}. Trying next available model...")
                        last_error = response.text
                        continue
                    else:
                        logger.error(f"Gemini API returned status {response.status_code}: {response.text}")
                        raise AppException(
                            detail=f"Google Gemini AI service error: {response.text[:200]}",
                            status_code=502,
                            error_code="AI_PROVIDER_ERROR",
                        )
            except (json.JSONDecodeError, httpx.RequestError) as ex:
                last_error = str(ex)
                continue

        raise AppException(
            detail=f"All Gemini models exhausted or unavailable: {last_error}",
            status_code=502,
            error_code="AI_PROVIDER_ERROR",
        )

    def generate_text(self, prompt: str, system_instruction: str) -> str:
        if not self.api_key or not self.api_key.strip():
            raise AppException(
                detail="Google Gemini API key is not configured.",
                status_code=503,
                error_code="AI_NOT_CONFIGURED",
            )

        payload = {
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.4}
        }

        candidate_models = [self.model]
        for alt in ("gemini-3.5-flash", "gemini-3.7-flash", "gemini-3.6-flash"):
            if alt not in candidate_models:
                candidate_models.append(alt)

        last_error = None
        for model_name in candidate_models:
            endpoint = f"{self.base_url}/models/{model_name}:generateContent?key={self.api_key}"
            try:
                with httpx.Client(timeout=30.0) as client:
                    response = client.post(endpoint, json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        candidates = data.get("candidates", [])
                        if not candidates:
                            continue
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if not parts or "text" not in parts[0]:
                            continue
                        return str(parts[0]["text"]).strip()
                    elif response.status_code in (429, 404, 500, 503):
                        last_error = response.text
                        continue
                    else:
                        raise AppException(
                            detail=f"Gemini API error: {response.text[:200]}",
                            status_code=502,
                            error_code="AI_PROVIDER_ERROR",
                        )
            except Exception as ex:
                last_error = str(ex)
                continue

        logger.error(f"Gemini generate_text failed across models: {last_error}")
        raise AppException(
            detail="Failed to generate text from Gemini AI.",
            status_code=502,
            error_code="AI_PROVIDER_ERROR",
        )
