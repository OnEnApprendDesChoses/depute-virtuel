"""API FastAPI du pipeline député virtuel.

Endpoints prévus :
- GET  /documents            : dossiers ingérés
- POST /extract              : extraction LLM d'un texte fourni
- POST /verify               : vérification de cohérence
- GET  /ask?q=...            : recherche RAG
- POST /quiz                 : questions de compréhension + évaluation

TODO (semaines 4-5) : wiring complet.
"""
from fastapi import FastAPI

app = FastAPI(
    title="Député virtuel",
    description="Extraction et vérification des propositions de loi et amendements (open data AN)",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "pipeline": "depute-virtuel"}
