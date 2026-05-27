# memory.md — Regras, convenções e decisões do projeto

## Decisões de produto
- **Escopo:** elaborar **e** auditar a DD Técnica (não só conferir). Entrada = pasta do
  empreendimento no Drive; saídas = parecer (documento) + planilha de controle + leitura de negócio.
- **Saídas obrigatórias:** (1) Parecer Técnico no formato oficial SZI; (2) planilha `.xlsx`
  de controle com status por etapa; (3) conclusão com **go / go com ressalvas / no-go**.
- **A skill assiste, não decide:** toda saída é rascunho técnico para **revisão humana**.

## Regras de negócio (fixas)
- **Gatilho de retificação de matrícula:** diferença entre área topográfica e área de
  matrícula **> 3%** ⇒ exigir retificação. Mais de uma matrícula ⇒ avaliar amembramento.
- **Consistência cruzada:** áreas (matrícula × cadastro × confrontantes × topográfico) e
  nº de unidades (EVA × estrutura × EP) devem ser confrontados sempre.
- **Parâmetros urbanísticos:** TO, CA, recuo, TP e gabarito do estudo devem ser checados
  contra o Plano Diretor do zoneamento.
- **Ambiental:** sinalizar APP, terreno de marinha (exigir afastamento **+ conferir
  documentação da SPU**), UC, supressão vegetal (AuC + compensação) e condicionantes
  (esgoto/ACP, demolição, licenciamento).
- **Geotécnico:** sondagem → fundação recomendada → coerência com doc estrutural → custo.
- **Zoneamento e exigências legais** vêm da **Viabilidade Técnica Construtiva** (documento do
  site da prefeitura) — é a fonte oficial dos parâmetros urbanísticos.
- **DD Jurídica NÃO entra** nesta DD Técnica — é consulta separada.

## Convenções
- **Idioma:** português (pt-BR) em toda a saída.
- **Rastreabilidade:** todo dado citado leva **fonte** (nome do arquivo + link do Drive).
- **Severidade:** 🔴 crítico · 🟡 atenção · 🟢 ok. Status: OK / Pendente / Divergência / Não se aplica.
- **Nunca presumir:** documento ausente ou ilegível ⇒ **Pendente** (jamais inventar conteúdo).
- **Parametrização por município:** órgãos e leis ficam em `references/legislacao-municipios.md`.
- **Encoding:** UTF-8 em todo I/O.
- **Convenção de pastas (entrega):** `claude.md/` (código), `lessons.md/` (erros), `memory.md/`
  (regras/decisões). Não criar arquivos homônimos às pastas na mesma raiz (ver lesson L1).

## Arquitetura (decisão: virou app deployável)
- O projeto tem **duas formas**: (1) skill do Claude Code; (2) **aplicação web** em `app/`
  publicada no **Coolify**, que lê a pasta `02 - Projetos` no Drive e gera Google Doc + planilha.
- **Disparo:** página manual ("Gerar DD") **e** monitor automático (`/api/monitor/run`,
  agendável por cron do Coolify).
- **Acesso ao Drive:** **Service Account** (server-to-server) — não usar MCP/OAuth interativo
  num app autônomo. A pasta 02 - Projetos é compartilhada com o e-mail da service account.
- **Leitura dos documentos:** PDFs enviados nativamente à **Claude API** (document blocks);
  Google Docs/Sheets exportados para PDF antes.
- **Saídas:** Google Doc na pasta + planilha `.xlsx` + preview na tela.
- **Modo demo offline** (`DEMO_MODE=1`): usa os exemplos do Jurerê III sem Drive/Claude —
  para testar e gravar a demo.

## Stack / dependências
- Claude Code (skill em `SKILL.md`) + Claude API (motor do app).
- App: **FastAPI + Uvicorn**, frontend estático (HTML/JS/CSS).
- Google Drive/Docs via `google-api-python-client` + Service Account.
- `openpyxl` para a planilha; `anthropic` para o motor.
- Deploy: **Dockerfile** → Coolify (repo na org `seazone-tech`).

## Estrutura de pastas no Drive (produção)
- **Lista de empreendimentos:** pasta "00 - Empreendimentos Estruturados / em Estruturação"
  (ID `1D9y8aKfkGGE13WbGMlw07G8Euu0Pg7fF`) → env `EMPREENDIMENTOS_FOLDER_ID`. Cada subpasta é
  um empreendimento (ex.: "1.43 - [6468] Jurerê Spot III", ID `1Cnh1CmyUFbZ7McaUoZBaV3eEjIODO8zZ`).
- Por empreendimento: docs de estudo em `02 - Projetos/<NN>`; matrícula/certidões em
  `05 - Jurídico/01 - Terreno/00 - Documentos e certidões.../Imóvel 1|2`; proposta em
  `05 - Jurídico/01 - Terreno/02 - Proposta de compra e venda`; imagens em
  `02 - Projetos/09 - Imagens de Drone`. Saída do parecer: `02 - Projetos/07 - DD Técnica`.

## Caso-base
- **Jurerê Spot III** (Florianópolis/SC). Pasta da DD no Drive: `1H1MIZ-1eRzKsLGN7x5Zaq0szD8t3sQeJ`.
  Documento-modelo: "[Jurerê Spot III] DD Técnica Spot.docx".
- Legislação caso-base: PMF; Plano Diretor LC 739/2023 (zoneamento ATR 4.5: TO 50%, impermeab. 70%,
  ~4 pav.); FLORAM (AuC/DANC); CASAN (esgoto/ACP); Bombeiros SC; NBR-9050; NBR 6484.

## Glossário
- **DD Técnica:** Due Diligence Técnica — análise de viabilidade do terreno/empreendimento.
- **EVA:** Estudo de Viabilidade Ambiental.
- **EP:** Estudo Preliminar (validado pelo arquiteto responsável).
- **TO / CA / TP:** taxa de ocupação / coeficiente de aproveitamento / taxa de permeabilidade.
- **APP / UC:** Área de Preservação Permanente / Unidade de Conservação.
- **AuC / DANC:** Autorização de Corte de vegetação / Declaração de Atividade Não Constante (FLORAM).
- **SPT:** Standard Penetration Test (ensaio de sondagem).
- **VGV:** Valor Geral de Vendas.
- **Amembramento:** unificação de matrículas em uma só.
