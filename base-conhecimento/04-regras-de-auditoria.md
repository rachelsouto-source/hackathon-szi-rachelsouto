# 04 — Regras obrigatórias de auditoria (R1–R7)

**Sempre executar automaticamente**, em toda DD, mesmo quando nada parece errado.
Cada regra produz **achados**, e cada achado tem: descrição, **fonte**, **criticidade**
([05](05-criticidade.md)) e ação recomendada.

Regra que não pôde ser executada por falta de documento **não é "OK"** — é pendência
(ver [R6](#r6--completude-documental)).

---

## R1 — Consistência de áreas

Comparar as áreas informadas por **todas** as fontes disponíveis:

matrícula (soma, se houver mais de uma) × espelho cadastral × confrontantes ×
levantamento topográfico × área considerada na proposta.

```
dif% = | área_topográfica − área_matrícula | / área_matrícula × 100
```

- **dif% > 3% ⇒ classificar como risco** e exigir **retificação de matrícula**.
- Mais de uma matrícula ⇒ avaliar **unificação / amembramento**.
- Qualquer divergência entre as fontes ⇒ listar **todas** as áreas lado a lado no parecer,
  ainda que abaixo de 3%.

Registrar também o impacto: área menor que a registrada reduz potencial construtivo e,
portanto, o valor justo do terreno.

---

## R2 — Quantidade de unidades

Comparar a quantidade de unidades em **todos** os documentos que a informam:
estudo de massa, EVA, validação do EP, estrutural, memorial, proposta.

**Todos devem apresentar o mesmo número.** Caso contrário: **gerar inconsistência**,
apontando documento por documento qual número consta e qual é o vigente.

O mesmo confronto vale para vagas, pavimentos e altura.

---

## R3 — Parâmetros urbanísticos

Comparar os parâmetros do **projeto** (EP / estudo de massa / estrutural) com os
parâmetros **legais** (viabilidade construtiva + plano diretor do zoneamento):

| Parâmetro | Confronto |
|---|---|
| **TO** — taxa de ocupação | projetada ≤ máxima? |
| **CA** — coeficiente de aproveitamento | projetado ≤ máximo? há outorga onerosa envolvida? |
| **TP** — taxa de permeabilidade | projetada ≥ mínima? |
| **Recuos** | frontal, laterais e fundos atendidos? |
| **Gabarito** | nº de pavimentos e altura ≤ máximo? |
| **Uso** | o uso pretendido é permitido na zona? |

Qualquer parâmetro não atendido ⇒ achado de criticidade alta ou crítica + indicação de
readequação do anteprojeto. Se o atendimento depender de **outorga, incentivo, fruição
pública ou operação urbana**, quantificar o **custo** e registrar o risco de mudança de
regra (ver [09 — Florianópolis](09-florianopolis.md)).

---

## R4 — Riscos ambientais

Validar, com fonte, cada um dos itens:

- **APP** — existência, faixa, área não edificável, % de área útil remanescente, e se o
  projeto a respeita.
- **Terreno de marinha** — se sim, exigir afastamento demarcado no topográfico **e** no
  ambiental, e conferir a **documentação da SPU** ([bloco 10](03-ordem-de-analise.md#10-spu--terreno-de-marinha)).
- **SPU** — RIP, ocupação, aforamento, autorização. Marinha sem documentação SPU ⇒ pendência crítica.
- **Supressão** de vegetação — nº de indivíduos, autorização exigida, compensação e custo.
- **UC** — imóvel em unidade de conservação ou zona de amortecimento ⇒ achado crítico até
  prova documental em contrário.
- **Demolição** — construções existentes exigem alvará de demolição (prazo, custo e,
  em alguns municípios, dedução de outorga).
- **Sistema de esgoto** — comprovação de esgotamento sanitário / declaração da
  concessionária; condicionantes judiciais aplicáveis ao município.

---

## R5 — Riscos geotécnicos

Validar, cruzando sondagem × fundação × estrutural:

- **Solo mole** — camadas de baixa resistência, aterro, turfa.
- **Lençol freático** — NA raso, necessidade de rebaixamento e seu licenciamento.
- **Fundações especiais** — tipo recomendado pela sondagem × tipo adotado no projeto.
- **Contenções** — necessidade em função de desnível, divisas e vizinhança.

Toda solução onerosa vira linha no impacto de custo/prazo. Vibração e recalque em
vizinhos edificados são risco de implantação, não só de custo.

---

## R6 — Completude documental

Validar a presença de **todos** os documentos obrigatórios de
[03 — Ordem de análise](03-ordem-de-analise.md) e **informar os documentos faltantes**.

- Documento ausente, ilegível ou desatualizado ⇒ **pendência**, nunca presunção.
- Documento em revisão superada ⇒ registrar e exigir a versão vigente.
- Terreno de marinha ⇒ documentação SPU entra como obrigatória.

A lista de pendências é seção obrigatória do parecer e condiciona a conclusão: pendência
crítica em aberto impede um **GO** limpo.

---

## R7 — Bombeiros / CBMSC

Extrair a **altura do projeto** (piso do último pavimento habitável até o nível de
descarga) e classificar:

| Faixa | Exigência típica | Impacto de custo |
|---|---|---|
| **até 12 m** | escada não enclausurada | baixo |
| **12 a 23 m** | **EEE** — escada enclausurada com exaustão (ou conforme IN vigente) | moderado |
| **acima de 23 m** | **EP** — escada pressurizada | **alto** — shaft, equipamento, manutenção |

Validar ainda:

- **EEE / EP** — o tipo indicado no projeto bate com a altura real?
- **ocupação** e **classe** — grupo de ocupação (residencial multifamiliar × hotel
  residencial / apart-hotel) e classe de risco. Produto de hospedagem pode atrair
  exigências adicionais de brigada e alarme; confirmar com o órgão em caso de dúvida.
- **NBR** aplicáveis (saídas de emergência, escadas, acessibilidade).
- **IN CBMSC** vigentes (Instruções Normativas) para o estado de Santa Catarina.

**Zona de risco:** altura entre ~20 m e ~25 m — pequena variação de projeto muda EEE → EP
e encarece significativamente. Sinalizar sempre, mesmo quando o projeto atual está abaixo
do limite.

Escopo na DD: o objetivo **não** é a análise de conformidade completa do preventivo, e sim
identificar **riscos de custo, prazo ou bloqueio** que afetem a decisão de compra.
