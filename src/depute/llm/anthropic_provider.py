"""Implémentation Anthropic du LLMProvider (comparaison / arbitrage coût-qualité).

Seconde implémentation volontaire : démontre que le pipeline n'est pas
verrouillé sur un fournisseur. Sortie structurée via tool use + validation
pydantic manuelle.
"""
import os

from pydantic import BaseModel

from .provider import LLMProvider, LLMResponse

DEFAULT_MODEL = "claude-sonnet-4-5"


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, model: str = DEFAULT_MODEL, api_key: str | None = None):
        import anthropic

        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key or os.environ["ANTHROPIC_API_KEY"])

    def complete(self, system: str, user: str, temperature: float = 0.0) -> LLMResponse:
        resp = self.client.messages.create(
            model=self.model, max_tokens=4096, system=system, temperature=temperature,
            messages=[{"role": "user", "content": user}],
        )
        return LLMResponse(text="".join(b.text for b in resp.content if b.type == "text"))

    def complete_structured(self, system: str, user: str, schema: type[BaseModel]) -> BaseModel:
        # TODO semaine 1 : passer le schéma pydantic en tool use et valider.
        raise NotImplementedError
