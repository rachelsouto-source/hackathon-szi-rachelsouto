# 10 — Consulta à base histórica

O método (arquivos 00–09) diz **o que perguntar**. A base histórica deste repositório diz
**o que costuma dar errado** — o que a Seazone já viveu em DD, licenciamento, alvarás e
aprovações nos empreendimentos anteriores.

Use as duas juntas: um achado ganha muito mais valor quando vem acompanhado do precedente
("no Novo Campeche isso custou X meses").

## Onde a memória vive

Planilha **"Base de Conhecimento — DD Técnica (Seazone)"**, alimentada pelo motor de
extração do repositório `seazone-tech/base-conhecimento-dd-tecnica` (projeto do Vini —
ver `CONTEXTO.md` e `docs/RETOMADA.md` naquele repo). Duas camadas:

| Aba | O que é | Granularidade |
|---|---|---|
| `aprendizados` | Matéria-prima granular, append-only, com link para o documento original | 1 linha por evento/achado |
| `sintese` | Derivada e regenerável — **nunca editar à mão** (exceto `nota_humana`) | 1 linha por `emp_id × disciplina × categoria` |

Expostas na Nekt como
`nekt_operacional_silver.szi_dd_tecnica_aprendizados` e `.szi_dd_tecnica_sintese`.

## Fluxo de consulta (três passos)

1. **Ler a `sintese`** (leve) → identificar os empreendimentos e disciplinas comparáveis.
2. **Descer nas granulares** via `linhas_ref` das sínteses relevantes.
3. **Só então abrir os documentos originais** no Drive (coluna `link` da granular).

Não leia 50 projetos a cada análise: consulte a base leve, escolha os ~3 empreendimentos
mais compatíveis e aprofunde apenas neles.

## Como escolher os precedentes

- **Mesma cidade** → priorizar. Alvarás, aprovações, licenças ambientais e demolições
  locais são o melhor preditor (ex.: Floripa → Novo Campeche, Jurerê, Ilha do Campeche).
- **Sem precedente local** → subir para o **estado** e para produtos análogos
  (ex.: Alagoas → Japaratinga, Patacho).
- **Perdidos e cancelados também contam** — são os que mais trazem aprendizado.

## Vocabulário de consulta

- `disciplina` (fixa): `ambiental` · `urbanístico` · `concessionárias` · `incêndio` ·
  `sanitário` · `patrimônio` · `jurídico-cartorial` · `topografia` ·
  `arquitetura-projeto` · `engenharia`
- `categoria`: `referência` · `conhecimento-geral` · `acerto` · `gargalo` ·
  `exigência-de-órgão` · `erro`
- `tema`: aberto (ex.: "corte de árvore/supressão", "alvará de demolição", "PPCI / bombeiros")

Fonte da verdade: `engine/schema.py` → `TAXONOMIA`, em
`seazone-tech/base-conhecimento-dd-tecnica`.

## Perguntas que a base responde bem

- "Quais os principais gargalos ambientais dos últimos projetos em Florianópolis?"
- "Quanto tempo, na prática, levou entre protocolo e alvará de demolição nos casos anteriores?"
- "Que exigências o CBMSC repetiu nos apart-hotéis já aprovados?"
- "Já tivemos terreno de marinha? O que a SPU exigiu e quanto atrasou?"

## Regras de uso

- **Precedente não é prova.** Um aprendizado histórico embasa uma **recomendação**, nunca
  um fato sobre o terreno em análise. O fato vem do documento do terreno.
- Cite o precedente com o empreendimento de origem e o link do documento — memória
  referenciada, não genérica.
- **Consulta programática:** nunca via MCP `read_file_content` (trunca silenciosamente);
  usar `ler_aprendizados` / `ler_sintese` (Sheets API) ou `trabalho/<emp_id>/linhas.json`.

## Realimentação

A cada DD concluída, os achados devem voltar para a base como novas linhas granulares,
com disciplina, categoria, tema, resumo, desfecho e link — é isso que faz a base melhorar
a cada projeto em vez de reler tudo do zero.
