"""Schémas de sortie de l'extraction (pydantic strict).

Le LLM doit produire exactement ces structures. Tout écart = erreur
d'extraction, comptée dans l'évaluation.
"""
from pydantic import BaseModel, Field


class Article(BaseModel):
    numero: str = Field(description="ex: '1er', '2'")
    titre: str | None = None
    contenu: str
    code_modifie: str | None = Field(default=None, description="Code visé, ex: 'code du travail'")


class PropositionExtraite(BaseModel):
    titre: str
    numero: str
    expose_des_motifs: str
    articles: list[Article]
    signataires: list[str]
    gage: str | None = None


class AmendementExtraite(BaseModel):
    numero: str
    numero_article: str | None = Field(description="Article visé, ex: '1er', 'avant l'article 3'")
    dispositif: str
    exposition: str | None = None
    signataires: list[str]
    sort: str | None = None
