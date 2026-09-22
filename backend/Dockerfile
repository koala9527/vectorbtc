FROM python:3.12-slim-bookworm

WORKDIR /app

# Install runtime utilities
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies in a cached layer
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Create persistent data directory for SQLite
RUN mkdir -p /app/data

# Copy application source code
COPY app ./app

ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite+aiosqlite:////app/data/vectorbtc.db

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
