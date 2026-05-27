# Deploy — Auditor de DD Técnica (Coolify)

App web (FastAPI + frontend) que lê a pasta **02 - Projetos** no Drive, audita a DD Técnica
via Claude API e gera Google Doc + planilha. Publicado no **Coolify** (deploy.seazone.dev).

## Pré-requisitos (segredos)
1. **Service Account Google** (acesso ao Drive):
   - Google Cloud Console → criar projeto → ativar **Google Drive API**.
   - Criar **Service Account** → gerar **chave JSON**.
   - Compartilhar a pasta **02 - Projetos** com o e-mail da service account
     (`...@...iam.gserviceaccount.com`) — como **Editor** (para escrever o Google Doc).
   - Pegar o **ID da pasta** 02 - Projetos (da URL do Drive).
2. **Chave da Claude API** (Anthropic) — `ANTHROPIC_API_KEY`.

## Variáveis de ambiente (no Coolify)
| Variável | Valor |
|---|---|
| `DEMO_MODE` | vazio (produção) — ou `1` para demo sem credenciais |
| `ANTHROPIC_API_KEY` | sua chave da Claude API |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-5` (default) |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | conteúdo **inteiro** do JSON da service account |
| `PROJETOS_FOLDER_ID` | ID da pasta "02 - Projetos" no Drive |

## Passos no Coolify
1. Subir este repositório para o GitHub na org **seazone-tech**.
2. Usar a skill **deploy-coolify** (ou o painel) apontando para o repo.
   - Build: **Dockerfile** (já incluso na raiz).
   - Porta: `8000` (o container lê `$PORT`).
3. Cadastrar as variáveis de ambiente acima.
4. Deploy → a skill devolve a **URL de acesso**.

## Monitor automático (os dois modos)
- **Manual:** a página web (botão *Gerar DD*).
- **Automático:** agendar (cron do Coolify / agendador externo) uma chamada
  `POST {URL}/api/monitor/run` (ex.: a cada hora). Ele varre 02 - Projetos e gera a DD dos
  empreendimentos que já têm todos os documentos obrigatórios e ainda não têm parecer.
- Diagnóstico: `GET {URL}/api/monitor` mostra a completude de cada empreendimento.

## Testar localmente
```bash
pip install -r requirements.txt
cd app
DEMO_MODE=1 uvicorn main:app --reload      # modo demo (Jurerê III), sem credenciais
# produção local: exporte as variáveis acima e rode sem DEMO_MODE
python _smoketest.py                         # teste ponta a ponta (demo)
```

## Endpoints
- `GET /` — página.
- `GET /api/health` — status/modo.
- `GET /api/empreendimentos` — lista de 02 - Projetos.
- `POST /api/dd` — body `{ "id": "<folderId>", "nome": "<empreendimento>" }`.
- `GET /api/dd/{rid}/xlsx` — baixa a planilha.
- `GET /api/monitor` · `POST /api/monitor/run` — monitor automático.
