FROM python:3.12-slim-bookworm

WORKDIR /app

# Configure domestic apt mirror for faster builds
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list || true

# Install runtime utilities
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies in a cached layer using domestic PyPI mirror
COPY requirements.txt ./
RUN pip install --no-cache-dir \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com \
    --default-timeout 120 \
    -r requirements.txt

# Create persistent data directory for SQLite
RUN mkdir -p /app/data

# Copy application source code
COPY app ./app

ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite+aiosqlite:////app/data/vectorbtc.db

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
