FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copy project files
COPY pyproject.toml uv.lock* ./
COPY src/ ./src/

# Install project dependencies using uv
RUN uv sync --frozen --no-cache --no-dev

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

COPY server.py ./
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import asyncio; from database import get_engine; asyncio.run(get_engine().connect())" || exit 1

# Run the MCP server
CMD ["uv", "run", "python", "server.py"]