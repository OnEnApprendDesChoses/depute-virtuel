"""Extraction LLM structurée des documents législatifs.

Règles :
- temperature=0, output structuré strict (schémas pydantic).
- Cache : un document déjà extrait n'est JAMAIS renvoyé au LLM
  (coût et reproductibilité).
- Les prompts sont versionnés comme du code.
"""
from ..llm.provider import LLMProvider
from .schemas import AmendementExtraite, PropositionExtraite

EXTRACTION_SYSTEM = """Tu es un assistant d'extraction de documents législatifs.
Tu extrais fidèlement les informations du document fourni, sans en ajouter,
sans en omettre, sans reformuler. Si une information est absente, renvoie
null. Réponds uniquement via la structure imposée."""


def extraire_proposition(provider: LLMProvider, texte_brut: str) -> PropositionExtraite:
    """Extrait une proposition de loi en structure PropositionExtraite."""
    return provider.complete_structured(
        system=EXTRACTION_SYSTEM,
        user=f"Extrait structuré de cette proposition de loi :\n\n{texte_brut}",
        schema=PropositionExtraite,
    )


def extraire_amendement(provider: LLMProvider, amendement_brut: str) -> AmendementExtraite:
    """Extrait un amendement en structure AmendementExtraite."""
    return provider.complete_structured(
        system=EXTRACTION_SYSTEM,
        user=f"Extrait structuré de cet amendement :\n\n{amendement_brut}",
        schema=AmendementExtraite,
    )
