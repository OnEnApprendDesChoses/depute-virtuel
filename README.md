# Député virtuel

Pipeline d'extraction et de vérification des propositions de loi et amendements
de l'Assemblée nationale (open data), avec validation de compréhension par
questions/réponses.

**Philosophie : comprendre avant de débattre.**

## Pourquoi ce projet

Chaque texte de loi peut être compris et débattu par n'importe qui, à
condition d'en avoir lu le contenu. Ce pipeline extrait, structure et
vérifie automatiquement les documents législatifs issus de
[data.assemblee-nationale.fr](https://data.assemblee-nationale.fr/), puis
génère des questions de compréhension sur chaque texte.

## Pipeline

1. **Ingestion** : téléchargement des jeux open data AN (XML/JSON), cache local.
2. **Extraction** : structuration LLM (articles, signataires, dispositif des amendements).
3. **Vérification** : règles de cohérence en code pur (zéro LLM).
4. **RAG** : recherche sémantique sur le corpus (pgvector).
5. **Compréhension** : génération de questions sur un texte + évaluation des réponses.

Le LLM extrait, le code vérifie. Aucune règle métier ne repose sur un LLM.

## Dossier pilote

- Principal : PDL « travailler le 1er mai » (dossier AN n° DLR5L17N51987).
- Second corpus d'évaluation : PDL « médecins diplômés au Royaume-Uni avant le Brexit ».

## Métriques

(Taux d'erreur d'extraction et faux positifs de vérification : voir `eval/reports/`.
À remplir après le premier run d'évaluation.)

## Lancement

```bash
docker compose up -d        # postgres + api
make dev                    # ou: uv run uvicorn src.depute.api.main:app --reload
make eval                   # run d'évaluation
```

## Périmètre

Ceci est une démonstration technique, pas une plateforme. Pas de comptes
utilisateurs, pas de votes. Neutralité politique : extraction et
structuration de documents uniquement, aucune prise de position.
