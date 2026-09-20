"""
LLM client.

Why wrapped: the rest of the codebase calls `LLMClient.generate(...)`
and never imports the Groq SDK directly. If we ever swap providers
(OpenAI, Anthropic, a local model via Ollama), only this one file
changes -- services, prompts, and API routes are untouched.
"""
from groq import Groq

from app.config import get_settings

settings = get_settings()


class LLMClient:
    def __init__(self) -> None:
        self._client = Groq(api_key=settings.groq_api_key)
        self._model = settings.llm_model

    def generate(self, system_prompt: str, user_prompt: str, *, temperature: float = 0.7) -> str:
        """
        Sends a single-turn chat completion request and returns plain text.
        Raises on failure, or if the model returns empty content, so callers
        (services) can retry or translate this into a clean API response
        instead of silently passing an empty string through to the UI.

        reasoning_effort="low" and a larger max_tokens are set because
        reasoning-capable models (e.g. openai/gpt-oss-20b on Groq) spend
        part of the token budget on hidden "thinking" tokens before writing
        the final answer -- for a short interview question, a high
        reasoning effort or a too-small max_tokens can consume the whole
        budget before any visible answer is produced.
        """
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=1024,
                reasoning_effort="low",
            )
        except TypeError:
            # Fallback for models/SDK versions that don't accept
            # reasoning_effort as a kwarg -- retry without it rather than
            # failing the whole request over an optional parameter.
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=1024,
            )

        content = (response.choices[0].message.content or "").strip()
        if not content:
            raise RuntimeError(
                "LLM returned an empty response (likely truncated by the "
                "token limit during internal reasoning). Try again."
            )
        return content


_llm_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    # Lazy singleton: avoids constructing the Groq client (and validating
    # the API key) at import time, e.g. during tests that don't need it.
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
