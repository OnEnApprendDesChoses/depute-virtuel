.PHONY: dev test lint eval
dev:
	uv run uvicorn src.depute.api.main:app --reload
test:
	uv run pytest -q
lint:
	uv run ruff check src tests eval
eval:
	uv run python eval/run_eval.py
