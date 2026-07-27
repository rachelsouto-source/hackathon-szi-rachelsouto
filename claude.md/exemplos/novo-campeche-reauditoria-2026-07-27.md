# REAUDITORIA — NOVO CAMPECHE SPOT III (emp 10045)

> **Data:** 27/07/2026 · **Método:** `base-conhecimento/` (metodologia Rachel Souto), regras R1–R7
> **Base de evidência:** parecer de 01/07/2026 e `novo-campeche-achados.json`. **Nenhum documento
> novo foi lido** — o Drive não estava acessível nesta rodada. Portanto, tudo aqui é
> **reprocessamento das fontes já extraídas**, não nova extração.
> **Requer revisão humana.** Os itens marcados "a validar" são perguntas, não conclusões.

---

## 1. Resumo executivo

O parecer de 01/07 está correto no que afirma. A reauditoria pelo método não derruba nenhum
achado — ela encontra **seis lacunas**, das quais duas mudam materialmente a leitura de negócio:

| # | Lacuna | Criticidade | Por quê importa |
|---|---|---|---|
| N-01 | **OODC não dimensionada, nem em ordem de grandeza** | **Crítico** | Pode chegar à mesma ordem de todo o resto dos custos adicionais somados |
| N-02 | **Esgotamento sanitário / CASAN não avaliado** | **Alto** | R4 exige; Campeche é bacia sensível e há condicionante judicial no município |
| N-03 | **Taxa de permeabilidade (TP) ausente da análise** | **Alto** | Parâmetro obrigatório do R3 — e crítico num lote em área inundável |
| N-04 | **Recuos não verificados** | **Médio** | Parâmetro obrigatório do R3; ausente do quadro comparativo |
| N-05 | **Topográfico disponível e não lido** | **Alto** | R1 não pôde ser fechada tendo a fonte prevalente na pasta |
| N-06 | **Nº de unidades com fonte única** | **Médio** | R2 exige confronto entre EM × EP × estrutura |

Além disso, dois achados existentes se **acoplam** e devem virar uma pergunta única ao arquiteto
(ver §4), e um risco externo novo pode atingir a solução urbanística (ver §5).

**Conclusão mantida: 🔴 NO GO por ora** (o "PAUSADO" do parecer de 01/07), agora com uma
condicionante financeira a mais: dimensionar a OODC antes de qualquer compromisso.

---

## 2. R1 — Consistência de áreas: **não executada**

Cinco fontes documentadas:

| Fonte | Área | Δ vs matrícula |
|---|---|---|
| Matrícula 42.480 | 450,00 m² | — |
| IPTU 2026 | 450,00 m² | 0,00% |
| Consulta Ambiental FLORAM 17823068371826/2026 | 452,27 m² | +0,50% |
| Estudo de Massa ARQ_EM_R00 | 452,26 m² | +0,50% |
| EP Validação ARQ_EP_R00 | 445,00 m² | −1,11% |

Maior divergência entre extremos (FLORAM × EP): **1,61%** — abaixo do gatilho de 3% do R1.
**Mas o R1 não está fechado**, porque a fonte que prevalece para área física — o **levantamento
topográfico** — está na pasta 03 (7 subpastas, completa) e **não foi lida**.

Pelo [método](../../base-conhecimento/07-regras-de-comportamento.md), documento **disponível e não
lido** é pior que documento ausente: não gera pendência visível para ninguém. Reclassificação:

> **[Alto] R1 não executada — levantamento topográfico disponível e não lido.**
> O parecer classifica a divergência de áreas como F-09 / 🟡 baixa probabilidade. Sem o
> topográfico, o que existe é ausência de verificação, não ausência de risco.
> **Ação:** ler a pasta 03 (Planta + Memorial Descritivo + Relatório Técnico + Análise de
> Dominialidade) e fechar o R1 antes da escritura.

**Pergunta em aberto que ninguém fez:** de onde vêm os **445,00 m² do EP**? Nenhuma outra fonte
chega perto. Se o EP calculou TO e IA sobre 445 m², os percentuais do quadro urbanístico estão
sobre a base errada — ver §3.

---

## 3. R3 — Parâmetros urbanísticos: três lacunas

O quadro do parecer cobre uso, IA, TO, pavimentos, altura, marinha e vagas. Faltam **dois
parâmetros obrigatórios** do R3 e há uma questão de base de cálculo.

### 3.1 TP — taxa de permeabilidade: **ausente** *(N-03, Alto)*

A taxa de permeabilidade do ATR-2.5 não aparece em nenhum documento da análise, nem como
parâmetro legal nem como valor de projeto. Num lote que a FLORAM declarou **susceptível a
inundação e alagamento**, TP não é formalidade: é o parâmetro que conversa diretamente com o
risco declarado, e é o que a PMF cobra em análise.

**Ação:** extrair a TP mínima da Consulta de Construção PMF N° 028428/2026 e confrontar com a
área permeável do EP. Se o projeto ocupa TO 68% num terreno arenoso e inundável, a folga de
permeabilidade precisa ser demonstrada, não presumida.

### 3.2 Recuos: **não verificados** *(N-04, Médio)*

Recuo frontal, laterais e fundos não constam do comparativo. A Consulta PMF traz esses limites.

**Ação:** completar o quadro do R3 com recuo exigido × recuo projetado (implantação do EP).

### 3.3 Base de cálculo da TO — a validar

O parecer registra TO projetada = 68% e limite com OODC = 65% (50% × 1,3). A conta muda conforme
a área usada como denominador:

| Premissa | Área de projeção implícita | TO recalculada sobre 452,27 m² |
|---|---|---|
| 68% sobre **445,00 m²** (área do EP) | 302,6 m² | **66,9%** |
| 68% sobre **452,27 m²** (área PMF/EM) | 307,5 m² | 68,0% |

Em qualquer das duas hipóteses **o limite de 65% continua estourado** — o excedente é de
~8,6 m² a ~13,5 m² de projeção. Ou seja: resolver a divergência de área **não resolve** o
problema de TO, mas muda o tamanho do ajuste que o arquiteto precisa fazer.

> ⚠️ Cálculo derivado de percentuais documentados, **não** de medição de projeto. A área de
> projeção real deve vir do EP — não presumir.

---

## 4. Acoplamento entre F-05 e F-06: é uma pergunta só

O parecer trata como dois achados independentes:

- **F-05** — 3 pavimentos contáveis × máximo padrão 2 no ATR-2.5 (TDC = 0)
- **F-06** — TO 68% × máximo 65% com OODC

Eles são o mesmo problema em duas dimensões. A leitura encadeada:

1. O **3º pavimento só existe** se houver enquadramento em OODC ou incentivo (a nota da própria
   PMF menciona "edificações de 3+ pavimentos" no contexto da outorga).
2. O limite de TO de **65% já é o limite majorado por OODC** (50% × 1,3, Art. 70-A LC 482/2014).
   Ou seja, o projeto **já consumiu** o benefício da outorga na taxa de ocupação e ainda assim
   está 3 p.p. acima.
3. Logo, o projeto depende de **dois** enquadramentos simultâneos — outorga para o pavimento e
   um incentivo adicional para a TO. Nenhum dos dois está documentado no EP.

**Reformulação da pergunta ao arquiteto (Thais Lee Cleaver Brochado)** — uma só, em vez de duas:

> Qual é o enquadramento legal completo que sustenta, ao mesmo tempo, o 3º pavimento e a TO de
> 68%? Indicar artigo por artigo (LC 482/2014 / LC 739/2023 — Arts. 291-A, 292, 295-A a 295-T ou
> equivalente), com memória de cálculo, e informar sobre qual área de terreno os percentuais
> foram calculados.

Se a resposta for "não há" para qualquer um dos dois, o EP volta para a prancheta — e aí a
contagem de 49 unidades e a eficiência de 77,54% mudam junto.

---

## 5. OODC — a lacuna mais cara *(N-01, Crítico)*

O parecer registra "OODC: obrigatória (CA > 1) — **a calcular**" e deixa fora da tabela de custos.
A tabela fecha em **R$ 85.800 – 211.500 "excl. OODC"**. Isso subestima a decisão: a outorga pode
ser da mesma ordem de grandeza de tudo o mais somado.

### 5.1 Ordem de grandeza (premissas explícitas, **não** memória de cálculo)

Fórmula LC 755/2023: **CP = PGUrb × FM × IE**, aplicando na sequência o **índice de transição** e,
se pagamento em parcela única em até 30 dias, o fator **0,80**.

Premissas usadas — **todas a validar**:

| Premissa | Valor | Origem |
|---|---|---|
| PGUrb não residencial | R$ 1.121,14 /m² | Decreto 25.888/2023, citado no achado "Zoneamento e parâmetros PMF" |
| Área do terreno | 452,27 m² | Consulta Ambiental FLORAM / Estudo de Massa |
| IA do projeto | 2,22 | EP Validação, confirmado no quadro PMF |
| CA básico | 1,0 × terreno | LC 755/2023, todo o município |
| Dedução por demolição | 204,30 m² | edificação de 1999 confirmada pela FLORAM — **admissibilidade a confirmar** |

Área computável ≈ 2,22 × 452,27 ≈ **1.004 m²** → FM ≈ 1.004 − 452 ≈ **552 m²** → com dedução da
demolição ≈ **348 m²**.

| Cenário | IE | Transição | CP | À vista (×0,80) |
|---|---|---|---|---|
| Melhor caso | 0,50 | 0,5 | ~R$ 97 mil | **~R$ 78 mil** |
| Provável (ver 5.2) | 1,00 | 0,5 | ~R$ 195 mil | ~R$ 156 mil |
| Pior caso | 1,00 | 0,7 | ~R$ 273 mil | **~R$ 218 mil** |

> Ordem de grandeza para dimensionar risco, **não** valor de outorga. Substituir pela memória de
> cálculo assim que o enquadramento do §4 estiver definido.

### 5.2 Por que o IE provavelmente **não** é 0,50

O IE médio padrão de 0,50 exige **três critérios simultâneos** (Decreto 25.887/2023):
PGUrb **residencial** nas faixas 1–5, vagas ≤ 1,5 × nº de unidades, e eficiência
(privativa/total) ≥ 60%.

O projeto é **apart-hotel** e a própria análise adota o PGUrb **não residencial**
(R$ 1.121,14/m²) — o primeiro critério não é atendido. Somando as 3 lojas, o uso predominante
não residencial (≥ 75%) aplica esse PGUrb a toda a edificação. **Conclusão provável: IE = 1,00**,
o que **dobra** a contrapartida em relação ao melhor caso.

> Isso não aparece em lugar nenhum do parecer de 01/07 e é, sozinho, ~R$ 78 mil de diferença.

### 5.3 Risco de data — não é constante, é parâmetro

O índice de transição da LC 755/2023 é **0,5 na 1ª fase e 0,7 na 2ª**. A 1ª fase foi prorrogada
pelo Decreto 27.230/2024 e houve prorrogações sucessivas; **a data-limite vigente precisa ser
conferida na data do protocolo**. Na virada, o custo sobe **+40%**.

**Ação:** tratar o índice como parâmetro por **data de protocolo** e, se o protocolo estiver
próximo da virada, isso vira argumento de cronograma — não de projeto.

### 5.4 Alavanca não explorada

A **demolição dos 204,30 m²** aparece no parecer apenas como custo (R$ 40–80 mil). Ela também é
**dedução na base da outorga** — no cenário acima, reduz o FM em ~37% e vale mais do que custa.
Confirmar a admissibilidade e a documentação exigida para pleitear a dedução.

---

## 6. R4 — Esgotamento sanitário: eixo inteiro não avaliado *(N-02, Alto)*

O R4 exige verificar **sistema de esgoto**. O parecer cobre APP, UC, inundação, vegetação e
demolição, mas **não menciona CASAN nem esgotamento sanitário** — nem como OK, nem como pendência.

Em Florianópolis isso é condicionante estrutural: a **ACP nº 5005775-70.2012.4.04.7200/SC**
condiciona aprovações à comprovação de esgotamento sanitário em operação, e a situação varia
**por bacia**. O Campeche é justamente uma região onde essa comprovação já travou processos.

**Ação:** obter declaração/viabilidade de esgoto da CASAN para o endereço (Rua Gilmar Darli
Vieira, 106) e verificar a situação da bacia frente à ACP. Sem isso, o eixo ambiental do parecer
está incompleto — e é um item que trava aprovação, não que encarece.

**Precedente a consultar:** os empreendimentos da Seazone no Campeche (Campeche Spot, emp 2595 —
base histórica registra perfil ambiental com gargalo) devem ter esse histórico. Consultar a aba
`sintese` por `cidade = "Florianópolis, SC"`, `disciplina = "concessionárias"`, tema
"água e esgoto (CASAN)".

---

## 7. R2 — Nº de unidades: fonte única *(N-06, Médio)*

O parecer registra **49 unidades** (2 PCD + 47 simples) com fonte única: EP Validação ARQ_EP_R00.
O R2 exige o mesmo número em **todos** os documentos que o informam — no mínimo Estudo de Massa
× EP. O Estudo de Massa (ARQ_EM_R00) foi lido para área, mas o nº de unidades dele não foi
confrontado.

**Ação:** extrair o nº de unidades, vagas e pavimentos do ARQ_EM_R00 e comparar com o EP.
Divergência aqui costuma ser o primeiro sintoma de que o produto mudou sem atualizar o estudo.

---

## 8. R5, R7 e completude — sem alteração

- **R5 (geotécnico):** SPT ausente em lote **declarado inundável**. O parecer já trata como
  crítico e a reauditoria confirma. Pela regra de criticidade, a pendência **herda** o risco que
  esconde: sem SPT, o risco geotécnico é *desconhecido*, não *baixo*. Fundação (pasta 11) e EVA
  (pasta 04) vazias reforçam.
- **R7 (bombeiro):** h = 9,18 m < 12 m → escada natural, sem EEE/EP. Correto e com folga de
  ~2,8 m até a primeira faixa de custo. Único ponto: confirmar que a altura foi medida até o
  **piso do último pavimento habitável** — se o rooftop tiver uso de lazer, verificar se ele
  entra na contagem do CBMSC. Mesmo entrando (12,24 m no barrilete), a mudança seria para EEE, não
  EP. **Informativo.**
- **R6 (completude):** lista do parecer está correta. Acrescentar à lista de pendências:
  declaração de esgoto CASAN (§6), TP e recuos (§3), leitura do topográfico (§2), conceito
  estrutural (pasta 10 tem só alvenaria/drywall — não é projeto estrutural).

---

## 9. Risco externo a checar antes de contar com incentivo

Se a solução urbanística do §4 depender de **incentivo** (e não só de OODC), verificar se o
dispositivo específico está afetado por decisão judicial em curso. Há precedente ativo na
carteira: a liminar da ADI no TJSC que suspendeu os arts. 13 e 14 do **Decreto 27.952/2025**
atingiu projeto já aprovado no **Ilha do Campeche Spot I** (mérito previsto para ~05/08/2026).

Não é o mesmo dispositivo até prova em contrário — mas é exatamente o tipo de risco que só
aparece cruzando com o histórico. **Ação:** ao receber o enquadramento do arquiteto, checar se o
artigo invocado está sob questionamento.

---

## 10. O que muda no parecer de 01/07

| Item do parecer 01/07 | Reauditoria |
|---|---|
| F-09 área 450 × 452 — 🟡 baixa | **Alto** — R1 não executada, topográfico disponível e não lido |
| F-05 pavimentos + F-06 TO — dois achados | **Um** achado com duas manifestações; uma pergunta só ao arquiteto |
| OODC "a calcular", fora da tabela de custos | **Crítico** — ~R$ 78 mil a ~R$ 218 mil; IE provavelmente 1,00; risco de data |
| Custos adicionais R$ 85,8–211,5 mil | Com OODC: **~R$ 164 mil a ~R$ 430 mil** (ordem de grandeza) |
| Ambiental: APP, UC, inundação, vegetação | Falta **esgoto/CASAN + ACP** — eixo obrigatório do R4 |
| Urbanístico: uso, IA, TO, pav., altura | Faltam **TP e recuos** — parâmetros obrigatórios do R3 |
| 49 unidades | Fonte única — R2 não executada |
| Demolição = custo | Também é **dedução** na base da outorga |

**Conclusão:** 🔴 **NO GO** enquanto não houver (1) enquadramento legal do 3º pavimento e da TO,
(2) sondagem SPT, (3) OODC dimensionada com memória de cálculo, (4) certidões renovadas e
averbação da hipoteca confirmada, (5) declaração de esgoto da CASAN.

Resolvidos (1) a (5) sem surpresa, o caso migra para **GO COM RESSALVAS**.
