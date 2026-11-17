"""Modèles des documents bruts issus de l'open data AN."""
from datetime import date

from pydantic import BaseModel, Field


class Document(BaseModel):
    """Document brut générique du dossier législatif."""
    type: str = Field(description="proposition | amendement | rapport | debat")
    numero: str
    legislature: str = "17"
    date_depot: date | None = None
    raw: str = Field(description="Contenu texte brut du document")


class Amendement(Document):
    texte_vise: str = Field(description="Numéro du texte de loi visé")
    numero_article: str | None = None
    signataires: list[str] = []
    dispositif: str = Field(description="Texte de l'amendement")
    exposition: str | None = None
    etat: str | None = None
