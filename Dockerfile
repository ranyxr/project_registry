FROM python:3.12-slim

ENV UV_CACHE_DIR=/root/.cache/uv
ENV UV_PROJECT_ENV=/app/.venv
ENV UV_INDEX_URL=https://pypi.org/simple
ENV PIP_INDEX_URL=https://pypi.org/simple

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock* README.md ./

RUN if [ -f uv.lock ]; then uv sync --frozen; else uv sync; fi

COPY . .

RUN chmod +x scripts/entrypoint.sh

EXPOSE 8000

CMD ["./scripts/entrypoint.sh"]
