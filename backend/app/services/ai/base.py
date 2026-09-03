from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseAIProvider(ABC):
    """
    Abstract Base Class for AI Large Language Model providers.
    Enforces a strict contract allowing seamless switching across Gemini, OpenAI, Claude, etc.
    """

    @abstractmethod
    def generate_structured_json(self, prompt: str, system_instruction: str) -> Dict[str, Any]:
        """
        Send prompt to the AI provider and guarantee a parsed JSON dictionary response.
        """
        pass

    @abstractmethod
    def generate_text(self, prompt: str, system_instruction: str) -> str:
        """
        Send prompt to the AI provider and return the raw textual response.
        """
        pass
