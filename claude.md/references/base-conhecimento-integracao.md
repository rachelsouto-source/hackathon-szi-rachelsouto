# Integração com a Base de Conhecimento de DD Técnica (projeto do Vini)

> Analisado em 09/07/2026 a partir do repo `seazone-tech/base-conhecimento-dd-tecnica`
> (privado, dono: Vinícius Melo). Este arquivo documenta a integração; não duplicar a
> lógica do projeto do Vini aqui — ele é a fonte da verdade.

## O que é e por que existe

Decisão da reunião "IA - Lançamentos" (02/07/2026, Bianca/Caroline/Tati/Vini): o projeto
foi dividido em duas frentes que se conectam:

| Parte | Responsável | Repo |
|---|---|---|
| **Base de conhecimento** (extrai e consolida aprendizados históricos de DD) | Vini | `seazone-tech/base-conhecimento-dd-tecnica` |
| **Consultor/analisador de DD** (consome a base e gera o parecer) | Rachel | este repo — Auditor de DD Técnica |

Motivação: a cada DD, a IA relia tudo do zero e cada entrega saía diferente — faltava uma
base persistente que acumulasse "isso já aconteceu no [spot X]" entre empreendimentos.

## Onde os dados vivem

- **Planilha Google** "Base de Conhecimento — DD Técnica (Seazone)", ID
  `1rDsR5BbzmegQ697aW2L8xulmRD-1t5S9AY9YIsZgSg8` (Meu Drive do Vini, compartilhada).
- **Nekt** (fonte preferencial para consumo programático): tabelas
  `nekt_operacional_silver.szi_dd_tecnica_aprendizados` e `.szi_dd_tecnica_sintese`.
- ⚠️ **Nunca ler a planilha inteira via MCP genérico do Drive (`read_file_content`)** —
  ela tem 5.000+ linhas e trunca silenciosamente (confirmado na prática em 09/07/2026).
  Consumo real deve ser via Nekt (SQL) ou via a Sheets API dedicada do próprio projeto
  do Vini (`engine/sheets_writer.py: ler_aprendizados` / `ler_sintese`).

## Estrutura dos dados

**Aba `aprendizados`** (granular, 1 linha por evento/documento, append-only):
`id, empreendimento, emp_id, cidade, uf, disciplina, categoria, tema, resumo, desfecho,
documento, data_doc, fonte_extracao, data_extracao, link`.

`categoria` é sempre uma de: `referência`, `conhecimento-geral`, `acerto`, `gargalo`,
`exigência-de-órgão`, `erro`.

**Aba `sintese`** (derivada, 1 linha por `emp_id × disciplina × categoria`, regenerável):
parágrafo consolidado por LLM + `linhas_ref` (ids das granulares de origem) +
`nota_humana` (única coluna editável à mão).

### Taxonomia `disciplina` (vocabulário fixo do Vini) × regras desta skill (R1–R7)

| `disciplina` (base do Vini) | Onde mapeia no `dd-tecnica-playbook.md` |
|---|---|
| `ambiental` | R4 Ambiental (APP, marinha, UC, supressão vegetal, licenciamento) |
| `urbanístico` | R3 Gabarito/urbanístico (TO, CA, recuo, alvará) |
| `jurídico-cartorial` | Fora do escopo desta DD Técnica (é DD Jurídica) — mas útil para achados de titularidade/certidões, ver `novo-campeche-achados.json` |
| `topografia` | R1 Consistência de área |
| `engenharia` | R5 Geotécnico (sondagem/fundação) |
| `incêndio` | Seção Bombeiro do parecer (R7, hoje calculado direto da altura — a base pode confirmar precedentes de EEE/EP) |
| `concessionárias`, `sanitário`, `patrimônio` | Achados complementares, sem regra própria ainda |

## Fluxo de consulta (desenhado pelo Vini para esta skill)

1. Consultar `sintese` (leve) filtrando por `cidade`/`uf` do empreendimento em DD — se não
   houver precedente na mesma cidade, cair para o mesmo `uf` (estado).
2. Dentro dos resultados, priorizar `categoria = gargalo` e `categoria = erro` — são os que
   mais evitam retrabalho.
3. Descer nas linhas granulares via `linhas_ref` para pegar o `resumo`/`desfecho` completo.
4. Só então abrir o documento original no Drive via a coluna `link`, se for preciso
   aprofundar.

## Como usar nesta skill

No **passo 0** do `SKILL.md` (antes de rodar os cruzamentos R1–R7), consultar a base por
precedentes na mesma cidade/estado e citar os relevantes na nova seção **"Precedentes"**
do parecer (`templates/parecer-tecnico.md`), sempre com o nome do empreendimento de origem
e o link — nunca genérico ("já vimos isso antes"), sempre rastreável ("isso aconteceu no
Campeche Spot [2595]").

## Estado da base (checar antes de confiar cegamente)

Em 09/07/2026: **4 de ~72 empreendimentos** extraídos e sintetizados — Campeche Spot
(`2595`), Jurerê Spot (`6665`), Japaratinga (`0584`), Jurerê Beach (`2811`). Os outros 68
estão **pausados** até o Vini validar que os 4 pilotos agregam valor real. Ou seja: hoje a
base só cobre esses 4 casos — para qualquer outra cidade/empreendimento, a consulta
provavelmente não vai encontrar precedente ainda, e isso é esperado (não é falha da
consulta, é cobertura parcial). Confirmar com o Vini antes de expandir a dependência desta
skill na base.
