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

        endpoint = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"

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

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(endpoint, json=payload)
                if response.status_code != 200:
                    logger.error(f"Gemini API returned status {response.status_code}: {response.text}")
                    raise AppException(
                        detail=f"Google Gemini AI service error: {response.text[:200]}",
                        status_code=502,
                        error_code="AI_PROVIDER_ERROR",
                    )
                data = response.json()

            candidates = data.get("candidates", [])
            if not candidates:
                raise AppException(
                    detail="Google Gemini returned empty candidates.",
                    status_code=502,
                    error_code="AI_EMPTY_RESPONSE",
                )

            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts or "text" not in parts[0]:
                raise AppException(
                    detail="Invalid response structure from Gemini API.",
                    status_code=502,
                    error_code="AI_MALFORMED_RESPONSE",
                )

            raw_text = parts[0]["text"]
            cleaned = self._clean_json_string(raw_text)
            return json.loads(cleaned)

        except json.JSONDecodeError as je:
            logger.error(f"Failed to parse JSON from Gemini response: {je}")
            raise AppException(
                detail="Failed to parse structured JSON from Gemini AI.",
                status_code=502,
                error_code="AI_JSON_PARSE_ERROR",
            )
        except httpx.RequestError as re:
            logger.error(f"Connection error to Gemini API: {re}")
            raise AppException(
                detail="Failed to connect to Google Gemini AI service.",
                status_code=503,
                error_code="AI_NETWORK_ERROR",
            )

    def generate_text(self, prompt: str, system_instruction: str) -> str:
        if not self.api_key or not self.api_key.strip():
            raise AppException(
                detail="Google Gemini API key is not configured.",
                status_code=503,
                error_code="AI_NOT_CONFIGURED",
            )

        endpoint = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.4}
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(endpoint, json=payload)
                if response.status_code != 200:
                    raise AppException(
                        detail=f"Gemini API error: {response.text[:200]}",
                        status_code=502,
                        error_code="AI_PROVIDER_ERROR",
                    )
                data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            logger.error(f"Gemini generate_text failed: {e}")
            raise AppException(
                detail="Failed to generate text from Gemini AI.",
                status_code=502,
                error_code="AI_PROVIDER_ERROR",
            )
