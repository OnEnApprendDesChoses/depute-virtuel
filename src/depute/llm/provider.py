"""Abstraction LLMProvider : le pipeline n'est jamais couplé à un fournisseur."""
from abc import ABC, abstractmethod

from pydantic import BaseModel


class LLMResponse(BaseModel):
    text: str


class LLMProvider(ABC):
    """Interface unique. Deux implémentations : Mistral (principal), Anthropic."""

    name: str = "base"

    @abstractmethod
    def complete(self, system: str, user: str, temperature: float = 0.0) -> LLMResponse:
        """Appel de complétion simple. temperature=0 par défaut : on fait de
        l'extraction, pas de la création."""

    @abstractmethod
    def complete_structured(self, system: str, user: str, schema: type[BaseModel]) -> BaseModel:
        """Appel avec sortie structurée validée par un schéma pydantic."""
