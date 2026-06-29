# Bombeiro CBMSC — Resumo para DD Técnica

> Uso: referência rápida do auditor de DD para identificar riscos de custo e viabilidade.
> Para análise de conformidade detalhada por entrega arquitetônica, usar `base-bombeiro-sc.md`.
> Versão: v1.0 | Baseado em base-bombeiro-sc v1.1 (2026-06-26)

---

## Pergunta central da DD

> "O conceito do projeto cria exigências de bombeiro que afetam custo ou inviabilizam o negócio?"

Não é compliance. É viabilidade.

---

## 1. Limiar de custo mais importante: EEE vs EP

| Altura (h) | Tipo de escada | Custo relativo |
|---|---|---|
| h ≤ 12 m | Escada natural | Baixo |
| 12 m < h ≤ 23 m | **EEE** — Enclausurada com Exaustão | Moderado |
| **h > 23 m** | **EP** — Escada Pressurizada | **Alto** ⬆️ |

**h = distância do piso do último pavimento habitável ao nível da rua (térreo).**

> ⚠️ Zona de risco: h entre 20 m e 26 m → qualquer ajuste de pavimento pode cruzar o limiar.
> Sinalizar para revisão do anteprojeto antes de fechar negócio.

EP exige: shaft dedicado, equipamento de pressurização, ante-câmara, projeto específico (NBR 14880),
manutenção recorrente. Custo adicional estimado: R$ 80–150 k dependendo do porte.

---

## 2. Grupos de ocupação (o que importa para SZI)

| Grupo | Descrição | Exigências |
|---|---|---|
| **A-2** | Residencial Multifamiliar (apartamentos) | Padrão |
| **B-2** | Hotel Residencial / flat / apart-hotel | Pode exigir brigada de incêndio e alarme com thresholds diferentes |
| H | **Saúde** (hospitais, clínicas) | ⚠️ Não confundir — H ≠ hospedagem no CBMSC |

**Regra prática**: uso "transitório" (Spot, flat, apart-hotel) → perguntar ao CBMSC se A-2 ou B-2.

---

## 3. O que checar na Validação do Arquiteto

A validação do EP pelo arquiteto é o documento principal para flags de bombeiro na DD.
Buscar explicitamente:

| Item | Flag se... |
|---|---|
| Tipo de escada indicado | Diverge da altura real (ex.: indica EEE mas h > 23 m) |
| Porta da EEE/EP | Menção a "sentido de abertura" ou "PCF" com problema |
| Acesso de viaturas | Testada < 6 m; via bloqueada ou com declive excessivo |
| Distância de percurso | > 20 m até a escada sem sprinkler |
| Sprinkler obrigatório | Exige chuveiros automáticos (custo adicional significativo) |
| Área de refúgio / heliponto | Mencionado como exigência (h > 50 m) |

---

## 4. Flags que entram como custo no parecer de negócio

| Situação | O que registrar |
|---|---|
| h > 23 m confirmado (EP exigida) | Adicionar custo EP estimado ao sumário de custos |
| Sprinkler obrigatório | Adicionar custo sprinkler estimado |
| B-2 confirmado | Verificar exigência de brigada — custo recorrente na operação |
| Acesso de viatura bloqueado | Possível exigência de obra de acesso → custo + prazo |

---

## 5. Instrução Normativa de referência (CBMSC)

| IN | Assunto |
|---|---|
| IN-009 | Saídas de emergência (escadas EEE e EP) |
| IN-012 | Detecção e alarme de incêndio |
| IN-006 | Extintores |
| IN-1 Parte 2 | Tabela geral de sistemas por ocupação/altura |

Site oficial: **cbmsc.sc.gov.br/sci/instrucoes-normativas**

---

## 6. Quando escalar para o Consultor Técnico

A DD identifica o risco. O Consultor Técnico faz a análise detalhada. Escalar quando:

- h próximo de 23 m (limiar EEE/EP)
- Arquiteto já flagou problemas de bombeiro na validação
- Projeto é B-2 (hospedagem) e exigências não estão claras
- Área > 2.000 m² (maior complexidade de sistemas)
- Projeto tem uso misto com comercial > 750 m²
