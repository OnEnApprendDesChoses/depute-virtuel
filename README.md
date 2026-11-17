# 🏛️ Député virtuel

Démo d'application qui permet de **voter les lois**, avec un **workflow assisté par IA** : chaque proposition de loi peut être résumée par l'IA avant le vote.

## Lancer le projet

Prérequis : Node.js (aucune dépendance à installer).

```bash
npm start
```

Puis ouvrir <http://localhost:3000>.

La variable d'environnement `PORT` permet de changer le port (3000 par défaut).

## Structure

```
├── server.js            Serveur zero-dependency (statique + API JSON)
├── data/lois.json       Propositions de loi de la démo
├── public/              Front-end (HTML/CSS/JS vanilla)
│   ├── index.html
│   ├── style.css
│   └── app.js
└── docs/workflow-ia.md  Description du workflow IA de la démo
```

## API

| Méthode | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/lois` | Liste des lois avec le décompte des votes |
| POST | `/api/lois/:id/vote` | Vote : body `{ "choix": "pour" \| "contre" \| "abstention" }` |
| GET | `/api/lois/:id/resume-ia` | Résumé « IA » de la loi (simulé dans le starter kit) |

Exemple :

```bash
curl -X POST http://localhost:3000/api/lois/loi-semaine-32h/vote \
  -H 'Content-Type: application/json' \
  -d '{"choix": "pour"}'
```

## Workflow IA

Voir [docs/workflow-ia.md](docs/workflow-ia.md). Le starter kit simule la réponse de l'IA ; le doc explique comment brancher un vrai modèle (clé d'API uniquement via variable d'environnement, jamais dans le code).

## Notes

- Les lois proposées sont fictives et servent uniquement à la démo.
- Les votes sont stockés en mémoire : ils sont remis à zéro à chaque redémarrage du serveur.
