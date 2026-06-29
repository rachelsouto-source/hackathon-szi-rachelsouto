# Relatório de Conformidade Técnica — Jurerê Spot III

> Gerado pelo Consultor Técnico (skill `consultor-tecnico`) — disciplinas Bombeiro CBMSC + NBR.
> Documentos analisados: EP Rev.00 (28/08/2025, AF Arquitetura) + PL Rev.01 (01/04/2026, AF Arquitetura).
> Base: base-bombeiro-sc **v1.1** (atualizada 2026-06-26 com correção de grupos e INs).
> **Requer revisão humana antes de qualquer uso oficial.**

---

## Cabeçalho

| Campo | Valor |
|---|---|
| **Empreendimento** | Jurerê Spot III — Rua Accácio Melo, 64 e 76, Jurerê, Florianópolis/SC |
| **SPE** | JURERE SPOT III SPE LTDA — CNPJ 62.354.414/0001-76 |
| **Arquiteto responsável** | André Fornari — CAU/SC A64518-4 |
| **Disciplinas checadas** | Bombeiro CBMSC + NBR 9050 (acessibilidade) + NBR 15575 (desempenho) |
| **Versão do projeto analisada** | PL Rev.01 (01/04/2026) — versão mais recente disponível |
| **Legislação vigente** | base-bombeiro-sc **v1.1** (2026-06-26) · base-nbr v1.0 (2026-06-25) |
| **Comunique(s) anteriores** | Nenhum registrado — primeiro ciclo de verificação |
| **Gerado em** | 2026-06-25 |

---

## Classificação da edificação

| Item | Valor | Fonte |
|---|---|---|
| Uso / Ocupação declarado | USO MISTO (Residencial Multifamiliar Transitório + Comercial) | Quadro de Áreas, PL Rev.01 |
| Grupo CBMSC (presumido) | **A-2** (Residencial Multifamiliar) — CBMSC não usa A-4 | base-bombeiro-sc v1.1 |
| ⚠️ Grupo CBMSC (a confirmar) | **Pode ser B-2** (Hotel Residencial / flat) — uso "transitório" indica apart-hotel. No CBMSC, Grupo H = **Saúde** (hospitais), não hospedagem. | base-bombeiro-sc v1.1 |
| Altura do último pavimento habitável (h) | **18,66 m** (Pav. Cobertura/Penthouse — cota 1866 no corte) | Corte A e B, PL Rev.01 |
| Altura total da estrutura | 28,43 m (inclui barrilete e reservatório, não habitáveis) | Corte A, PL Rev.01 |
| Faixa de altura CBMSC | **Alta (12 m < h ≤ 23 m)** | base-bombeiro-sc v1.0 |
| Nº de pavimentos habitáveis | 7 (Térreo/Lofts + PI + 2º + 3º + 4º + 5º + Cobertura) | Quadro de Áreas, PL Rev.01 |
| Área construída total | 2.161,52 m² | Quadro de Áreas, PL Rev.01 |
| Nº de unidades | 69 unidades (10 loft + 15 + 13×3 tipo + 5 cobertura) | Quadro de Áreas, PL Rev.01 |
| Vagas de carro | 0 vagas residenciais + 1 embarque/desembarque | Quadro de Áreas, PL Rev.01 |
| Vagas de bicicleta | 5 | Quadro de Áreas, PL Rev.01 |

> ⚠️ **ALERTA DE CLASSIFICAÇÃO (atualizado v1.1)**: O CBMSC NÃO possui A-4. O grupo residencial multifamiliar é **A-2**. Para uso "transitório" (apart-hotel / Spot), o CBMSC usa **Grupo B-2** (Hotel Residencial / flat com cozinha própria) — **não Grupo H** (que no CBMSC = Saúde/hospitais). Confirmar com o CBMSC se o projeto é A-2 ou B-2 antes de protocolar o preventivo.

---

## Resumo executivo

| Status | Contagem | Nota |
|---|---|---|
| 🟢 Atende | 5 itens | |
| 🔴 Não atende | 2 itens | Porta EEE sentido errado · unidades acessíveis não indicadas |
| 🟡 Atenção | 5 itens | +1 vs v0: detecção automática provavelmente não exigida em h=18,66m (A-2) |
| ⬜ Pendente (doc ausente) | 7 itens | -1 vs v0: B13 detecção reclassificado |
| ➖ Não se aplica | 1 item | Vagas PcD (sem garagem) |

**Recomendação geral**: ⚠️ **Corrigir antes do protocolo** — 2 itens críticos não atendidos identificados diretamente no projeto disponível; 8 itens pendentes aguardam documentação complementar (projeto de incêndio, elétrico, hidrossanitário).

---

## DISCIPLINA 1 — BOMBEIRO CBMSC

### 1.1 Escada de emergência (IN-012/CBMSC)

| # | Item | Regra | Evidência no projeto | Status | Severidade |
|---|---|---|---|---|---|
| B1 | **Tipo de escada** | h = 18,66m (Alta) → **EEE exigida** (12m < h ≤ 23m) | Projeto indica EEE. Tipo CORRETO para esta altura. | 🟢 Atende | 🔴 Crítico |
| B2 | **Sentido de abertura da porta da EEE** | Porta deve abrir no sentido da rota de fuga; raio livre 1,25m (IN-9/CBMSC) | EP Rev.00 (sec. 10.7): "a porta abre em sentido oposto" — não corrigido na versão PL Rev.01 disponível | 🔴 Não atende | 🔴 Crítico |
| B3 | **Porta Corta-Fogo (PCF)** | P-90 (resistência 90 min) na escada enclausurada | PL Rev.01 Det. 02: PCF-90x210 indicado na entrada da escada (térreo) e PCF-100x210 nos pavimentos tipo | 🟢 Atende | 🔴 Crítico |
| B4 | **Duto de exaustão (EEE)** | Abertura livre ≥ 1,00 m² por andar; ≥ 1,20 m² no topo (IN-012) | PL Rev.01 Det. 02: Duto ø150 indicado. Dimensão de 15cm de diâmetro é INSUFICIENTE para abertura livre de 1,0 m² — este duto é provavelmente de esgoto/pluvial, não a abertura da EEE | 🟡 Atenção | 🔴 Crítico |
| B5 | **Largura mínima da escada** | ≥ 1,20 m (A-4 multifamiliar) | PL Rev.01: escada visível nas plantas baixas, mas largura não cotada explicitamente no detalhamento disponível | ⬜ Pendente | 🔴 Crítico |
| B6 | **Descarga da escada** | Para o exterior ou rota protegida (sem cruzar área de risco) | PL Rev.01: escada deságua no térreo próximo à entrada — verificar se descarga é direta para o exterior | ⬜ Pendente | 🔴 Crítico |

### 1.2 Saídas de emergência (IN-011/CBMSC)

| # | Item | Regra | Evidência no projeto | Status | Severidade |
|---|---|---|---|---|---|
| B7 | **Nº de saídas** | 1 escada se área/pav ≤ 750 m² e ≤ 200 pessoas | Área por pavimento tipo: 295 m² → 1 escada suficiente | 🟢 Atende | 🔴 Crítico |
| B8 | **Distância máxima de percurso** | ≤ 20 m (sem sprinkler) até a escada | Plantas baixas (2º ao 5º pav.): unidades mais distantes da escada estimadas em ~15–18 m — necessita medição exata | 🟡 Atenção | 🔴 Crítico |
| B9 | **Largura dos corredores** | ≥ 1,20 m | Plantas tipo: corredores cotados como 1,30 m no 2º pav. (Imagem 28, EP) | 🟢 Atende | 🔴 Crítico |

### 1.3 Sistemas de proteção ativa (hidrante, extintores, detecção)

| # | Item | Regra | Evidência no projeto | Status | Severidade |
|---|---|---|---|---|---|
| B10 | **Hidrante interno** | Obrigatório: 3+ pav. ou > 750 m² — raio 30 m por ponto | Projeto arquitetônico não inclui planta de incêndio | ⬜ Pendente | 🔴 Crítico |
| B11 | **Extintores** | ABC em todas as áreas comuns, garagem, casa de máquinas | Projeto arquitetônico não inclui planta de incêndio | ⬜ Pendente | 🔴 Crítico |
| B12 | **Iluminação de emergência** | Em escada, corredores, hall, garagem; autonomia ≥ 1h | Projeto elétrico não disponível | ⬜ Pendente | 🔴 Crítico |
| B13 | **Detecção e alarme** | ⚠️ THRESHOLD A CONFIRMAR: para A-2, detecção automática parece ser exigida a partir de h ≥ 40 m (não h > 12m). Para h > 12m, acionadores manuais de alarme provavelmente são exigidos. h=18,66m → possivelmente **apenas alarme manual**. Confirmar via IN-012 + IN-1 Parte 2. | Projeto de incêndio não disponível | ⬜ Pendente (impacto revisado) | 🟡 Atenção |
| B14 | **RTI (Reserva Técnica de Incêndio)** | ≥ 8 m³ (residencial multifamiliar) — via reservatório ou cisterna | Reservatório indicado na cobertura (33,53 m²) — volume não especificado; projeto hidrossanitário pendente | ⬜ Pendente | 🟡 Atenção |
| B15 | **Sinalização de emergência** | Saídas, extintores, hidrantes, rotas | Projeto de incêndio/sinalização não disponível | ⬜ Pendente | 🔴 Crítico |

### 1.4 Alerta especial — Classificação H-1 (Hospedagem)

| # | Item | Situação | Status | Severidade |
|---|---|---|---|---|
| B16 | **Confirmação Grupo CBMSC (A-2 vs B-2)** | Uso "transitório" = apart-hotel → pode ser Grupo **B-2** (Hotel Residencial). B-2 pode ter exigências diferentes de A-2 (ex: sistemas de alarme com limiar diferente, brigada de incêndio). Grupo H no CBMSC = Saúde/hospitais — **não se aplica** a este projeto. Confirmar A-2 vs B-2 com CBMSC antes do protocolo preventivo. | 🟡 Atenção | 🔴 Crítico |

---

## DISCIPLINA 2 — NBR 9050:2020 (Acessibilidade)

### 2.1 Unidades habitacionais acessíveis

| # | Item | Regra | Evidência no projeto | Status | Severidade |
|---|---|---|---|---|---|
| N1 | **Cotas obrigatórias** | 5% acessíveis (min 1) + 10% visitáveis (min 1). Para 69 unidades: **4 acessíveis + 7 visitáveis** | Declaração de responsabilidade (PL Rev.01) inclui Decreto 9.269/2018 (5%) e NBR 9050. Projeto não indica explicitamente quais unidades são acessíveis/visitáveis nas plantas baixas disponíveis | 🟡 Atenção | 🔴 Crítico |

### 2.2 Rota acessível

| # | Item | Regra | Evidência no projeto | Status | Severidade |
|---|---|---|---|---|---|
| N2 | **Rampa de acesso principal** | Inclinação ≤ 8,33% (1:12); corrimão duplo 0,70m + 0,92m em ambos os lados; largura ≥ 1,20 m | EP Rev.00 (sec. 10.5): inclinação = 7,68% (< 8,33% ✅). Arquiteto aponta necessidade de corrimão duplo — não confirmado como incluído na versão PL Rev.01 | 🟡 Atenção | 🔴 Crítico |
| N3 | **Piso tátil (rota acessível)** | Piso tátil direcional/alerta desde calçada até hall e elevador | PL Rev.01 Det. 02: "PISO ALERTA" indicado apenas na área do elevador. Continuidade da rota desde a calçada não verificada | 🟡 Atenção | 🟡 Atenção |
| N4 | **Largura dos corredores** | ≥ 1,20 m livre | Plantas tipo: 1,30 m cotado no 2º pav. | 🟢 Atende | 🔴 Crítico |

### 2.3 Elevador

| # | Item | Regra | Evidência no projeto | Status | Severidade |
|---|---|---|---|---|---|
| N5 | **Obrigatoriedade** | Obrigatório: ≥ 4 pavimentos | Elevador indicado em todas as plantas. 7 níveis habitáveis. | 🟢 Atende | 🔴 Crítico |
| N6 | **Dimensão mínima da cabine** | ≥ 1,10 m × 1,40 m (profundidade) | PL Rev.01 Det. 02: cabine indicada no detalhamento, mas dimensões internas não cotadas explicitamente na planta de circulação vertical | ⬜ Pendente | 🔴 Crítico |

### 2.4 Vagas de garagem

| # | Item | Regra | Evidência no projeto | Status | Severidade |
|---|---|---|---|---|---|
| N7 | **Vagas PcD** | 5% das vagas (mín. 1), dimensão 2,50 × 5,00 m | 0 vagas de carro no projeto (somente 1 embarque/desembarque). Vagas de carro não existem → percentual sobre zero. | ➖ N/A | — |

### 2.5 Banheiros acessíveis

| # | Item | Regra | Evidência no projeto | Status | Severidade |
|---|---|---|---|---|---|
| N8 | **WC PcD em áreas comuns e comerciais** | Obrigatório em áreas de uso coletivo e comerciais | PL Rev.01 Det. 01: WC PCD detalhado para Loja 01, Loja 02, Loja 03 e área comum Cobertura | 🟢 Atende | 🔴 Crítico |

### 2.6 Corrimão de escadas e rampas

| # | Item | Regra | Evidência no projeto | Status | Severidade |
|---|---|---|---|---|---|
| N9 | **Duplo corrimão (0,70 m + 0,92 m)** | Ambas as alturas obrigatórias em escadas e rampas | PL Rev.01 Det. 02 (Corte Circulação Vertical): cotados 92 e 70 — **atende** | 🟢 Atende | 🔴 Crítico |

---

## DISCIPLINA 3 — NBR 15575:2013 (Desempenho)

| # | Item | Regra | Evidência no projeto | Status | Severidade |
|---|---|---|---|---|---|
| D1 | **TRRF da estrutura** | h = 18,66 m → TRRF ≥ **60 min** (NBR 15575-3 / NBR 14432) | Declaração de responsabilidade inclui NBR 15.575. Memorial estrutural e de desempenho não disponíveis para verificação | ⬜ Pendente | 🔴 Crítico |
| D2 | **Memorial de desempenho** | Memória técnica de vedações externas + cobertura exigida na PMF | Não disponível nos documentos analisados | ⬜ Pendente | 🟡 Atenção |

---

## Itens REGRESSÃO

Nenhum — este é o primeiro ciclo de verificação. Não há histórico de comuniques anteriores registrados.

---

## Pontos para decisão de gestão (régua Seazone)

| # | Item | Situação | Opções para Rachel |
|---|---|---|---|
| G1 | **Classificação CBMSC A-4 vs H-1** | Uso "transitório" pode mudar a classificação e exigências. Afeta todos os sistemas de proteção ativa. | (a) Confirmar A-4 com CBMSC antes de protocolar; (b) Aceitar risco e protocolar como A-4 |
| G2 | **Projeto de incêndio separado** | 8 itens permanecem ⬜ Pendente porque o projeto preventivo de incêndio não foi desenvolvido ainda. É documento obrigatório para o alvará. | (a) Contratar projetista de incêndio agora (recomendado antes do protocolo); (b) Desenvolver após aprovação arquitetônica |
| G3 | **Corrimão duplo na rampa** | Arquiteto identificou necessidade mas não confirmado como corrigido. Baixo custo de correção. | (a) Solicitar confirmação ao arquiteto na próxima revisão |

---

## Ações recomendadas (próximo ciclo de revisão)

| Prioridade | Ação | Responsável | Prazo |
|---|---|---|---|
| 🔴 Urgente | Corrigir orientação da porta da EEE (item B2) | Arquiteto (AF Arquitetura) | Antes do protocolo PMF |
| 🔴 Urgente | Verificar duto de exaustão da EEE: ø150 é insuficiente — confirmar se há abertura livre ≥ 1,0 m² por andar (item B4) | Arquiteto | Antes do protocolo CBMSC |
| 🔴 Urgente | Confirmar classificação CBMSC (A-4 vs H-1) diretamente com o Corpo de Bombeiros (item B16) | Rachel / Arquiteto | Antes do protocolo |
| 🔴 Urgente | Contratar e desenvolver projeto de incêndio (resolve itens B10–B15) | Projetista de incêndio | Antes do alvará |
| 🟡 Atenção | Indicar nas plantas quais das 69 unidades são acessíveis (4 acessíveis + 7 visitáveis) (item N1) | Arquiteto | Próxima revisão do projeto |
| 🟡 Atenção | Confirmar corrimão duplo (0,70 + 0,92m) incluído na rampa de acesso 7,68% (item N2) | Arquiteto | Próxima revisão |
| 🟡 Atenção | Cotar dimensão interna da cabine do elevador (≥ 1,10 × 1,40 m) no detalhamento (item N6) | Arquiteto | Próxima revisão |
| 🟡 Atenção | Apresentar memorial de desempenho NBR 15575 (TRRF ≥ 60 min) ao protocolar (item D1) | Arquiteto / Eng. Estrutural | Antes do protocolo PMF |

---

## Nota sobre documentos analisados vs. necessários

Os documentos disponíveis (EP Rev.00 + PL Rev.01) permitem verificar **o projeto arquitetônico**.
Os documentos abaixo NÃO estão disponíveis e geram os 8 itens ⬜ Pendente:

| Documento faltante | Itens que desbloqueiam |
|---|---|
| Projeto Preventivo de Incêndio (CBMSC) | B10, B11, B13, B15 (hidrante, extintores, detecção, sinalização) |
| Projeto de Instalações Elétricas | B12 (iluminação de emergência) |
| Projeto Hidrossanitário | B14 (RTI) |
| Memorial de Desempenho NBR 15575 | D1, D2 (TRRF, desempenho) |
| Detalhamento do elevador com cotas | N6 (dimensão da cabine) |

---

*Relatório gerado pelo Consultor Técnico (skill `consultor-tecnico`) — disciplinas Bombeiro CBMSC + NBR.*
*Base de regras: base-bombeiro-sc v1.0 + base-nbr v1.0 (2026-06-25).*
*Requer revisão humana e validação por profissional habilitado (engenheiro/arquiteto + especialista em incêndio) antes de qualquer uso oficial.*
