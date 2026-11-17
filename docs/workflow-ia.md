# Workflow IA de la démo

Le starter kit simule un workflow en 4 étapes :

1. **Proposition de loi** — chaque loi est décrite dans `data/lois.json` (titre, exposé, points clés).
2. **Résumé par l'IA** — le bouton « Résumé de l'IA » appelle `GET /api/lois/:id/resume-ia`. Dans le starter kit, la réponse est générée localement par un gabarit (`resumeIA()` dans `server.js`), marquée `source: "simulation"`.
3. **Vote du citoyen** — l'utilisateur vote Pour / Contre / Abstention via `POST /api/lois/:id/vote`.
4. **Synthèse des résultats** — le front affiche le décompte et le pourcentage de votes favorables.

## Brancher un vrai modèle

Pour remplacer la simulation par un appel à un modèle de langage :

1. Créer une fonction qui envoie le texte de la loi au modèle (ex. via l'API Mistral) et renvoie son résumé.
2. L'appeler dans la route `/api/lois/:id/resume-ia` à la place de `resumeIA(loi)`, en gardant le même format de réponse (`{ titre, resume, source }`).
3. Lire la clé d'API **uniquement** depuis une variable d'environnement (ex. `process.env.MISTRAL_API_KEY`), jamais en dur dans le code, et la lister dans `.gitignore` / `.env.example`.

Le front n'a pas besoin d'être modifié : il consomme déjà le champ `resume` de la réponse.
