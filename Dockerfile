FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN uv venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

COPY requirements.txt .

RUN uv pip install --no-cache -r requirements.txt

RUN wget -O /tmp/meilisearch.tar.gz \
    https://github.com/meilisearch/meilisearch/releases/download/v1.15.2/meilisearch-linux-amd64 \
    && mv /tmp/meilisearch.tar.gz /app/meilisearch \
    && chmod +x /app/meilisearch

COPY . .

RUN chmod +x /app/start.sh

EXPOSE 7870
EXPOSE 7700
EXPOSE 8001
EXPOSE 8000
EXPOSE 8501

CMD ["/app/start.sh"]