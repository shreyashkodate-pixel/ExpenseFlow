import json
import logging
from typing import Dict, Any, Optional
import httpx
from .base import BaseAIProvider
from ...core.exceptions import AppException

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI / ChatGPT Adapter using standard Chat Completions endpoint.
    Compatible with OpenAI, Groq, OpenRouter, and self-hosted LLMs.
    """

    def __init__(self, api_key: Optional[str], model: str = "gpt-4o-mini", base_url: Optional[str] = None):
        self.api_key = api_key
        self.model = model or "gpt-4o-mini"
        self.base_url = (base_url or "https://api.openai.com/v1").rstrip("/")

    def _clean_json_string(self, text: str) -> str:
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
                detail="OpenAI API key is not configured. Set AI_API_KEY in environment variables.",
                status_code=503,
                error_code="AI_NOT_CONFIGURED",
            )

        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(endpoint, headers=headers, json=payload)
                if response.status_code != 200:
                    logger.error(f"OpenAI API returned status {response.status_code}: {response.text}")
                    raise AppException(
                        detail=f"OpenAI service error: {response.text[:200]}",
                        status_code=502,
                        error_code="AI_PROVIDER_ERROR",
                    )
                data = response.json()

            content = data["choices"][0]["message"]["content"]
            return json.loads(self._clean_json_string(content))

        except json.JSONDecodeError as je:
            logger.error(f"Failed to parse JSON from OpenAI response: {je}")
            raise AppException(
                detail="Failed to parse structured JSON from OpenAI.",
                status_code=502,
                error_code="AI_JSON_PARSE_ERROR",
            )
        except httpx.RequestError as re:
            logger.error(f"Connection error to OpenAI API: {re}")
            raise AppException(
                detail="Failed to connect to OpenAI service.",
                status_code=503,
                error_code="AI_NETWORK_ERROR",
            )

    def generate_text(self, prompt: str, system_instruction: str) -> str:
        if not self.api_key or not self.api_key.strip():
            raise AppException(
                detail="OpenAI API key is not configured.",
                status_code=503,
                error_code="AI_NOT_CONFIGURED",
            )

        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4,
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(endpoint, headers=headers, json=payload)
                if response.status_code != 200:
                    raise AppException(
                        detail=f"OpenAI error: {response.text[:200]}",
                        status_code=502,
                        error_code="AI_PROVIDER_ERROR",
                    )
                data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenAI generate_text failed: {e}")
            raise AppException(
                detail="Failed to generate text from OpenAI.",
                status_code=502,
                error_code="AI_PROVIDER_ERROR",
            )
