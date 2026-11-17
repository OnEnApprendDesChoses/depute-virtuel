"""Génération de questions de compréhension sur un texte de loi.

La mécanique historique du projet « député virtuel » : on ne peut débattre
que ce qu'on a compris. Le LLM génère des questions de compréhension sur
chaque article ; l'utilisateur y répond ; la réponse est évaluée.
"""
from pydantic import BaseModel, Field

from ..llm.provider import LLMProvider

QUESTIONS_SYSTEM = """Tu génères des questions de compréhension sur un texte
de loi. Les questions doivent : porter sur le contenu exact du texte, être
vérifiables par lecture du texte seul, ne pas demander d'opinion, et être
formulées de façon neutre."""


class Question(BaseModel):
    enonce: str
    reponse_attendue: str = Field(description="Réponse attendue, basée sur le texte seul")
    article: str


def generer_questions(provider: LLMProvider, article_texte: str, article_numero: str, n: int = 3) -> list[Question]:
    """Génère n questions de compréhension sur un article. TODO semaine 3."""
    raise NotImplementedError
