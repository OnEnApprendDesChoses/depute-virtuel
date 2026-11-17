"""Règles de cohérence : 100% testables sans LLM."""
from src.depute.extraction.schemas import AmendementExtraite, Article, PropositionExtraite
from src.depute.extraction.verification import verifier_amendement, verifier_proposition


def prop_exemple() -> PropositionExtraite:
    return PropositionExtraite(
        titre="PDL exemple", numero="1673", expose_des_motifs="…",
        articles=[Article(numero="1er", contenu="Contenu article 1er")],
        signataires=["A. Billon", "H. Marseille"],
    )


def test_amendement_valide_sans_probleme():
    prop = prop_exemple()
    am = AmendementExtraite(
        numero="AM1", numero_article="1er", dispositif="Insérer …", signataires=["X"]
    )
    assert verifier_amendement(am, prop) == []


def test_amendement_article_inconnu_detecte():
    prop = prop_exemple()
    am = AmendementExtraite(
        numero="AM2", numero_article="99", dispositif="Supprimer …", signataires=["X"]
    )
    problemes = verifier_amendement(am, prop)
    assert any(p.regle == "R3_article_inconnu" for p in problemes)


def test_amendement_dispositif_vide_detecte():
    prop = prop_exemple()
    am = AmendementExtraite(numero="AM3", numero_article="1er", dispositif="  ", signataires=["X"])
    assert any(p.regle == "R1_dispositif_vide" for p in verifier_amendement(am, prop))


def test_proposition_sans_article_detectee():
    prop = prop_exemple().model_copy(update={"articles": []})
    assert any(p.regle == "R4_sans_article" for p in verifier_proposition(prop))
