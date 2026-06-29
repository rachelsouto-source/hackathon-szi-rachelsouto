# Trilha de Auditoria — Consultor Técnico

> Template do **Auditor** do Consultor Técnico. Gerado pela skill `consultor-tecnico`.

---

## Cabeçalho

| Campo | Valor |
|---|---|
| **Empreendimento** | [nome] |
| **Período auditado** | [data_início] a [data_fim] |
| **Gerado em** | [AAAA-MM-DD] |

---

## 1. Mapa de entregas e cobertura do Checador

| Versão do projeto | Data | Disciplina | Checador rodou? | Base estava fresca? | Observação |
|---|---|---|---|---|---|
| EP Rev.00 | AAAA-MM-DD | Bombeiro | ✅ Sim | ✅ Sim (base v1.0) | — |
| AP Rev.00 | AAAA-MM-DD | Bombeiro | ❌ Não | — | 🔴 Lacuna de processo |
| AP Rev.01 | AAAA-MM-DD | NBR | ✅ Sim | 🟡 Base com 95 dias | Abastecedor não rodou no período |
| PL Rev.00 | AAAA-MM-DD | Bombeiro | ✅ Sim | ✅ Sim | — |

**Cobertura geral**: [X de Y entregas com Checador rodado] — [XX%]

---

## 2. Mapa de comuniques

| Comunique | Data | Nº de itens | Atendidos | Pendentes | Contestados |
|---|---|---|---|---|---|
| Comunique nº 1 | AAAA-MM-DD | X | X | X | X |
| Comunique nº 2 | AAAA-MM-DD | X | X | X | X |

### Detalhe por item (todos os comuniques)

| Comunique | Item | Descrição | Status | Versão em que foi atendido | Regressão detectada? |
|---|---|---|---|---|---|
| nº 1 | A | [descrição] | ✅ Atendido | AP Rev.02 | ❌ Não |
| nº 1 | B | [descrição] | ⏳ Pendente | — | — |
| nº 2 | C | [descrição] | ✅ Atendido | PL Rev.00 | ⚠️ SIM — ver seção 3 |

---

## 3. Regressões detectadas (🔴 prioridade máxima)

> Item já atendido em versão/comunique anterior que foi quebrado em versão posterior.

| # | Comunique origem | Item | Atendido em | Quebrado em | Descrição da quebra | Ação recomendada |
|---|---|---|---|---|---|---|
| 1 | nº 2, item C | [descrição] | PL Rev.00 | PL Rev.01 | [o que mudou] | Reverter para solução da Rev.00 ou aprovar nova solução |

---

## 4. Indicadores de reincidência

> Itens exigidos mais de uma vez em comuniques diferentes = candidatos a entry na base de regras.

| Item | Nº de vezes exigido | Comuniques | Candidato a base? |
|---|---|---|---|
| Tipo de escada (EEE vs EP) | 2 | nº 1 e nº 3 | ✅ Sim — já está na base |
| Piso tátil na entrada | 3 | nº 1, nº 2 e nº 4 | ✅ Sim — adicionar à base-nbr |
| [outro item] | 1 | nº 2 | 🟡 Avaliar |

---

## 5. Indicadores de saúde do processo

| Indicador | Valor | Meta | Status |
|---|---|---|---|
| Cobertura do Checador (% de entregas auditadas) | XX% | 100% | 🔴/🟡/🟢 |
| Regressões detectadas | X | 0 | 🔴/🟢 |
| Dias desde último abastecimento da base | XX dias | ≤ 90 dias | 🔴/🟡/🟢 |
| Itens pendentes de decisão de gestão | X | 0 | 🔴/🟡/🟢 |
| Comuniques com itens pendentes | X | 0 | — |

---

## 6. Ações recomendadas

| Prioridade | Ação | Responsável |
|---|---|---|
| 🔴 Urgente | Corrigir regressão [item X — seção 3] | Arquiteto + Rachel |
| 🔴 Urgente | Rodar Checador na versão [AP Rev.00] que ficou sem cobertura | Rachel |
| 🟡 Atenção | Rodar Abastecedor (base com > 90 dias) | [responsável pelo abastecimento] |
| 🟡 Atenção | Adicionar "piso tátil na entrada" à base-nbr (reincidente 3x) | Rachel |

---

*Relatório gerado pelo Consultor Técnico (skill `consultor-tecnico`) — papel Auditor.*
