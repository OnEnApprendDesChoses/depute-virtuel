"""Règles de cohérence : du code pur, zéro LLM, 100% testable.

Le LLM extrait, le code vérifie. Chaque règle retourne un problème typé ;
c'est ce qui alimente les métriques de faux positifs/négatifs de l'éval.
"""
from dataclasses import dataclass

from .schemas import AmendementExtraite, PropositionExtraite

VALID_ARTICLE_REPR = {"1er", "2", "3", "4", "5", "6", "7", "8", "9"}


@dataclass
class Probleme:
    regle: str
    message: str
    document: str


def verifier_amendement(am: AmendementExtraite, prop: PropositionExtraite) -> list[Probleme]:
    """Vérifie un amendement contre la proposition qu'il modifie."""
    problemes: list[Probleme] = []

    # R1 : le dispositif ne doit pas être vide
    if not am.dispositif.strip():
        problemes.append(Probleme("R1_dispositif_vide", "Dispositif vide", am.numero))

    # R2 : au moins un signataire
    if not am.signataires:
        problemes.append(Probleme("R2_sans_signataire", "Aucun signataire", am.numero))

    # R3 : l'article visé doit exister dans la proposition
    if am.numero_article and am.numero_article not in {a.numero for a in prop.articles}:
        problemes.append(
            Probleme("R3_article_inconnu", f"Article visé '{am.numero_article}' absent", am.numero)
        )

    return problemes


def verifier_proposition(prop: PropositionExtraite) -> list[Probleme]:
    """Vérifie la cohérence interne d'une proposition extraite."""
    problemes: list[Probleme] = []

    # R4 : au moins un article
    if not prop.articles:
        problemes.append(Probleme("R4_sans_article", "Aucun article extrait", prop.numero))

    # R5 : pas de numéro d'article en doublon
    numeros = [a.numero for a in prop.articles]
    for n in sorted(set(numeros) - {x for x in numeros if numeros.count(x) == 1}):
        problemes.append(Probleme("R5_article_duplique", f"Article '{n}' en doublon", prop.numero))

    # R6 : chaque article a un contenu non vide
    for a in prop.articles:
        if not a.contenu.strip():
            problemes.append(Probleme("R6_article_vide", f"Article '{a.numero}' vide", prop.numero))

    return problemes
