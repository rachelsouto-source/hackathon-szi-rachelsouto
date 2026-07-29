# 02 — Método de análise

## As cinco leituras

**Nunca leia um documento apenas uma vez.** Faça múltiplas leituras, cada uma com um
objetivo diferente:

| Leitura | Objetivo | Saída |
|---|---|---|
| **1ª — Compreensão** | Entender o documento: o que é, quem emitiu, quando, para quê, qual seu papel no processo | Nota de contexto |
| **2ª — Extração** | Extrair as informações **estruturadas** listadas em [03 — Ordem de análise](03-ordem-de-analise.md) para aquele tipo de documento | Ficha de campos + fonte |
| **3ª — Cruzamento** | Confrontar cada campo extraído com os demais documentos já lidos | Tabela comparativa |
| **4ª — Inconsistências** | Buscar ativamente o conflito: o que não bate, o que está ausente, o que está desatualizado, o que contradiz | Lista de achados classificados |
| **5ª — Parecer** | Montar o parecer com base nos achados | Documento final |

Só passe para a leitura seguinte quando a anterior estiver concluída. A 4ª leitura é a
que gera valor — pular direto da extração para o parecer produz um resumo, não uma auditoria.

## Cruzamento é obrigatório

Um campo extraído só vira conclusão depois de confrontado com **todas** as outras fontes
que também informam aquele campo. Monte sempre a tabela lado a lado antes de concluir:

| Campo | Matrícula | Espelho cadastral | Topográfico | Viabilidade | EVA / Estudo | EP | Divergência |
|---|---|---|---|---|---|---|---|
| Área (m²) | 4.200 | 4.170 | 4.050 | — | — | — | **3,57%** 🔴 |
| Nº de unidades | — | — | — | — | 68 | 69 | **1 unidade** 🟡 |

Campos com mais de uma fonte **sempre** entram nessa tabela, mesmo quando batem — a
confirmação também é resultado de auditoria.

## Rastreabilidade — sempre citar a origem

Nunca escreva:

> ~~"O terreno possui APP."~~

Escreva:

> "Segundo o levantamento topográfico (folha 02, prancha TOPO-01, rev. 03, 12/03/2026),
> foi identificada faixa de APP de 30 m ao longo do curso d'água na divisa nordeste."

ou

> "Conforme a Viabilidade Técnica Construtiva emitida pela PMF em 04/2026 (protocolo
> 00190020-2025), o terreno está inserido na zona ATR 4.5."

**Toda informação precisa possuir fonte.** O registro mínimo de cada dado é:

- **arquivo** (nome exato) + **link** no Drive;
- **localização interna** (folha, prancha, página, item, cláusula);
- **data / revisão** do documento.

Quando duas versões do mesmo documento existirem, use a **última revisão** e registre
explicitamente que versões anteriores foram descartadas — divergência entre revisões é,
ela mesma, um achado.

## Ordem de leitura

A ordem importa: cada documento é lido já sabendo o que os anteriores disseram.
Siga a sequência obrigatória de [03 — Ordem de análise](03-ordem-de-analise.md).
