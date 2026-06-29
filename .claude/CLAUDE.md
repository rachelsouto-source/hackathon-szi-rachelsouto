# Auditor de DD Técnica + Consultor Técnico — SZI Lançamentos

Produto publicado em: **https://auditor-dd.seazone.properties**
Contexto completo: `claude.md/CLAUDE.md`

## Skills instaladas neste projeto

| Skill | Invocação | O que faz |
|---|---|---|
| `/auditor-dd-tecnica` | "auditar DD técnica do [empreendimento]" | Auditoria de viabilidade do terreno (matrícula, topografia, ambiental, sondagem, estrutura). Roda uma vez, na compra. |
| `/consultor-tecnico` | "checar bombeiro/nbr/sst [empreendimento]" | Verifica conformidade de entregas arquitetônicas contra NBR, CBMSC e SST. Roda a cada entrega do projeto. |

## Caso-base validado
**Jurerê Spot III** — Florianópolis/SC. Exemplos em `claude.md/exemplos/`.

## Estrutura dos arquivos de referência

```
claude.md/
  SKILL.md                        ← skill DD Técnica (código-fonte)
  CONSULTOR-TECNICO.md            ← skill Consultor Técnico (código-fonte)
  references/
    dd-tecnica-playbook.md        ← regras da DD Técnica (cérebro do Auditor)
    legislacao-municipios.md      ← órgãos/leis por município
    base-bombeiro-sc.md           ← base de regras CBMSC completa (Consultor Técnico — por entrega)
    base-bombeiro-dd-resumo.md    ← resumo CBMSC para DD Técnica (flags de custo/viabilidade)
    base-nbr.md                   ← base de regras NBR 9050 + 15575
    base-sst.md                   ← base SST (stub — a desenvolver)
  templates/
    parecer-tecnico.md            ← output DD Técnica
    checklist-controle.csv        ← planilha de controle DD Técnica
    relatorio-conformidade.md     ← output Checador
    relatorio-abastecimento.md    ← output Abastecedor
    trilha-auditoria.md           ← output Auditor
  exemplos/                       ← saídas reais Jurerê Spot III
  scripts/
    gerar_checklist.py            ← gera .xlsx de controle
```

## Fonte de dados
Usar **NEKT** para dados de projetos — não usar Lake ou planilhas desatualizadas.
