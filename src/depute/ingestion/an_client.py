"""Client open data de l'Assemblée nationale.

Télécharge les jeux de données (XML/JSON zippés) et les met en cache local.
Sources : https://data.assemblee-nationale.fr/

Jeux utiles (17e législature), URLs relevées sur data.assemblee-nationale.fr
(inventaire du dossier pilote : eval/reports/volumes_dossier_pilote.md) :
- Amendements de toute la législature, groupés par texte de loi, un fichier
  JSON par amendement dans le zip (arborescence `<texteLegislatifRef>/<uid>.json`) :
  /static/openData/repository/17/loi/amendements_div_legis/Amendements.json.zip
  (idem en XML : Amendements.xml.zip)
- Dossiers législatifs : /travaux-parlementaires/dossiers-legislatifs
- Comptes rendus des débats : /travaux-parlementaires/comptes-rendus
"""

import json
import zipfile
from html.parser import HTMLParser
from pathlib import Path

import httpx

BASE_URL = "https://data.assemblee-nationale.fr"
CACHE_DIR = Path("data")  # hors git (voir .gitignore)

# URLs relevées sur https://data.assemblee-nationale.fr/travaux-parlementaires/amendements/tous-les-amendements
AMENDEMENTS_JSON_URL = (
    f"{BASE_URL}/static/openData/repository/17/loi/amendements_div_legis/Amendements.json.zip"
)
AMENDEMENTS_XML_URL = (
    f"{BASE_URL}/static/openData/repository/17/loi/amendements_div_legis/Amendements.xml.zip"
)

# Dossier pilote : PPL « travailler le 1er mai » (dossier AN DLR5L17N51987).
# Deux textes législatifs côté AN : la proposition adoptée par le Sénat
# (n° 1673) et le texte de la commission (n° 2335, réf. PIONANR5L17BTC2335).
DOSSIER_PILOTE = "DLR5L17N51987"
TEXTES_PILOTES = frozenset({"PIONANR5L17B1673", "PIONANR5L17BTC2335"})


def download(url: str, cache_dir: Path = CACHE_DIR) -> Path:
    """Télécharge une ressource avec cache local. Ne jamais re-télécharger un
    fichier déjà présent (coût réseau et stabilité des tests)."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    dest = cache_dir / url.rstrip("/").rsplit("/", 1)[-1]
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    tmp = dest.with_name(dest.name + ".part")
    with httpx.stream("GET", url, timeout=120.0, follow_redirects=True) as resp:
        resp.raise_for_status()
        with open(tmp, "wb") as f:
            f.writelines(resp.iter_bytes())
    tmp.replace(dest)  # renommage atomique : jamais de fichier partiel en cache
    return dest


class _ExtracteurTexte(HTMLParser):
    """Extrait le texte brut d'un fragment HTML embarqué dans l'open data
    (champs `dispositif` / `exposeSommaire` des amendements)."""

    def __init__(self) -> None:
        super().__init__()
        self._morceaux: list[str] = []

    def handle_data(self, data: str) -> None:
        self._morceaux.append(data)

    def texte(self) -> str:
        return " ".join(" ".join(self._morceaux).split())


def _html_vers_texte(fragment: str | None) -> str:
    if not fragment:
        return ""
    extracteur = _ExtracteurTexte()
    extracteur.feed(fragment)
    return extracteur.texte()


def _libelles_signataires(signataires: object) -> list[str]:
    """Libellés lisibles de l'auteur et des cosignataires (structure AN 17e)."""
    if not isinstance(signataires, dict):
        return []
    libelles: list[str] = []
    if signataires.get("libelle"):
        libelles.append(str(signataires["libelle"]))
    cosignataires = signataires.get("cosignataires")
    if isinstance(cosignataires, dict):
        for c in cosignataires.get("cosignataire") or []:
            if isinstance(c, dict) and c.get("libelle"):
                libelles.append(str(c["libelle"]))
    return libelles


def _aplatir_amendement(brut: dict) -> dict:
    """Aplatit le JSON brut AN (17e) d'un amendement en dict stable et
    sérialisable. Champs source : uid, identification.numeroLong, examenRef,
    texteLegislatifRef, signataires, pointeurFragmentTexte (division + alinea),
    corps.contenuAuteur (dispositif / exposeSommaire en HTML), sort, dateDepot.
    Le JSON brut est conservé sous la clé `brut` pour l'audit."""
    identification = brut.get("identification") or {}
    pointeur = brut.get("pointeurFragmentTexte") or {}
    division = pointeur.get("division") or {}
    alinea = pointeur.get("alinea") or {}
    corps = brut.get("corps") or {}
    contenu = corps.get("contenuAuteur") or {}
    sort = brut.get("sort")
    if isinstance(sort, dict):
        sort = sort.get("libelle") or sort.get("code")
    return {
        "uid": brut.get("uid"),
        "numero": identification.get("numeroLong"),
        "examen_ref": brut.get("examenRef"),
        "texte_ref": brut.get("texteLegislatifRef"),
        "numero_article": division.get("titre") or division.get("articleDesignation"),
        "alinea": alinea.get("numero"),
        "signataires": _libelles_signataires(brut.get("signataires")),
        "dispositif": _html_vers_texte(contenu.get("dispositif")),
        "exposition": _html_vers_texte(contenu.get("exposeSommaire")),
        "sort": sort,
        "date_depot": brut.get("dateDepot"),
        "brut": brut,
    }


def lire_amendements_zip(
    zip_path: Path, textes_ref: frozenset[str] | set[str] = TEXTES_PILOTES
) -> list[dict]:
    """Lit un zip `Amendements.json.zip` et ne garde que les amendements dont
    le texte législatif (`texteLegislatifRef`) appartient au dossier pilote."""
    amendements: list[dict] = []
    with zipfile.ZipFile(zip_path) as zf:
        for nom in zf.namelist():
            if nom.endswith("/") or not nom.endswith(".json"):
                continue
            with zf.open(nom) as f:
                brut = json.load(f)
            if brut.get("texteLegislatifRef") in textes_ref:
                amendements.append(_aplatir_amendement(brut))
    amendements.sort(key=lambda a: (a.get("texte_ref") or "", a.get("numero") or ""))
    return amendements


def parse_amendements(
    legislature: str = "17",
    textes_ref: frozenset[str] | set[str] = TEXTES_PILOTES,
    cache_dir: Path = CACHE_DIR,
) -> list[dict]:
    """Charge les amendements du dossier pilote depuis le jeu zippé de la
    législature. Le zip est mis en cache : un second appel ne re-télécharge
    rien (coût et reproductibilité)."""
    url = (
        f"{BASE_URL}/static/openData/repository/{legislature}"
        "/loi/amendements_div_legis/Amendements.json.zip"
    )
    zip_path = download(url, cache_dir)
    return lire_amendements_zip(zip_path, textes_ref)
