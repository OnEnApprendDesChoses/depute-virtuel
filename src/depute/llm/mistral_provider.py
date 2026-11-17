"""Implémentation Mistral du LLMProvider (principal)."""
import os

from pydantic import BaseModel

from .provider import LLMProvider, LLMResponse

DEFAULT_MODEL = "mistral-large-latest"


class MistralProvider(LLMProvider):
    name = "mistral"

    def __init__(self, model: str = DEFAULT_MODEL, api_key: str | None = None):
        from mistralai import Mistral  # import différé : facilite les tests

        self.model = model
        self.client = Mistral(api_key=api_key or os.environ["MISTRAL_API_KEY"])

    def complete(self, system: str, user: str, temperature: float = 0.0) -> LLMResponse:
        resp = self.client.chat.complete(
            model=self.model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=temperature,
        )
        return LLMResponse(text=resp.choices[0].message.content or "")

    def complete_structured(self, system: str, user: str, schema: type[BaseModel]) -> BaseModel:
        resp = self.client.chat.parse(
            model=self.model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            response_format=schema,
        )
        return resp.choices[0].message.parsed
