# AGENTS.md — Député virtuel

> Ce fichier donne le contexte du projet à tout agent de code (Mistral Code, Copilot, Claude Code, etc.).
> **Lis-le en entier avant d'écrire ou de modifier du code.** Ne réinvente pas le projet : il est déjà spécifié ici.

## À propos du projet

**Député virtuel** est une démo IA de portfolio (pas une plateforme ni un business) : un pipeline d'extraction et de vérification de documents législatifs français à partir de l'open data de l'Assemblée nationale (data.assemblee-nationale.fr, sources XML/JSON zippés).

Objectif démontré de bout en bout sur **un seul dossier législatif** :

1. Ingestion d'un dossier législatif (proposition de loi + amendements).
2. Extraction structurée par LLM (articles, exposé des motifs, signataires, dispositif des amendements) → JSON validé par schéma pydantic.
3. Vérification de cohérence déterministe (l'article modifié existe bien, dispositif non vide, pas de doublons…).
4. RAG sur le corpus (pgvector).
5. Brique différenciante : génération de questions de compréhension sur le texte + évaluation des réponses.
6. Industrialisation : métriques d'erreur sur échantillon annoté, tests, Docker, CI GitHub Actions, serveur MCP.

**Neutralité politique stricte** : extraction et structuration uniquement. Aucune prise de position, aucune analyse d'opinion, aucun wording à charge sur les textes ou leurs auteurs.

**État actuel** : starter kit — l'ossature et les interfaces existent, plusieurs fonctions sont des `TODO` explicites (semaine 1 à 5, voir les docstrings de chaque module). Ne réécris pas l'existant pour le rendre « fini » d'un coup ; avance les TODO dans l'ordre indiqué.

## Dossiers législatifs pilotes (ne pas en changer sans demande explicite)

- **Principal** : PPL « travailler le 1er mai » (dossier AN `DLR5L17N51987`, texte n° 1673, 17e législature).
- **Évaluation** : PPL « exercice en France des médecins diplômés au Royaume-Uni avant le Brexit » (cycle complet jusqu'à promulgation).

## Stack (celle du repo, ne pas en changer sans demande explicite)

- **Python 3.12+**, gestion des dépendances avec **uv** (`uv sync`, `uv run …`, `uv.lock` committé). FastAPI + uvicorn pour l'API.
- **LLM** : abstraction `LLMProvider` (`src/depute/llm/provider.py`), deux implémentations : `MistralProvider` (principal, `mistral-large-latest`) et `AnthropicProvider` (à garder fonctionnelle ; son `complete_structured` est encore un TODO — tool use + validation pydantic). **Jamais d'appel SDK direct ailleurs que dans `src/depute/llm/`** (les imports SDK y sont différés pour faciliter les tests).
- **Validation** : toute sortie LLM passe par `provider.complete_structured(...)` avec un schéma **pydantic v2**. Règle : `model_config = ConfigDict(extra="forbid")` sur les schémas de sortie LLM (à généraliser aux schémas existants de `extraction/schemas.py`). Pas de `json.loads` brut sur du texte de modèle.
- **Base** : PostgreSQL + pgvector via `sqlmodel` / `psycopg` / `pgvector` (image `pgvector/pgvector:pg17` dans `docker-compose.yml`). Pas de SQL brut en dehors des modules de persistance (`rag/`). Pas de migration pour l'instant ; introduire Alembic si le schéma SQL évolue.
- **Outils** : `ruff` (lint, `line-length = 100`, `target-version = py312`), `pytest` (+ `respx` pour mocker httpx), `httpx` pour le client AN. `mypy` est prévu mais **pas encore installé** : l'ajouter en dépendance dev avant de l'exiger (`uv run mypy src`).
- **Infra locale** : `docker compose up -d` (services `db` + `api`). `Dockerfile` basé sur `python:3.12-slim` + uv.
- **Pas de** : OCR, scraping HTML de l'AN, comptes utilisateurs, votes, modération, système de débat. Le périmètre est limité à la démo ci-dessus.

## Arborescence réelle

```
src/depute/
  api/            # FastAPI : main.py expose /health ; endpoints prévus listés dans la docstring
  ingestion/      # an_client.py (download/parse open data AN, TODO semaine 1), models.py (modèles bruts pydantic)
  extraction/     # extractor.py (prompts + extraction LLM), schemas.py (schémas de sortie), verification.py (règles R1-R6, déterministes)
  rag/            # embeddings.py + queries.py (TODO semaine 3 : pgvector, recherche hybride)
  comprehension/  # questions.py (génération de questions), grading.py (évaluation des réponses) — TODO semaine 3
  llm/            # provider.py (interface LLMProvider), mistral_provider.py, anthropic_provider.py
mcp/server.py     # serveur MCP exposant le pipeline comme tools (extract/verify/search/quiz) — TODO semaine 5, transport stdio
eval/run_eval.py  # workflow d'évaluation : dataset dans eval/dataset/, rapports JSON dans eval/reports/
tests/            # test_api.py, test_extractor.py (golden tests à écrire), test_verification.py
```

- **Convention de langue** : code (noms de fonctions, docstrings, messages d'erreur) en **français**, comme le starter kit. README en français ; une version EN est bienvenue pour le portfolio.
- Couches : `ingestion` → `extraction` → `verification` (dans `extraction/verification.py`) / `rag` / `comprehension`. `llm` est le **seul module transversal** (utilisé par `extraction`, `rag`, `comprehension`) ; aucun autre import transversal. `api/` et `mcp/server.py` orchestrent le pipeline.
- `extraction/verification.py` est **100 % déterministe** : des règles codées, zéro LLM. Le LLM n'intervient que dans `extraction`, `comprehension` et `rag`.
- Configuration par variables d'environnement : `MISTRAL_API_KEY`, `ANTHROPIC_API_KEY`, `DATABASE_URL` (voir `.env.example`). **Jamais de secret en dur ni dans un fichier committé** (`.env` et `data/` sont dans `.gitignore`).

## Commandes exactes

```bash
docker compose up -d     # postgres + pgvector et API
make dev                 # API en local : uv run uvicorn src.depute.api.main:app --reload
make lint                # uv run ruff check src tests eval
make test                # uv run pytest -q
make eval                # uv run python eval/run_eval.py (appels LLM réels : ne pas lancer à chaque commit)
```

- CI (`.github/workflows/ci.yml`) : sur chaque PR et chaque push sur `main` → `uv sync --dev`, `ruff check src tests eval`, `pytest -q`.
- Éval nocturne (`.github/workflows/eval.yml`) : `workflow_dispatch` + cron à 6h, secret `MISTRAL_API_KEY`, publie `eval/reports/` en artifact.

## Règles de contribution

- Branche dédiée + PR, **jamais de push direct sur `main`** (la CI tourne sur les PR).
- Avant de considérer un travail terminé : `make lint` et `make test` doivent passer.
- Toute fonction de `extraction`, `verification`, `comprehension` doit avoir des tests unitaires, y compris les cas d'échec de parsing et les sorties LLM malformées.
- Toute modification d'un prompt LLM doit être accompagnée d'un test de non-régression sur fixtures : **réponses LLM réelles enregistrées** (`tests/test_extractor.py`, golden tests), jamais de fixture inventée.
- Extraction LLM : `temperature=0`, sortie structurée stricte, et **cache** — un document déjà extrait n'est jamais renvoyé au LLM (coût + reproductibilité).
- Les sorties LLM sont stockées brutes en plus du JSON validé, pour permettre l'audit des métriques d'erreur (à mettre en place avec l'eval).
- Si une information manque (format exact d'un champ open data, structure d'un XML), **inspecte les vrais fichiers** du corpus (cache local `data/`, hors git) ou sur data.assemblee-nationale.fr avant de deviner un format. L'inventaire du zip « Tous les amendements » du dossier pilote est la référence pour les volumes ; consigner les volumes réels dans `eval/reports/`.
- `eval/dataset/` : objectif ~50 documents avec vérité terrain annotée à la main. Les rapports JSON vont dans `eval/reports/` (les `*.json` y sont gitignorés, seul `.gitkeep` est committé) ; le chiffre de tête va dans le README.

## Rappels de contexte

- Ce repo est public : README soigné, pas de données personnelles, pas de secret. Il sert de preuve pour des missions freelance IA.
- Si une tâche semble nécessiter de sortir du périmètre décrit ici, arrête-toi et demande plutôt que d'improviser.
