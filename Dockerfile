FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código do app (núcleo v2 em app/auditor/) + exemplos do modo demo
COPY app/ ./app/
COPY claude.md/exemplos/ ./claude.md/exemplos/

# Metodologia da DD Técnica — carregada como system prompt pelo agente
# (auditor/agente.py::_base_metodo). Sem isto o motor cai no playbook antigo.
COPY base-conhecimento/ ./base-conhecimento/

# Histórico entre rodadas, cache de extração e sessão de contestação.
# Montar um VOLUME aqui no Coolify — sem volume tudo degrada para memória e o
# changelog não sobrevive a um restart do container.
ENV AUDITOR_DADOS_DIR=/data/auditor
RUN mkdir -p /data/auditor

WORKDIR /app/app

EXPOSE 8000

# Coolify injeta a porta via $PORT (default 8000).
# keep-alive alto: a auditoria roda como job em thread e o painel faz polling.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --timeout-keep-alive 120"]
