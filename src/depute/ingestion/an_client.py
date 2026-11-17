"""Client open data de l'Assemblée nationale.

Télécharge les jeux de données (XML/JSON zippés) et les met en cache local.
Sources : https://data.assemblee-nationale.fr/

Jeux utiles (17e législature) :
- Amendements : /travaux-parlementaires/amendements/tous-les-amendements
- Dossiers législatifs : /travaux-parlementaires/dossiers-legislatifs
- Comptes rendus des débats : /travaux-parlementaires/comptes-rendus

TODO (semaine 1) :
1. Implémenter download() (httpx streaming + cache disque, jamais re-télécharger).
2. Implémenter parse_amendements() : dézipper et charger le dossier pilote
   (PDL « travailler le 1er mai », dossier AN n° DLR5L17N51987).
3. Vérifier ici les volumes réels (nb d'amendements par lecture) et le
   consigner dans eval/reports/.
"""
from pathlib import Path

BASE_URL = "https://data.assemblee-nationale.fr"
CACHE_DIR = Path("data")  # hors git (voir .gitignore)

# TODO: URLs réelles des ressources zip, à relever sur data.assemblee-nationale.fr
AMENDEMENTS_URL = f"{BASE_URL}/static/openData/repository/17/loi/amendements_div_legis/Amendements.xml.zip"


def download(url: str, cache_dir: Path = CACHE_DIR) -> Path:
    """Télécharge une ressource avec cache local. Ne jamais re-télécharger un
    fichier déjà présent (coût réseau et stabilité des tests)."""
    raise NotImplementedError


def parse_amendements(legislature: str = "17") -> list[dict]:
    """Charge les amendements de la législature depuis le jeu zippé.

    Filtre sur le dossier pilote (texte n° 1673 / dossier DLR5L17N51987).
    """
    raise NotImplementedError
