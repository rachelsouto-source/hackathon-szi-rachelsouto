# Consultor Técnico & Auditor de DD — SZI Lançamentos

Produto publicado em: **https://auditor-dd.seazone.properties**
Contexto completo: `claude.md/CLAUDE.md`

## Skills instaladas neste projeto

| Skill | Quando invocar | O que faz |
|---|---|---|
| `/consultor-tecnico` | "checar bombeiro/NBR/SST [X]", "abastecer [disciplina]", "auditar entregas de [X]" | Verificação contínua por entrega arquitetônica (Modos B–D) |
| `/auditor-dd-tecnica` | "auditar DD técnica de [X]", "due diligence do terreno [X]", "esse terreno é viável?" | Auditoria única na compra do terreno (Modo A) — redireciona ao consultor-tecnico |

> **Skill unificado**: ambas as invocações usam o mesmo skill (`consultor-tecnico/SKILL.md`).
> O `auditor-dd-tecnica` é um alias para o Modo A do skill unificado.

## Caso-base validado
**Jurerê Spot III** — Florianópolis/SC. Exemplos em `claude.md/exemplos/`.

## Estrutura dos arquivos de referência

```
claude.md/
  CLAUDE.md                         ← este arquivo
  references/
    dd-tecnica-playbook.md          ← regras da DD Técnica + Drive paths (R1–R7)
    legislacao-municipios.md        ← órgãos/leis por município
    base-bombeiro-sc.md             ← base CBMSC completa (Consultor Técnico — por entrega)
    base-bombeiro-dd-resumo.md      ← resumo CBMSC para DD Técnica (flags de custo/viabilidade)
    base-nbr.md                     ← base NBR 9050 + NBR 15575
    base-sst.md                     ← base SST (stub — a desenvolver)
  templates/
    parecer-tecnico.md              ← output DD Técnica (Modo A)
    checklist-controle.csv          ← planilha de controle DD Técnica
    relatorio-conformidade.md       ← output Checador (Modo B)
    relatorio-abastecimento.md      ← output Abastecedor (Modo C)
    trilha-auditoria.md             ← output Auditor de Trilha (Modo D)
  exemplos/                         ← saídas reais Jurerê Spot III
  scripts/
    gerar_checklist.py              ← gera .xlsx de controle
```

## Fonte de dados
Usar **NEKT** para dados de projetos — não usar Lake ou planilhas desatualizadas.

## Drive — estrutura de pastas dos empreendimentos
```
<Pasta do empreendimento>/
  02 - Projetos/           ← documentos de projeto (topográfico, EVA, sondagem, estrutura, EP)
  05 - Jurídico/
    01 - Terreno/
      00 - Documentos e certidões.../
        Imóvel 1/  Imóvel 2/    ← matrícula, IPTU, confrontantes
      02 - Proposta de compra e venda/
```
Empreendimentos ficam em `00 - Empreendimentos Estruturados` na pasta mãe da SZI.
