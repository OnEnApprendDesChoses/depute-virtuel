# Inventaire du dossier pilote — PPL « travailler le 1er mai » (DLR5L17N51987)

Consulté le 2026-11-17 sur les sources officielles de l'Assemblée nationale :

- Page du dossier : https://www.assemblee-nationale.fr/dyn/17/dossiers/DLR5L17N51987
- Jeu « Tous les amendements » (17e législature) :
  https://data.assemblee-nationale.fr/travaux-parlementaires/amendements/tous-les-amendements
  - JSON : `…/static/openData/repository/17/loi/amendements_div_legis/Amendements.json.zip`
  - XML  : `…/static/openData/repository/17/loi/amendements_div_legis/Amendements.xml.zip`
  - Le zip regroupe les amendements **par texte de loi** : arborescence
    `<texteLegislatifRef>/<uid-amendement>.json` (un fichier par amendement).

## Textes législatifs AN du dossier et volumes d'amendements

| Texte AN (ref open data) | Rôle | Amendements |
|---|---|---|
| `PIONANR5L17B1673` (texte n° 1673, déposé le 3 juillet 2025) | Proposition adoptée par le Sénat, examen en commission à l'AN | **20** |
| `PIONANR5L17BTC2335` (texte de la commission n° 2335-A0, 13 janvier 2026) | Examen en séance publique à l'AN | **234** |

**Total côté AN : 254 amendements sur 2 examens** (texte rejeté en séance le 10 avril 2026).

## Conséquence pour le pipeline

Le zip « tous les amendements » couvre toute la législature (volumineux) :
pour le dossier pilote, `parse_amendements()` filtre par `texteLegislatifRef`
∈ {`PIONANR5L17B1673`, `PIONANR5L17BTC2335`} — constante `TEXTES_PILOTES` dans
`src/depute/ingestion/an_client.py`.
