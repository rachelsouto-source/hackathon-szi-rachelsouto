# Relatório de Conformidade Técnica — [DISCIPLINA]

> Template do **Checador** do Consultor Técnico. Gerado pela skill `consultor-tecnico`.
> Requer revisão humana antes de uso oficial.

---

## Cabeçalho

| Campo | Valor |
|---|---|
| **Empreendimento** | [nome do empreendimento] |
| **Disciplina** | [Bombeiro CBMSC / NBR Acessibilidade / NBR Desempenho / SST] |
| **Versão do projeto** | [AP Rev.00 / PL Rev.02 / etc.] |
| **Data da entrega** | [AAAA-MM-DD] |
| **Legislação vigente** | [versão da base usada, ex: base-bombeiro-sc v1.0 de 2026-06-25] |
| **Comunique(s) de referência** | [Comunique nº X de AAAA-MM-DD — lista os anteriores] |
| **Gerado em** | [AAAA-MM-DD] |

---

## Classificação da edificação

| Item | Valor |
|---|---|
| Uso / Ocupação | [ex: A-4 — Residencial Multifamiliar] |
| Altura total (h) | [xx,x m] |
| Nº de pavimentos | [T+N] |
| Área construída total | [xxx m²] |
| Nº de unidades | [xx unidades] |
| Nº de vagas | [xx vagas] |
| Classificação CBMSC | [ex: Grupo A-4, Muito Alta (h > 23m)] |

---

## Resumo executivo

| Status | Contagem |
|---|---|
| 🟢 Atende | X itens |
| 🔴 Não atende | X itens |
| 🟡 Atenção | X itens |
| ⬜ Pendente (doc ausente) | X itens |
| 🔄 REGRESSÃO (comunique quebrado) | X itens |
| ➖ Não se aplica | X itens |

**Recomendação geral**: [Aprovado para protocolo / Corrigir antes do protocolo / Revisão urgente]

---

## Checklist de conformidade

### [Sistema ou Grupo de Regras 1 — ex: Escada de emergência]

| # | Item | Regra | Evidência no projeto | Status | Severidade |
|---|---|---|---|---|---|
| 1 | Tipo de escada (EEE vs EP) | h > 23m → EP (IN-012/CBMSC) | [Planta de cobertura mostra EEE / não indica tipo] | 🔴 Não atende | 🔴 Crítico |
| 2 | Largura mínima 1,20 m | IN-012 | [Cotado 1,20 m na planta baixa] | 🟢 Atende | 🔴 Crítico |
| ... | | | | | |

### [Sistema ou Grupo de Regras 2 — ex: Hidrante]

| # | Item | Regra | Evidência no projeto | Status | Severidade |
|---|---|---|---|---|---|
| ... | | | | | |

---

## Itens REGRESSÃO (🔄 — maior prioridade)

> Pontos que estavam **atendidos** em versão/comunique anterior e que a versão atual coloca em risco.

| Comunique / Versão anterior | Item | Como estava atendido | O que mudou nesta versão |
|---|---|---|---|
| Comunique nº X (AAAA-MM-DD), item Y | [descrição] | [o que o projeto anterior fazia] | [o que mudou] |

---

## Pontos para decisão de gestão (régua)

> Itens que dependem da définição de mínimo vs. preciosismo pela Rachel.
> A skill não decide — lista para que a gestão resolva.

| # | Item | Situação atual no projeto | Opções |
|---|---|---|---|
| 1 | [ex: Plano de emergência/brigada] | [Não previsto] | (a) Exigir no projeto; (b) Tratar como pós-aprovação |

---

## Ações recomendadas (para o próximo ciclo de revisão)

| Prioridade | Ação | Responsável | Prazo sugerido |
|---|---|---|---|
| 🔴 Urgente | [corrigir tipo de escada para EP] | Arquiteto | Antes da próxima revisão |
| 🟡 Atenção | [indicar coluna seca na fachada] | Arquiteto | Antes do protocolo |

---

*Relatório gerado pelo Consultor Técnico (skill `consultor-tecnico`) — disciplina [DISCIPLINA].*
*Requer revisão humana antes de qualquer uso oficial.*
