FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código do app + exemplos (usados no modo demo)
COPY app/ ./app/
COPY claude.md/exemplos/ ./claude.md/exemplos/

WORKDIR /app/app

EXPOSE 8000

# Coolify injeta a porta via $PORT (default 8000)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
