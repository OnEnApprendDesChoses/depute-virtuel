# Standards de review — Député virtuel

Tu reviewes comme un ingénieur senior sur une stack Python moderne (3.12, uv, FastAPI, pydantic v2, sqlmodel/pgvector).
Lis AGENTS.md avant toute review : il fait foi sur le périmètre, la stack et les conventions.
Ne commente pas le style : ruff et le CI s'en chargent. Concentre-toi sur les erreurs de logique, de conception et de sécurité.

## Bloquant (Request changes)

- Sortie LLM non validée : usage de json.loads ou parsing manuel au lieu de provider.complete_structured avec schéma pydantic v2.
- Schéma d'extraction sans ConfigDict(extra="forbid") ou qui accepte silencieusement des champs inconnus.
- Appel SDK Mistral/Anthropic en dehors de src/depute/llm/.
- Introduction d'un appel LLM, de réseau ou d'aléatoire dans extraction/verification.py (module déterministe par contrat).
- Prompt modifié sans test golden sur fixtures réelles (non-régression de l'extraction).
- Secret en dur, dans un fichier committé, ou .env hors .gitignore.
- Sortie du périmètre AGENTS.md : comptes, votes, modération, scraping HTML de l'AN, OCR.
- Réécriture en profondeur de code existant marqué TODO alors que la PR n'est pas consacrée à ce TODO (le starter kit avance par étapes).
- Test qui mock l'emploi réel du code (teste le mock, pas la fonction).

## À signaler (Comment)

- Régression de coût/perf LLM : document ré-extrait alors qu'un cache existe ; extraction sans température 0.
- Erreur de gestion : exception avalée, cas de sortie LLM malformée non couvert par un test.
- Requête SQL construite hors modules rag/, ou migration de schéma sans plan Alembic.
- Convention de langue : le code, les docstrings et les messages d'erreur sont en français.
- Manque de fiabilité du pipeline : logique non couverte par eval/run_eval.py alors qu'elle le devrait.

## Style de review

- Un défaut = un commentaire inline sur la ligne concernée, avec une suggestion de correction concrète (patch court quand c'est possible).
- Pas de commentaire générique ("consider adding tests") : nomme le cas de test précis manquant.
- Si le diff est globalement sain, dis-le et propose les 1-2 améliorations les plus utiles, sans bloquer.
- Ne génère pas de rapport exhaustif pour un TODO volontaire documenté dans les docstrings du starter kit.
