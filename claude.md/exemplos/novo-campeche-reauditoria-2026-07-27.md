# REAUDITORIA — NOVO CAMPECHE SPOT III (emp 10045)

> **Data:** 27/07/2026 · **Método:** `base-conhecimento/` (metodologia Rachel Souto), regras R1–R7
> **Base de evidência:** parecer de 01/07/2026, `novo-campeche-achados.json` e — a partir da
> **§11 (adendo)** — dois documentos do Drive que o parecer não havia usado.
> **Leia a §12 primeiro.** O documento foi construído em três rodadas: §§1–10 sem acesso ao
> Drive, §11 com dois documentos avulsos, **§12 com as fontes primárias da PMF em mãos**.
> A §12 corrige conclusões das rodadas anteriores — inclusive uma da própria §2 — e é a que
> vale. A conclusão final está em §12.7.
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

---

# 11. ADENDO — leitura do Drive (27/07/2026)

Com acesso ao Drive (conta `melina.marambaia@seazone.com.br`), foram localizados **dois
documentos que o parecer de 01/07 não usou**. Ambos existiam antes dele.

> ⚠️ **Limite de acesso:** a conta conectada **não enxerga** a pasta `1.47 - [10045] Novo
> Campeche Spot III` (retorna 404) nem a pasta-mãe de lançamentos. Portanto o **levantamento
> topográfico**, a **Consulta de Construção PMF N° 028428/2026** e a **Consulta Ambiental
> FLORAM N° 17823068371826/2026** continuam não lidos — as pendências N-05 e parte de N-03/N-04
> seguem abertas. Para fechá-las, é preciso compartilhar a pasta do empreendimento com a conta
> conectada.

---

## 11.1 Análise PDM — [ID 10045] Novo Campeche III (Júlia, 24/06/2026)

Planilha [`[ID - 10045] Novo Campeche III - Análise PDM`](https://docs.google.com/spreadsheets/d/1aZiddeZcqe25OyRGsq0drxbMyzPQjAdtnXQNVcCFZXA/edit),
mesma data das consultas PMF/FLORAM. **Não é citada em nenhum ponto do parecer nem do
`achados.json`** — e responde diretamente às duas perguntas que o parecer classificou como
críticas.

### O 3º pavimento tem justificativa documentada *(muda F-05)*

A PDM registra o gabarito como:

> 2 pavs base · **1 pav uso misto** · 1 pav cobertura · **4 pavimentos**

O pavimento extra vem do **incentivo de uso misto (+1 pavimento)**, com contrapartida explícita:

- área comercial ≥ **1/6 da área total computável do pavimento incentivado**, nunca inferior a 25 m²;
- **fachada ativa** ≥ 1/3 da fachada vinculada a via (terreno com testada > 15 m), nunca inferior a 3 m;
- fachada de loja de 5 m.

Também registra o **Art. 66-A** (pilotis: +1 pavimento e +3,60 m em zoneamentos de até três
pavimentos que usem incentivo de uso misto, com TO de áreas fechadas ≤ 30%).

> **Reclassificação de F-05: de 🔴 Crítico ("sem justificativa") para 🟡 Atenção
> ("justificativa existe, contrapartida não verificada").**
> A pergunta deixa de ser *"por que 3 pavimentos?"* e passa a ser:
> **as 3 lojas atingem 1/6 da área computável do pavimento incentivado, e a fachada ativa
> atinge 1/3 da testada?** O parecer só verificou a quantidade de lojas ("3 lojas, mínimo 1 ✓"),
> que não é a condicionante que vincula.

### A TO de 68% tem composição documentada *(muda F-06)*

A PDM decompõe:

> **TO torre outorgado: 68% = TO×1,3 (65%) + 2% de arte + 1% de sustentabilidade**

Ou seja: os 3 p.p. acima do teto de OODC vêm de **2% por arte pública** e **1% por
sustentabilidade** — incentivos nomeados, não uma folga inexplicada.

> **Reclassificação de F-06: de "sem incentivo declarado" para "dois incentivos declarados, ambos
> a documentar formalmente".** Duas ressalvas novas:
> 1. **Arte pública é uma alavanca que o time decidiu evitar** (feedback da weekly de 21/07 sobre
>    o material de outorga para Terrenos). Se essa diretriz vale aqui, 2% dos 68% caem e a TO
>    volta a estourar. **Confirmar com Terrenos antes de considerar o parâmetro fechado.**
> 2. Ambos os incentivos precisam de comprovação de projeto (peça de arte, itens de
>    sustentabilidade) — vira custo e vira condicionante de aprovação, não é ganho gratuito.

### Taxa de permeabilidade *(fecha o lado legal de N-03)*

> **IP mín = 30% · permitido 70% impermeável**

O parâmetro legal existe e a PDM o registra. **Falta o valor do projeto**: com TO de 68% mais
acessos, calçadas e áreas técnicas, os 30% permeáveis são apertados — e o terreno é
**declarado inundável** pela FLORAM. Continua sendo verificação obrigatória no EP.

### Recuos — e um risco de borda que ninguém viu *(fecha N-04 no lado legal)*

A PDM traz os parâmetros:

| Recuo | Exigência |
|---|---|
| Atingimento viário | 0 m |
| Frontal | 4 m no térreo · 2,8 m demais pavimentos |
| Laterais e fundos | **1,5 m** para fachada até **9,50 m** (Art. 74) |
| Laterais e fundos | **3 m** e ≥ **1/7 da altura** para fachada acima de 9,50 m (Art. 75) |

> **[Alto] Risco de borda a 9,50 m.** A altura de fachada do projeto é **9,18 m**
> (Consulta PMF / Corte B). A margem até o degrau do Art. 75 é de **32 cm**. Qualquer ajuste de
> pé-direito, laje, platibanda ou nível de soleira que empurre a fachada acima de 9,50 m **dobra
> o afastamento lateral e de fundos** (1,5 m → 3 m) — o que, num lote de ~450 m² com TO de 68%,
> reduz área por pavimento e derruba a conta de unidades.
>
> É a mesma natureza do risco de 23 m do bombeiro, e é mais apertado: 32 cm contra 2,8 m.
> Nem o parecer nem a PDM sinalizam essa proximidade.

Complemento relevante do **Art. 75, §2º**: *"os pavimentos decorrentes de aplicação de incentivos
obedecerão os afastamentos do pavimento inferior"* — ou seja, o pavimento de uso misto não
ganha afastamento próprio.

A PDM também registra: **sacadas inviáveis** neste projeto (exigiriam 1,5 m de afastamento) —
informação de produto que não está no parecer.

### Coeficiente de aproveitamento — três números diferentes 🔴

| Fonte | IA |
|---|---|
| Consulta PMF (via PDM) | básico **1,0** + adicional outorga **0,6** = **1,6 "máximo"** |
| Terrenos (via PDM) | **2,245** "com incentivos" |
| Parecer 01/07 | **2,4** máximo total (G2 1 + G3 0,6 + G4 0,8) · projeto **2,22** |

> **[Crítico] Não há uma fonte única sobre o teto de aproveitamento.** Se o teto por outorga é
> 1,6 e o projeto está em 2,22, todo o excedente depende de **incentivos empilhados** — os
> mesmos incentivos que sustentam o 3º pavimento e a TO. Se algum deles cair, cai também o
> potencial construtivo que forma o preço.
> **Ação:** obter do arquiteto **um único quadro** de IA: básico, adicional por outorga, adicional
> por cada incentivo (com o artigo), e o total — reconciliado com a Consulta PMF.

### Base de cálculo da outorga — número documentado, mas não reconciliado

A PDM registra, na linha de outorga: **"Área do terreno − IA básico: 491,71 m²"**.

Isso é uma **base de outorga concreta**, que a §5.1 desta reauditoria só conseguiu estimar
(~552 m² brutos, ~348 m² após dedução da demolição). Os dois números não batem, e nenhum dos
dois está fechado.

Recalculando com a base da PDM e o PGUrb não residencial de R$ 1.121,14/m²:

| Cenário | IE | Transição | CP | À vista (×0,80) |
|---|---|---|---|---|
| IE favorável | 0,50 | 0,5 | ~R$ 138 mil | ~R$ 110 mil |
| **Provável** (IE 1,00 — ver §5.2) | 1,00 | 0,5 | ~R$ 276 mil | **~R$ 221 mil** |
| Pior caso | 1,00 | 0,7 | ~R$ 386 mil | ~R$ 309 mil |

> A faixa **sobe** em relação à estimativa da §5.1 (~R$ 78–218 mil) porque a base de 491,71 m²
> aparentemente **não deduz a demolição**. Isso reforça a §5.4: confirmar se os 204,30 m²
> demolidos são dedutíveis pode valer ~R$ 100 mil.
> Segue sendo ordem de grandeza — **não** memória de cálculo.

### Bombeiro — contradição direta com o parecer 🔴

A PDM registra:

> Maior distância de caminhamento **33 m** · faixa **6 < H ≤ 12** ·
> **Apart (B-2): EPT — Escada Protegida** · Multi (A-2): ECM — Escada Comum
> Limite de caminhamento: **40 m sem DAI** · **50 m com DAI** (detecção automática de incêndio)

O parecer de 01/07 conclui: *"Escada Natural apenas. Sem EEE ou EP"* e recomenda confirmar
"distância de percurso ≤ 20 m até a escada sem sprinkler".

> **[Alto] Dois documentos discordam sobre o tipo de escada exigido.** A PDM diz que o
> enquadramento **B-2 (apart-hotel)** — que é justamente o uso aprovado — exige **escada
> protegida (EPT)**, não escada comum/natural. O critério de caminhamento também diverge
> (40/50 m na PDM × 20 m no parecer).
>
> Não é o degrau de custo da EP, mas **EPT tem custo e área** que a escada natural não tem, e o
> parecer registrou o item como **OK ✅** — ou seja, um item verde apoiado na premissa errada.
> **Ação:** fechar o enquadramento CBMSC (grupo, classe, tipo de escada e limite de caminhamento)
> contra a IN vigente antes de tratar bombeiro como resolvido.

### Vagas e bicicletários — divergência de exigência

| Item | PDM (24/06) | Parecer (01/07) |
|---|---|---|
| Vagas de automóvel | apart: **1 vaga de emb/des** | **0 exigidas** ✅ |
| Bicicletas | **10** (5 comercial + 5 apart) | **5** (exigido 5 ✅) |

A PDM anota que o uso residencial transitório e comercial com menos de 50 unidades é dispensado
de vaga de estacionamento **e de embarque/desembarque** (art. 79-A, II e III, e art. 84) — mas
ao mesmo tempo registra a exigência de 1 vaga de emb/des e de 10 bicicletários, e observa
*"usar apart em função disso"*. **Item contraditório dentro do próprio documento** — precisa de
uma leitura só. Se forem 10 bicicletários, o projeto atende metade.

### Nº de unidades — a segunda fonte apareceu, e diverge *(fecha N-06)*

A PDM registra, na linha de elevadores: *"adotado 1 elevador (**45 unidades**)"*.
O EP Validação registra **49 unidades** (2 PCD + 47 simples).

> **[Médio] R2 executada: 45 (PDM, 24/06) × 49 (EP, 01/04).** Diferença de 4 unidades.
> Pode ser evolução de projeto entre abril e junho, pode ser erro. Em qualquer hipótese,
> **o dimensionamento do elevador foi feito para 45** e a eficiência/VGV foram calculados
> para 49. **Ação:** confirmar o número vigente e refazer o dimensionamento no que estiver
> ancorado no número errado.

### Área do terreno — sexta fonte *(complementa §2)*

A PDM acrescenta duas informações à tabela de áreas:

| Fonte | Área |
|---|---|
| **Terrenos** | **449,839 m²** |
| Geoportal | 452,27 m² |
| Atingimento viário | **0 m²** |

Com Terrenos em 449,839 m² e FLORAM/Geoportal em 452,27 m², a dispersão total continua em
**1,66%** (EP 445,00 × Geoportal 452,27) — abaixo dos 3% do R1, mas ainda com **seis** valores
e **sem** o topográfico, que é a fonte que prevalece. **N-05 permanece aberta.**

### A própria PDM está incompleta — e confirma N-02

Os blocos 4 a 8 da análise estão marcados como **não executados** (`FALSE`):

| Bloco | Itens não executados |
|---|---|
| 4. Viabilidade técnica | topografia · **infraestrutura (energia, saneamento, pavimentação)** · restrições ambientais · condensadoras · medidores · lixo |
| 5. Potencial construtivo | potencial total · nº máx. de pavimentos · máx. de unidades · volumetria |
| 6. Eficiência | layout · dimensionamento de áreas comuns |
| 7. Mercado e público | estudo de mercado local |
| 8. Validação | revisão interna · alinhamento com diretores |

> O item **"Infraestrutura disponível: energia, saneamento, pavimentação"** está explicitamente
> em aberto. Isso **confirma N-02**: o eixo de esgotamento sanitário/CASAN não foi avaliado por
> ninguém — não é omissão do parecer, é uma etapa que a análise urbanística também deixou
> pendente. E, com a ACP nº 5005775-70.2012.4.04.7200/SC no município, é item que **trava
> aprovação**.
>
> Também não executado: **validação interna e alinhamento com diretores** — a PDM que sustenta
> os parâmetros do projeto ainda não passou por revisão formal.

---

## 11.2 Proposta prévia assinada — Clicksign #030012cd (02–03/06/2026)

O parecer de 01/07 lista a *"proposta de compra e venda"* como **"a solicitar"**. Ela existe
desde junho, na pasta do jurídico:
[`assinado_V1.0_-_Terrenos_Proposta_Previa_Novo_Campeche…Clicksign.pdf`](https://drive.google.com/file/d/1NNgET_cIYHRFru_yP_8iVwni2yve1Fu8/view).

### O negócio

| Item | Valor |
|---|---|
| **Preço total** | **R$ 5.000.000,00** |
| Arras confirmatórias (na assinatura do CCV) | R$ 250.000,00 |
| 2ª parcela (até 60 dias das arras) | R$ 250.000,00 |
| 3ª parcela (até 60 dias da 2ª) | R$ 2.000.000,00 |
| Saldo | 5 × R$ 500.000,00 mensais, a 1ª em 30 dias da 3ª parcela |
| Foro | Comarca de Florianópolis/SC |
| Data | Florianópolis, **02 de junho de 2026** |

**Compradora:** Seazone Investimentos Ltda. (CNPJ 34.226.198/0001-48), rep. por Matheus Alberto
Ambrosi. **Vendedores:** Carlos Eduardo Schmidt Capela **e** Roberta Pires de Oliveira, ambos
qualificados como **divorciados**.

### 🔴 A proposta não está assinada pelos vendedores

O log da Clicksign do próprio documento registra **duas** assinaturas:

- **Matheus Alberto Ambrosi** — assinou **como parte** em 03/06/2026 13:55
- **Tatiana Barros de Andrade Mello Gonçalves de Souza** — assinou **como testemunha** em 03/06/2026 19:45

A lista de assinatura criada em 03/06 contém **apenas esses dois e-mails**. **Carlos e Roberta
não foram adicionados à lista de assinatura e não constam como signatários.**

> **[Crítico] O documento chamado "assinado" vincula apenas a Seazone.** Ou existe uma via
> separada assinada pelos vendedores que não está nesta pasta, ou **não há acordo formalizado
> sobre os R$ 5 milhões** — apenas uma proposta emitida.
> **Ação:** localizar a via com assinatura dos vendedores. Se não existir, tratar o preço como
> **não acordado** e o cronograma abaixo como não iniciado.

### 🔴 Os prazos da proposta já venceram

| Cláusula | Prazo | Vencimento | Situação em 27/07 |
|---|---|---|---|
| 2.2 — assinar a **proposta definitiva** | 15 dias da prévia | ~18/06/2026 | **vencido há ~39 dias** |
| 2.2 — preço mantido se CCV assinado | 45 dias da definitiva | — | prejudicado |
| 3.2 — vendedores entregam documentos | **2 dias** da assinatura | ~05/06/2026 | **vencido** |

> **[Crítico] A trava de preço da cláusula 2.2 caducou.** O preço e a forma de pagamento só se
> mantinham inalterados se a proposta definitiva fosse assinada em até 15 dias. Passaram-se ~55
> dias. **Os R$ 5 milhões não estão mais garantidos por este instrumento** — o vendedor pode
> renegociar, e qualquer economia obtida nas ressalvas técnicas pode ser devolvida no preço.
> Isso é matéria de decisão comercial imediata, não de DD.

### A cláusula 3.2 reforça F-01

A proposta exige dos vendedores, em 2 dias, *"certidão atualizada de inteiro teor da matrícula
com ônus e ações (**últimos 30 dias**)"*. As três certidões da pasta estão vencidas (F-01).
Ou seja: **a obrigação documental foi contratada, o prazo passou, e o documento não foi
entregue** — a inadimplência documental é do vendedor e é argumento de negociação.

### O que o preço significa para a análise

| Métrica | Valor |
|---|---|
| Preço | R$ 5.000.000,00 |
| Por m² de terreno (452,27 m²) | ~R$ 11.055/m² |
| Custos adicionais estimados (§10, com OODC pela base da PDM) | ~R$ 200 mil a ~R$ 520 mil |
| Custos adicionais como % do preço | **~4% a ~10%** |

O bloco 12 do método (proposta × potencial construtivo) **ainda não pode ser fechado**: a
cláusula 1.1 remete a uma tabela com a descrição do imóvel que não foi extraível do PDF —
**não foi possível confirmar qual área o negócio considera**. Verificar manualmente.

---

## 11.3 Efeito líquido do adendo sobre a conclusão

| Achado | Antes do adendo | Depois |
|---|---|---|
| F-05 — 3º pavimento | 🔴 sem justificativa | 🟡 justificado (uso misto); **contrapartida de 1/6 não verificada** |
| F-06 — TO 68% | 🔴/🟡 sem incentivo declarado | 🟡 declarado (2% arte + 1% sust.); **arte pública contraria diretriz do time** |
| N-03 — TP | Alto, parâmetro desconhecido | parâmetro conhecido (IP ≥ 30%); **valor de projeto pendente** |
| N-04 — recuos | Médio, não verificados | parâmetros conhecidos + **novo achado Alto: borda de 32 cm em 9,50 m** |
| N-06 — unidades | Médio, fonte única | **R2 executada: 45 × 49 — divergência confirmada** |
| Bombeiro | ✅ OK no parecer | 🔴 **contradição: PDM exige EPT para B-2** |
| IA / potencial | não questionado | 🔴 **três tetos diferentes (1,6 / 2,245 / 2,4)** |
| Proposta / CCV | "a solicitar" | 🔴 **existe, R$ 5 mi, sem assinatura dos vendedores, prazos vencidos** |
| N-02 — esgoto/CASAN | Alto | **confirmado**: item em aberto também na PDM |
| N-05 — topográfico | Alto | **permanece**: sem acesso à pasta do empreendimento |

**Conclusão revisada: 🔴 NO GO**, com a lista da §10 acrescida de:

6. **Localizar a via da proposta assinada pelos vendedores** — ou reconhecer que não há preço acordado.
7. **Repactuar o instrumento**: os prazos das cláusulas 2.2 e 3.2 venceram.
8. **Reconciliar o quadro de IA** em uma fonte única, com artigo por artigo dos incentivos.
9. **Confirmar com Terrenos** se o incentivo de arte pública pode ser usado aqui.
10. **Fechar o enquadramento CBMSC** (B-2 → EPT?) antes de manter bombeiro como item verde.
11. **Compartilhar a pasta `1.47 - [10045]`** com quem for rodar a DD — sem o topográfico, a
    Consulta PMF e a Consulta FLORAM em mãos, R1 e parte de R3/R4 seguem sem execução.

## 11.4 O padrão que aparece nas duas rodadas

Três documentos decisivos existiam e não foram lidos por quem escreveu o parecer: o
**levantamento topográfico** (pasta 03, completa), a **Análise PDM** e a **proposta prévia
assinada**. Nenhum deles estava faltando — todos estavam a um clique.

O modo de falha da DD deste caso **não é falta de documento; é falta de varredura**. Vale
incorporar ao método: *antes de concluir qualquer eixo, listar exaustivamente o que existe na
pasta do empreendimento e marcar arquivo por arquivo como lido / não lido / não aplicável* —
e tratar "existe e não foi lido" como pendência de mesma severidade que "não existe".

---

# 12. RODADA 3 — fontes primárias lidas (27/07/2026)

Com a pasta `1.47 - [10045]` compartilhada, foram lidas na fonte a **Consulta Automatizada
para Fins de Construção N° 028428/2026** e a **Consulta Ambiental N° 17823068371826/2026**
(ambas de 24/06/2026), e varrida a estrutura completa de `02 - Projetos`.

O resultado muda a conclusão do caso.

---

## 12.1 🔴 ACHADO DECISIVO — TO×1,3 e incentivo de Uso Misto são mutuamente excludentes

A nota **(OODC)** da Consulta PMF N° 028428/2026, seção 5 — Limites de Ocupação, diz
textualmente:

> "As edificações de três ou mais pavimentos que fizerem uso da outorga onerosa do direito de
> construir poderão aumentar em até trinta por cento a taxa de ocupação (TOx1,3), **com exceção
> dos pavimentos que possuem taxa de ocupação diferenciada prevista no art. 71 da LC 482/2014
> e das edificações que fizerem uso do incentivo de Uso Misto**, conforme Art. 70-A da LC
> 482/2014."

O projeto do Novo Campeche III usa **os dois ao mesmo tempo**:

| Uso | Para quê | Fonte |
|---|---|---|
| **Incentivo de Uso Misto** | obter o 3º pavimento | Análise PDM: "2 pavs base · 1 pav uso misto · 1 pav cobertura" |
| **TO×1,3 (OODC)** | chegar aos 65% que formam a base dos 68% | Análise PDM: "TO torre outorgado: 68% = TO×1,3 (65%) + 2% arte + 1% sust" |

**Pela regra da própria prefeitura, a edificação que usa o incentivo de Uso Misto não pode
aplicar o TO×1,3.** Os dois caminhos são alternativos, não somáveis.

### O que isso faz com a taxa de ocupação

| Hipótese | TO máxima admissível | Projeto | Excedente |
|---|---|---|---|
| Como a Análise PDM assumiu (uso misto **+** TO×1,3) | 65% + 2% + 1% = **68%** | 68% | 0 |
| **Pela regra literal da Consulta PMF** (uso misto exclui TO×1,3) | 50% + 2% + 1% = **53%** | 68% | **15 p.p.** |

Em área de terreno, isso é a diferença entre um ajuste de ~13 m² de projeção e um corte de
**~68 m²** (sobre 452,27 m²).

> **Reclassificação de F-06: de 🟡 Atenção para 🔴 Crítico.**
> O parecer de 01/07 tratou como "3% acima do limite". A §11.1 desta reauditoria tratou como
> "justificado, falta documentar". Com a fonte primária em mãos, a leitura correta é:
> **o projeto pode estar 15 pontos percentuais acima do teto**, porque combina dois
> instrumentos que a legislação apresenta como excludentes.
>
> E o problema é circular: **abrir mão do uso misto para recuperar o TO×1,3 derruba o
> 3º pavimento**, que é justamente o que o uso misto concede. Não há como manter os dois.

**Ação — a pergunta única ao arquiteto passa a ser:**
> O projeto usa o incentivo de Uso Misto para o 3º pavimento **e** o TO×1,3 do Art. 70-A para a
> taxa de ocupação. A nota (OODC) da Consulta 028428/2026 exclui expressamente do TO×1,3 as
> edificações que usam o incentivo de Uso Misto. Como o projeto se sustenta? Se a leitura
> estiver correta, qual das duas alternativas o projeto adota — 3 pavimentos com TO de até 53%,
> ou 2 pavimentos com TO de até 68%? E qual o impacto de cada uma no nº de unidades e no VGV?

Enquanto essa resposta não vier, **nenhuma conta de potencial construtivo, unidades, VGV ou
outorga deste empreendimento está de pé.**

---

## 12.2 🔴 O coeficiente de aproveitamento não fecha sem TDC

Tabela oficial da Consulta PMF, ATR-2.5:

| Nº máx. pav. padrão (A1) | Acréscimo por TDC (A2) | T.O. máx. | **T.I. máx.** | Alt. fachada | Alt. cumeeira | CA mín. | CA básico (G2) | +OODC (G3) | +TDC (G4) | +Subsolo (G5) | **Máx. total (G6)** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **2** | **0** | **50%** | **70%** | **10,5 m** | **13 m** | 0,25 | **1,0** | **0,6** | **0,8** | 0 | **2,4** |

Os três números divergentes da §11.1 se explicam — e o resultado é pior do que qualquer um deles:

- **1,6** = 1,0 (básico) + 0,6 (OODC). É o teto **sem** Transferência do Direito de Construir.
- **2,4** = 1,6 + 0,8 (TDC). Só se alcança **comprando potencial construtivo transferido**.
- **2,22** = o que o projeto usa.

> **[Crítico] O projeto está 0,62 acima do teto sem TDC.** Para chegar a 2,22 é preciso TDC —
> instrumento que **não aparece em nenhum documento do empreendimento**, nem na Análise PDM,
> nem no parecer, nem no EP. TDC é aquisição onerosa de potencial de terceiros: tem custo,
> tem mercado e tem processo próprio.
>
> Note ainda a nota **(A2) = 0**: o TDC neste zoneamento dá **+0,8 de CA mas zero pavimento
> adicional**. Ou seja, o TDC não é caminho alternativo para o 3º pavimento — só o incentivo
> de Uso Misto é. O que reforça o impasse da §12.1.

**Ação:** exigir do arquiteto o quadro de CA fechado com a origem de cada décimo, e do
financeiro o custo do TDC — que hoje não está em nenhuma planilha.

---

## 12.3 O topográfico NÃO existe *(corrige a §2 e o parecer de 01/07)*

Varredura de `02 - Projetos/03 - Levantamento Topográfico`:

```
03 - Levantamento Topográfico/
  01 - Documentação Técnica e Legal (ART/TRT)/   (vazia)
  02 - Memorial Descritivo/  → 00 - OLD/         (vazia)
  03 - Planta Topográfica (PDF/DWG/KML/KMZ)/ → 00 - OLD/   (vazia)
  04 - Relatório Fotográfico/                    (vazia)
  05 - NF e Boleto/                              (vazia)
```

**Não há um único arquivo.** A estrutura é o template de pastas da Seazone, não conteúdo.

> **Correção.** O parecer de 01/07 registra: *"✅ Levantamento Topográfico — pasta 03 completa
> (7 subpastas: Planta, Memorial Descritivo, Relatório Técnico, Dominialidade, Imagens)"* — e a
> §2 desta reauditoria, confiando nele, classificou como "documento disponível e não lido".
> **Ambos estão errados.** O documento não existe. Contar subpastas vazias como documento
> entregue é o modo de falha mais perigoso da DD: gera um ✅ onde não há nada.

Mesma situação em:

| Pasta | Conteúdo real |
|---|---|
| `04 - Estudo Ambiental` (inclui a subpasta EVA) | **vazia** (só `00 - OLD`, também vazia) |
| `05 - Sondagem` (inclui Relatório de Sondagem) | **vazia** |
| `07 - DD Técnica` | **vazia** |

> **R1 não é "não executada por falta de leitura" — é inexecutável.** A área física do terreno
> **nunca foi medida**. As seis áreas em circulação (450,00 · 450,00 · 452,27 · 452,26 ·
> 449,839 · 445,00) são todas de fonte cadastral, cartorial ou de estudo — nenhuma é
> levantamento de campo.
>
> E isso não é opcional: a seção 8 da Consulta PMF é explícita —
> *"Os dados do imóvel – como endereço, área e dimensões do terreno – (...) deverão estar de
> acordo com a realidade encontrada no local, com o Cadastro Imobiliário Municipal e com o
> título de propriedade. Se houver divergência, o requerente deverá providenciar as
> correções/atualizações necessárias junto ao Cadastro Municipal e/ou ao Cartório de Registro
> de Imóveis **previamente ao pedido de aprovação de projeto e/ou licenciamento da obra**."*
>
> Como a matrícula diz 450,00 e a Consulta Ambiental diz 452,27 — **duas fontes da própria
> PMF, do mesmo dia, discordando entre si** — a correção prévia é obrigatória, e o topográfico
> é o que a resolve.

---

## 12.4 Confirmações e números oficiais

| Item | Valor oficial (Consulta 028428/2026 e 17823068371826/2026) |
|---|---|
| Zoneamento | **ATR-2.5 — 100% do lote** |
| Uso apart-hotel | **Adequado ao zoneamento** ✅ |
| Área do lote conforme cadastro | **450,00 m²** (Consulta de Construção) |
| Área do imóvel territorial | **452,27 m²** (Consulta Ambiental) — **as duas consultas divergem** |
| Inscrição imobiliária | 60.89.029.0105.001 |
| Leis de referência | LC 482/2014, alterada pela LC 739/2023 |
| Loteamento | Novo Campeche, projeto aprovado nº 41389; via denominada pela Lei 4893/1996 |
| Taxa de impermeabilização máx. | **70%** → área permeável mín. **30%** (confirma a PDM) |
| Altura máx. fachada / cumeeira | **10,5 m / 13 m** |
| PGV (Decreto 25.888/2023) | Residencial R$ 1.401,42/m² · **Não residencial R$ 1.121,14/m²** |
| Fórmula da OODC | **Lei nº 755/2023** |
| APP proibitiva / UC no imóvel | **nenhuma** ✅ |
| Condicionante 1 | **área susceptível a inundação/alagamento** (baixa cota altimétrica) |
| Condicionante 2 | **entorno de Unidade de Conservação** — consulta ao órgão gestor obrigatória |
| Edificação existente | 204,30 m², ano 1999, ocupação "Construído" |
| Validade da Consulta Ambiental | **90 dias** a partir de 24/06/2026 → vence ~**22/09/2026** |

Sobre recuos, a Consulta remete ao **Art. 78-E** (via local de loteamento aprovado) e aos
Art. 73/73-A (frontal) e 74 a 78 (laterais e fundos) — coerente com o que a Análise PDM
extraiu. **O risco de borda de 32 cm no degrau de 9,50 m (§11.1) permanece de pé**, agora com
o teto de fachada oficial confirmado em 10,5 m.

---

## 12.5 Quatro exigências novas que ninguém tinha mapeado

### a) Subsolo no Campeche exige estudo aprovado pela FLORAM 🟡

> *"A construção de subsolos está condicionada à aprovação de estudo específico para execução
> de subsolos nos bairros Santa Mônica, **Campeche**, Ingleses (...) O estudo deve ser
> analisado e aprovado pela Floram conforme a IN-FLORAM 04/2022."*

O Campeche é **nominalmente citado**. Se o projeto prevê subsolo — e num lote de 450 m² com
TO alta, subsolo é a saída natural para área técnica —, há uma etapa de licenciamento
adicional, com prazo e custo, em terreno **de lençol raso e inundável**. Não consta de
nenhum documento do empreendimento.

### b) Licenciamento declaratório provavelmente está vedado 🟡

> *"São EXCLUÍDOS do licenciamento declaratório os imóveis que possuem restrição ambiental,
> salvo sob anuência do órgão ambiental competente, conforme Art. 7° da LC 707/2021."*

O imóvel tem duas condicionantes ambientais (inundação e entorno de UC). Isso empurra o
processo para o **regime regular**, que é mais lento. O cronograma de aprovação embutido no
modelo do negócio precisa refletir isso.

### c) EIV — Estudo de Impacto de Vizinhança, não verificado 🟡

A Consulta remete à **Lei 11.029/2023** e ao **Decreto 25.400/2023** para verificar
obrigatoriedade. Nada no empreendimento indica que essa verificação foi feita.

**Precedente direto:** o Novo Campeche Spot I **tem pasta própria de EIV**
(`02 - Projetos/01 - Processo de Aprovação/05 - Estudo de Impacto de Vizinhança`) e o
Relatório Final de Projetos daquele empreendimento lista, entre as pendências,
*"Contratar laudo de estudo de vizinhança"*. Mesmo bairro, mesmo produto, mesma área de
terreno — a probabilidade de o III também precisar é alta.

### d) Vala de drenagem 🟡

> *"Havendo vala de drenagem no imóvel ou em suas proximidades, a Secretaria Municipal de
> Infraestrutura deverá ser consultada quanto aos afastamentos exigidos."*

Em lote de baixa cota altimétrica declarado inundável, é hipótese provável — e afeta
implantação, não só custo. Sem topográfico, não dá para saber.

---

## 12.6 Precedente: Novo Campeche Spot I (emp 7094) — o gêmeo

| | Novo Campeche I | Novo Campeche III |
|---|---|---|
| Endereço | R. Ana Luiza Vieira, 38 — Campeche | R. Gilmar Darli Vieira, 106 — Campeche |
| Área | **450,00 m²** | 450,00 m² |
| Matrícula | 42.585 — 2º RI | 42.480 — 2º RI |
| Situação | executado / entregue | em DD |

Do **Relatório Final de Projetos** do NC I (entrega para obra) e da estrutura de
`01 - Processo de Aprovação`, o que aquele empreendimento efetivamente enfrentou:

| O que aconteceu no NC I | O que isso diz sobre o III |
|---|---|
| *"verificar se o imóvel está inserido em área susceptível a inundações/alagamentos em função da baixa cota altimétrica, **mas conta com sistema de drenagem pluvial**"* | **Mesma condição, e foi contornável.** É o melhor precedente contra o alarme de F-04 — mas o III precisa comprovar a mesma drenagem |
| *"(LAP, LAI e LAO) com RAP"* | **Licenciamento ambiental trifásico com Relatório Ambiental Prévio foi exigido.** O III presume dispensa e não previu prazo nem custo disso |
| *"Taxa de Ocupação máxima com incentivos de **Sustentabilidade e Arte Pública**"* | **Os mesmos dois incentivos do III já foram usados e aprovados no mesmo bairro** — o caminho tem precedente. Resolve a dúvida da §11.1 sobre arte pública ser viável (a diretriz de "evitar" é preferência do time, não impedimento legal) |
| **AuC de 20 exemplares arbóreos** (4 nativos, 16 exóticos) | Supressão vegetal foi necessária e onerosa; o III não tem levantamento arbóreo |
| Pasta **`08 - Retificação de área`** com `Relatorio_Divergencia_Area_NCS.docx` | **O NC I teve divergência de área e precisou retificar.** Precedente forte para o R1 do III |
| Pasta **`07 - Alvará de demolição`**: protocolo PMF E 00037232-2026 em **11/02/2026**, taxas pagas em **16/03** (R$ 348,29 + R$ 534,76), processo ainda correndo em **17/04** | **Prazo real de demolição: 2+ meses só de trâmite**, taxas de ~R$ 883. O III estimou R$ 40–80 mil de obra mas não previu esse prazo no cronograma |
| Checklist final: *"Sondagem e **laudo de percolação**"* | **Laudo de percolação indica solução de esgoto por infiltração**, não rede coletora. Se no Campeche a CASAN não atende, o III precisa de sumidouro dimensionado — e isso é área de terreno consumida |
| Pasta `02 - Aprovação projeto Hidrossanitário` | Etapa formal de aprovação que o III não mapeou |

A própria Consulta PMF fecha o ponto do esgoto: o licenciamento está condicionado a
*"sistema de coleta de esgoto **coletivo ou autônomo**"* (Decreto 1966/2003, Art. 34 do Plano
Diretor, Decreto 13.574/2014). **N-02 deixa de ser hipótese: é requisito formal de
licenciamento**, e o precedente do vizinho sugere solução autônoma.

---

## 12.7 Conclusão consolidada

**🔴 NO GO.** Não por excesso de risco ambiental ou jurídico — esses são administráveis — mas
porque **o potencial construtivo que forma o preço não está demonstrado**.

Os três pilares do produto (49 unidades, 3 pavimentos, TO de 68%) apoiam-se em:

1. um **incentivo de Uso Misto** que, pela nota (OODC) da própria Consulta PMF, **exclui** o
   TO×1,3 usado para chegar aos 65% (§12.1);
2. um **CA de 2,22** que excede em 0,62 o teto de 1,6 disponível sem **TDC** — instrumento que
   nunca foi mencionado, orçado ou adquirido (§12.2);
3. uma **área de terreno nunca medida em campo**, com duas consultas da própria PMF divergindo
   entre si (450,00 × 452,27) e a prefeitura exigindo a correção **antes** do protocolo (§12.3).

E há uma **proposta de R$ 5 milhões** cuja trava de preço venceu em 18/06 e que não tem
assinatura dos vendedores (§11.2).

### Ordem de prioridade

| # | Ação | Responsável | Por quê |
|---|---|---|---|
| 1 | **Levar a questão Uso Misto × TO×1,3 ao arquiteto e, se necessário, à SMDU** (pedido de Reconsideração da Consulta, canal previsto no próprio documento) | Arquiteto + Terrenos | Define se o produto é viável como está |
| 2 | **Contratar levantamento topográfico** | Engenharia | Destrava R1, os recuos, a TP e o protocolo |
| 3 | **Esclarecer a origem do CA de 2,22** — TDC comprado? incentivos? | Arquiteto | Define potencial e custo |
| 4 | **Localizar a proposta assinada pelos vendedores** e repactuar prazos | Jurídico + Investimentos | O preço não está travado |
| 5 | **Contratar sondagem SPT + laudo de percolação** | Engenharia | Área inundável + provável esgoto autônomo |
| 6 | **Consultar CASAN e verificar a bacia frente à ACP** | Engenharia | Requisito formal de licenciamento |
| 7 | **Verificar obrigatoriedade de EIV** (Lei 11.029/2023) | Arquiteto | Precedente no NC I |
| 8 | **Renovar as 3 certidões e confirmar a averbação da hipoteca** | Jurídico | F-01 e F-02, já mapeados |
| 9 | Consultar o órgão gestor da UC; verificar vala de drenagem; verificar necessidade de estudo de subsolo (IN-FLORAM 04/2022) | Engenharia | Condicionantes com prazo |

**O que muda o veredito:** resolvido o item 1 com resposta favorável — e confirmados 2 e 3 —
o caso migra para **GO COM RESSALVAS**, com as condicionantes 4 a 9 como plano de ação.
Se a resposta ao item 1 for desfavorável, o EP precisa ser redesenhado e **o preço de
R$ 5 milhões precisa ser reavaliado**, porque foi formado sobre um potencial que não existe.
