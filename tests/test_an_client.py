"""Tests du client open data AN.

- download() : mock réseau via respx, aucun appel réel (cache disque vérifié).
- lire_amendements_zip() : zip fabriqué en test, au format réel 17e observé
  dans Amendements.json.zip (arborescence `<texteLegislatifRef>/<uid>.json`,
  champs uid / identification / examenRef / texteLegislatifRef / signataires /
  pointeurFragmentTexte / corps.contenuAuteur / sort).
"""

import io
import json
import zipfile
from pathlib import Path

import httpx
import pytest
import respx

from src.depute.ingestion.an_client import (
    AMENDEMENTS_JSON_URL,
    download,
    lire_amendements_zip,
    parse_amendements,
)

# Fixture au format réel 17e (structure documentée par l'open data AN et des
# extraits publiés, ex. AMANR5L17PO838901BTC0633P0D1N000078) ; refs adaptées au
# dossier pilote DLR5L17N51987 (textes PIONANR5L17B1673 / PIONANR5L17BTC2335).
AMENDEMENT_PILOTE_1 = {
    "uid": "AMANR5L17PO838901B1673P0D1N000001",
    "legislature": "17",
    "identification": {
        "numeroLong": "1",
        "numeroOrdreDepot": "1",
        "prefixeOrganeExamen": "AN",
        "numeroRect": "0",
    },
    "examenRef": "EXANR5L17PO838901B1673P0D1",
    "texteLegislatifRef": "PIONANR5L17B1673",
    "signataires": {
        "auteur": {
            "typeAuteur": "Député",
            "acteurRef": "PA793940",
            "groupePolitiqueRef": "PO845407",
        },
        "libelle": "Mme Billon",
        "cosignataires": {"cosignataire": [{"libelle": "M. Marseille"}]},
    },
    "pointeurFragmentTexte": {
        "division": {
            "titre": "Article 1er",
            "articleDesignation": "ARTICLE 1ER",
            "type": "ARTICLE",
        },
        "alinea": {"numero": "2", "alineaDesignation": "Alinéa 2"},
    },
    "corps": {
        "contenuAuteur": {
            "dispositif": "<p>Après l'article 1er, insérer un article ainsi rédigé :</p>",
            "exposeSommaire": "<p>Amendement de précision.</p>",
        }
    },
    "sort": {"code": "rejeté"},
    "dateDepot": "2026-01-05",
}

AMENDEMENT_PILOTE_2 = {
    "uid": "AMANR5L17PO838901BTC2335P0D1N000042",
    "legislature": "17",
    "identification": {"numeroLong": "42", "numeroOrdreDepot": "42", "prefixeOrganeExamen": "AN"},
    "examenRef": "EXANR5L17PO838901BTC2335P0D1",
    "texteLegislatifRef": "PIONANR5L17BTC2335",
    "signataires": {
        "auteur": {"typeAuteur": "Député", "acteurRef": "PA000001"},
        "libelle": "M. Portes",
    },
    "pointeurFragmentTexte": {"division": {"titre": "Article 2", "type": "ARTICLE"}},
    "corps": {"contenuAuteur": {"dispositif": "<p>Supprimer cet article.</p>"}},
}

AMENDEMENT_AUTRE_DOSSIER = {
    "uid": "AMANR5L17PO000000B0482P0D1N000001",
    "legislature": "17",
    "identification": {"numeroLong": "1"},
    "examenRef": "EXANR5L17PO000000B0482P0D1",
    "texteLegislatifRef": "PIONANR5L17B0482",  # autre dossier : doit être exclu
    "corps": {"contenuAuteur": {"dispositif": "<p>...</p>"}},
}


def _fabriquer_zip_bytes(fichiers: dict[str, object]) -> bytes:
    tampon = io.BytesIO()
    with zipfile.ZipFile(tampon, "w") as zf:
        for nom, contenu in fichiers.items():
            if isinstance(contenu, dict):
                contenu = json.dumps(contenu, ensure_ascii=False)
            zf.writestr(nom, contenu)
    return tampon.getvalue()


def _fabriquer_zip(path: Path, fichiers: dict[str, object]) -> Path:
    path.write_bytes(_fabriquer_zip_bytes(fichiers))
    return path


FICHIERS_ZIP = {
    "PIONANR5L17B1673/AMANR5L17PO838901B1673P0D1N000001.json": AMENDEMENT_PILOTE_1,
    "PIONANR5L17BTC2335/AMANR5L17PO838901BTC2335P0D1N000042.json": AMENDEMENT_PILOTE_2,
    "PIONANR5L17B0482/AMANR5L17PO000000B0482P0D1N000001.json": AMENDEMENT_AUTRE_DOSSIER,
    "PIONANR5L17B0482/lisezmoi.txt": "entrée non JSON : ignorée",
}


def test_lire_amendements_zip_filtre_et_aplatit(tmp_path):
    zip_path = _fabriquer_zip(tmp_path / "Amendements.json.zip", FICHIERS_ZIP)

    amendements = lire_amendements_zip(zip_path)

    # Seuls les 2 amendements du dossier pilote sont gardés, triés par texte puis numéro
    assert [a["uid"] for a in amendements] == [
        "AMANR5L17PO838901B1673P0D1N000001",
        "AMANR5L17PO838901BTC2335P0D1N000042",
    ]
    am1 = amendements[0]
    assert am1["numero"] == "1"
    assert am1["texte_ref"] == "PIONANR5L17B1673"
    assert am1["examen_ref"] == "EXANR5L17PO838901B1673P0D1"
    assert am1["numero_article"] == "Article 1er"
    assert am1["alinea"] == "2"
    assert am1["signataires"] == ["Mme Billon", "M. Marseille"]
    # HTML embarqué aplati en texte brut
    assert am1["dispositif"] == "Après l'article 1er, insérer un article ainsi rédigé :"
    assert am1["exposition"] == "Amendement de précision."
    assert am1["sort"] == "rejeté"
    assert am1["date_depot"] == "2026-01-05"
    # JSON brut conservé pour l'audit
    assert am1["brut"]["uid"] == am1["uid"]
    # Champs absents -> valeurs par défaut sûres (pas d'exception)
    am2 = amendements[1]
    assert am2["alinea"] is None
    assert am2["exposition"] == ""
    assert am2["sort"] is None


@respx.mock
def test_download_met_en_cache_et_ne_retelecharge_pas(tmp_path):
    route = respx.get(AMENDEMENTS_JSON_URL).mock(
        return_value=httpx.Response(200, content=b"contenu-zip")
    )

    p1 = download(AMENDEMENTS_JSON_URL, tmp_path)
    p2 = download(AMENDEMENTS_JSON_URL, tmp_path)

    assert p1 == p2 == tmp_path / "Amendements.json.zip"
    assert p1.read_bytes() == b"contenu-zip"
    assert route.call_count == 1  # jamais re-télécharger un fichier déjà en cache
    assert list(tmp_path.glob("*.part")) == []  # pas de fichier partiel laissé


@respx.mock
def test_download_erreur_http_ne_laisse_pas_de_fichier_partiel(tmp_path):
    respx.get(AMENDEMENTS_JSON_URL).mock(return_value=httpx.Response(404))

    with pytest.raises(httpx.HTTPStatusError):
        download(AMENDEMENTS_JSON_URL, tmp_path)

    assert not (tmp_path / "Amendements.json.zip").exists()
    assert list(tmp_path.glob("*.part")) == []


@respx.mock
def test_parse_amendements_de_bout_en_bout_sans_reseau(tmp_path):
    """parse_amendements : téléchargement mocké (zip réel en mémoire) + filtre
    dossier pilote. Aucun appel réseau réel."""
    respx.get(AMENDEMENTS_JSON_URL).mock(
        return_value=httpx.Response(200, content=_fabriquer_zip_bytes(FICHIERS_ZIP))
    )

    amendements = parse_amendements(cache_dir=tmp_path / "data")

    assert len(amendements) == 2
    assert {a["texte_ref"] for a in amendements} == {"PIONANR5L17B1673", "PIONANR5L17BTC2335"}
    # Le zip a bien été mis en cache local
    assert (tmp_path / "data" / "Amendements.json.zip").exists()
