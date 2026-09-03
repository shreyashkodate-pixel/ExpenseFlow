import logging
from .base import BaseAIProvider
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from .claude_provider import ClaudeProvider
from ...core.config import settings
from ...core.exceptions import AppException

logger = logging.getLogger(__name__)


def get_ai_provider() -> BaseAIProvider:
    """
    Factory function instantiating the active AI provider based on environment variables.
    Enables instant switching between Gemini, OpenAI, Claude, etc. with zero code changes.
    """
    provider_name = (settings.AI_PROVIDER or "gemini").strip().lower()

    if provider_name == "gemini":
        model = settings.AI_MODEL if settings.AI_MODEL and "gemini" in settings.AI_MODEL else "gemini-3.6-flash"
        return GeminiProvider(
            api_key=settings.AI_API_KEY,
            model=model,
            base_url=settings.AI_BASE_URL,
        )

    elif provider_name in ("openai", "chatgpt"):
        model = settings.AI_MODEL if settings.AI_MODEL and ("gpt" in settings.AI_MODEL or "o1" in settings.AI_MODEL) else "gpt-4o-mini"
        return OpenAIProvider(
            api_key=settings.AI_API_KEY,
            model=model,
            base_url=settings.AI_BASE_URL,
        )

    elif provider_name in ("claude", "anthropic"):
        model = settings.AI_MODEL if settings.AI_MODEL and "claude" in settings.AI_MODEL else "claude-3-5-haiku-20241022"
        return ClaudeProvider(
            api_key=settings.AI_API_KEY,
            model=model,
            base_url=settings.AI_BASE_URL,
        )

    else:
        logger.error(f"Unsupported AI provider '{provider_name}' configured in environment variables.")
        raise AppException(
            detail=f"Unsupported AI provider '{provider_name}'. Supported options are 'gemini', 'openai', 'claude'.",
            status_code=500,
            error_code="INVALID_AI_PROVIDER",
        )
