import json
import logging
from typing import Dict, Any, Optional
import httpx
from .base import BaseAIProvider
from ...core.exceptions import AppException

logger = logging.getLogger(__name__)


class ClaudeProvider(BaseAIProvider):
    """
    Anthropic Claude API Adapter using the Messages API.
    Default model: claude-3-5-haiku-20241022
    """

    def __init__(self, api_key: Optional[str], model: str = "claude-3-5-haiku-20241022", base_url: Optional[str] = None):
        self.api_key = api_key
        self.model = model or "claude-3-5-haiku-20241022"
        self.base_url = (base_url or "https://api.anthropic.com/v1").rstrip("/")

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
                detail="Claude API key is not configured. Set AI_API_KEY in environment variables.",
                status_code=503,
                error_code="AI_NOT_CONFIGURED",
            )

        endpoint = f"{self.base_url}/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        json_system = f"{system_instruction}\nCRITICAL: Respond ONLY with valid, raw JSON. Do not include markdown code block tags or introductory/concluding prose."
        payload = {
            "model": self.model,
            "max_tokens": 2048,
            "system": json_system,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(endpoint, headers=headers, json=payload)
                if response.status_code != 200:
                    logger.error(f"Claude API returned status {response.status_code}: {response.text}")
                    raise AppException(
                        detail=f"Claude service error: {response.text[:200]}",
                        status_code=502,
                        error_code="AI_PROVIDER_ERROR",
                    )
                data = response.json()

            content = data["content"][0]["text"]
            return json.loads(self._clean_json_string(content))

        except json.JSONDecodeError as je:
            logger.error(f"Failed to parse JSON from Claude response: {je}")
            raise AppException(
                detail="Failed to parse structured JSON from Claude.",
                status_code=502,
                error_code="AI_JSON_PARSE_ERROR",
            )
        except httpx.RequestError as re:
            logger.error(f"Connection error to Claude API: {re}")
            raise AppException(
                detail="Failed to connect to Claude service.",
                status_code=503,
                error_code="AI_NETWORK_ERROR",
            )

    def generate_text(self, prompt: str, system_instruction: str) -> str:
        if not self.api_key or not self.api_key.strip():
            raise AppException(
                detail="Claude API key is not configured.",
                status_code=503,
                error_code="AI_NOT_CONFIGURED",
            )

        endpoint = f"{self.base_url}/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": 2048,
            "system": system_instruction,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4,
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(endpoint, headers=headers, json=payload)
                if response.status_code != 200:
                    raise AppException(
                        detail=f"Claude error: {response.text[:200]}",
                        status_code=502,
                        error_code="AI_PROVIDER_ERROR",
                    )
                data = response.json()
            return data["content"][0]["text"]
        except Exception as e:
            logger.error(f"Claude generate_text failed: {e}")
            raise AppException(
                detail="Failed to generate text from Claude.",
                status_code=502,
                error_code="AI_PROVIDER_ERROR",
            )
