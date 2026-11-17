FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir uv && uv sync --frozen || uv sync
COPY src ./src
COPY eval ./eval
CMD ["uvicorn", "src.depute.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
