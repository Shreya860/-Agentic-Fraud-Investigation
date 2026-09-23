import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()


class OllamaLLM:
    """Small wrapper around the local Ollama API."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
    ):
        self.base_url = (
            base_url
            or os.getenv("LLM_BASE_URL")
            or "http://localhost:11434"
        ).rstrip("/")

        self.model = (
            model
            or os.getenv("LLM_MODEL")
            or "qwen3:4b"
        )

        self.timeout = int(
            os.getenv("LLM_TIMEOUT", "300")
        )

        self.num_predict = int(
            os.getenv("LLM_MAX_TOKENS", "256")
        )

    def is_available(self) -> bool:
        """Check whether the configured Ollama model is available."""

        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )

            response.raise_for_status()

            models = response.json().get("models", [])

            return any(
                model.get("name") == self.model
                for model in models
            )

        except (requests.RequestException, ValueError):
            return False

    def generate(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.2,
        num_predict: int | None = None,
    ) -> str:
        """
        Generate a response using Ollama.

        Qwen3 reasoning is enabled so Ollama can separate:
            thinking -> internal reasoning
            response -> final answer

        Only the final response is returned.
        """

        max_tokens = (
            num_predict
            if num_predict is not None
            else self.num_predict
        )

        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "think": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        if system:
            payload["system"] = system

        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

        result = str(
            data.get("response", "")
        ).strip()

        if not result:
            raise RuntimeError(
                "Qwen did not produce a final response. "
                "The generation may have exhausted its token budget "
                "during reasoning."
            )

        return result


def get_llm() -> OllamaLLM:
    """Return the configured local Ollama LLM."""

    return OllamaLLM()