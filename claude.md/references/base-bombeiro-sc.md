# Base de Regras — Corpo de Bombeiros Militar SC (CBMSC)

> Versão: v1.1 | Última atualização: 2026-06-26 | Responsável: Rachel Souto
> Normas de referência: Decreto Estadual SC nº 741/2013 (Regulamento de Segurança
> contra Incêndio e Pânico do Estado de SC) + Instruções Normativas CBMSC.
> ⚠️ Verificar sempre o site oficial: cbmsc.sc.gov.br/sci/instrucoes-normativas
> ⚠️ v1.1: Corrigidos grupos de ocupação, numeração de INs e threshold de detecção
>    (verificação online 2026-06-26 via buscas em documentoscbmsc.cbm.sc.gov.br)

---

## 1. Classificação da edificação (Decreto 741/2013 — Tabela 1)

### Por uso/ocupação (Grupo e Divisão)

> ⚠️ **CORREÇÃO v1.1**: O CBMSC NÃO usa A-4. O grupo residencial tem apenas A-1, A-2, A-3.
> ⚠️ **CORREÇÃO v1.1**: Grupo H no CBMSC = **Saúde** (hospitais). Hospedagem = **Grupo B**.

| Grupo | Divisão | Uso | Exemplos SZI |
|---|---|---|---|
| A | A-1 | Residencial unifamiliar | Casa térrea, condomínio horizontal |
| A | **A-2** | **Residencial multifamiliar** | **Apartamentos, condomínio vertical — caso típico SZI** |
| A | A-3 | Habitação coletiva (máx. 16 leitos) | Pensionato, alojamento |
| B | B-1 | Serviços de hospedagem — hotel e assemelhados (sem cozinha própria) | Hotel, pousada, albergue |
| B | **B-2** | **Hotel residencial (com cozinha própria)** | **Apart-hotel, flat, Spot (uso transitório)** |
| H | H-1 a H-6 | **Saúde** — hospitais, asilos, clínicas | Não aplicável SZI |

> Para apart-hotel / Spot (uso transitório): enquadra em **B-2** pelo CBMSC, não em Grupo A.
> Confirmar classificação com CBMSC antes de protocolar o preventivo — B-2 pode ter
> exigências adicionais em relação a A-2.

### Por altura (h = distância do piso do último pavimento habitável ao nível da rua)

| Faixa | Altura |
|---|---|
| Baixa | h ≤ 6 m |
| Média | 6 m < h ≤ 12 m |
| **Alta** | **12 m < h ≤ 23 m** |
| **Muito Alta** | **h > 23 m** |
| Grande altura | h > 60 m |

> Jurerê Spot III (PL Rev.01 abr/2026): h = **18,66 m** (cota do Pav. Cobertura no corte) → **Alta**.
> (O EP V00 de 2025 mencionava 24,5m usando convenção diferente; o projeto atual é 18,66m.)

### Regra prática: classificar SEMPRE ANTES de checar os sistemas
Grupo A-4 + Muito Alta = conjunto de exigências mais elevado. Se houver dúvida entre
faixas, adotar a mais restritiva (postura conservadora).

---

## 2. Sistemas de proteção exigidos por classificação

Tabela simplificada para **Grupo A (residencial multifamiliar)** — caso típico SZI.
Para outros grupos (H-1 apart-hotel), verificar tabela completa do Decreto.

| Sistema | Média (≤12m) | Alta (12–23m) | Muito Alta (>23m) | Régua Seazone |
|---|:---:|:---:|:---:|---|
| Saídas de emergência | ✅ | ✅ | ✅ | 🔴 Crítico |
| Extintores | ✅ | ✅ | ✅ | 🔴 Crítico |
| Iluminação de emergência | ✅ | ✅ | ✅ | 🔴 Crítico |
| Porta corta-fogo (PCF) | ✅ | ✅ | ✅ | 🔴 Crítico |
| Hidrante interno (mangotinho) | — | ✅ | ✅ | 🔴 Crítico |
| Hidrante externo | — | ✅ | ✅ | 🟡 Atenção |
| Detecção e alarme | — | ✅ | ✅ | 🔴 Crítico |
| Sinalização de emergência | ✅ | ✅ | ✅ | 🔴 Crítico |
| Escada enclausurada (EEE) | — | ✅ | ❌ (ver EP) | 🔴 Crítico |
| Escada pressurizada (EP) | — | — | ✅ | 🔴 Crítico |
| Controle de fumaça | — | — | ✅ | 🔴 Crítico |
| Plano de emergência / brigada | — | 🟡 | ✅ | 🟡 Atenção |
| Spkler / chuveiros automáticos | — | — | 🟡 (>30 pav.) | ✅ Preciosismo |

> ✅ = Exigido | — = Não exigido para este grupo/faixa | 🟡 = Verificar caso a caso

---

## 3. Regras por sistema (o que checar no projeto)

### 3.1 Escada de emergência (IN-009/CBMSC)

| Critério | Regra | Referência |
|---|---|---|
| Tipo de escada por altura | h ≤ 12m: EN (natural) ou EEE; 12m < h ≤ 23m: **EEE**; h > 23m: **EP** | Decreto 741/2013 + IN-009 |
| Largura mínima da escada | 1,20 m (A-2 multifamiliar); 1,50 m se > 200 pessoas | IN-009, tabela de larguras |
| Desnível máximo sem patamar | 3,20 m | IN-009 |
| Descarga da escada | Para o exterior (fora da projeção da edificação) ou para rota protegida | IN-009 |
| Porta corta-fogo (PCF) | Exigida em cada andar na escada enclausurada; resistência mínima: P-90 | IN-009 |
| EEE: abertura de exaustão | Área livre mínima: 1,20 m² no topo; 1,00 m² em cada andar | IN-009 |
| EP: pressurização | Diferencial de pressão mínimo: 25 Pa (porta aberta) / 50 Pa (fechada); conforme NBR 14880 | IN-009/CBMSC + NBR 14880 |

**O que checar no projeto**: (a) o tipo de escada bate com a altura real; (b) largura
indicada; (c) PCF em todos os andares; (d) se EEE: abertura de exaustão visível na
planta de cobertura; (e) se EP: nota de pressurização no memorial.

### 3.2 Saídas de emergência (IN-009/CBMSC)

| Critério | Regra |
|---|---|
| Nº mínimo de saídas | 1 escada se área/pavto ≤ 750 m² e ≤ 200 pessoas; senão 2 |
| Distância máxima de percurso até a saída | 30 m com chuveiros automáticos; 20 m sem |
| Largura mínima dos corredores de saída | 1,20 m |
| Descarga final | Diretamente para o exterior (sem cruzar outra área de risco) |
| Portas de saída | Abertura no sentido do escape; proibido tranca que impeça saída |

**O que checar**: (a) percurso de cada unidade até a escada ≤ 20m (sem sprinkler);
(b) largura dos corredores; (c) sentido de abertura das portas de saída no projeto.

> ⚠️ Não existe IN-011 identificada no CBMSC. Saídas de emergência (escadas incluídas) = **IN-009**.

### 3.3 Hidrante e mangotinho (IN-005/CBMSC)

| Critério | Regra |
|---|---|
| Quando exigir hidrante interno (mangotinho) | A partir de 3 pavimentos ou área total > 750 m² |
| Raio de cobertura por ponto | 30 m (mangueira de 25 m + jato de 5 m) |
| Reserva Técnica de Incêndio (RTI) | Mínimo 8 m³ (residencial multifamiliar) — verificar tabela |
| Localização dos abrigos | Em cada pavimento, próximo à escada; visível e sinalizado |
| Acesso à coluna seca (hidrante externo) | Fachada; identificado e desimpedido |

**O que checar**: (a) abrigos de hidrante indicados em planta em cada andar;
(b) cobertura de 30 m verificada (trace um raio na planta); (c) RTI no projeto
hidrossanitário ou reservatório identificado; (d) coluna seca na fachada.

### 3.4 Extintores (IN-006/CBMSC)

| Critério | Regra |
|---|---|
| Tipo mínimo | ABC (pó) para áreas comuns e garagem |
| Distância máxima até extintor | 15 m (Classe A — sólidos) |
| Locais obrigatórios | Garagem, hall de cada andar, casa de máquinas, área de lixo |
| Sinalização | Sinalética CBMSC visível |

**O que checar**: (a) extintores indicados em planta em todas as áreas obrigatórias;
(b) distância entre extintores ≤ 15 m.

### 3.5 Iluminação de emergência (IN a confirmar)

| Critério | Regra |
|---|---|
| Lumens mínimos na rota de saída | 3 lux no piso (escada e corredores de saída) |
| Autonomia mínima | 1 hora (residencial) |
| Pontos obrigatórios | Escada, corredores de saída, hall, garagem, casa de máquinas |
| Sinalização de saída | "SAÍDA" iluminada em cada porta de saída |

**O que checar**: (a) pontos de iluminação de emergência indicados em planta elétrica ou
planta de incêndio; (b) autonomia indicada no memorial.

> ⚠️ IN-009 no CBMSC = **Saídas de Emergência** (escadas), NÃO iluminação.
> A IN específica de iluminação de emergência não foi identificada nas buscas. A verificar.

### 3.6 Detecção e alarme (IN-012/CBMSC)

> ⚠️ **CORREÇÃO v1.1**: a IN correta é **IN-012** (não IN-013). IN-013 não existe como referência CBMSC identificada.
> ⚠️ **CORREÇÃO v1.1**: threshold de **detecção automática** para A-2 parece ser **h ≥ 40 m**,
>    NÃO h > 12m. A partir de 12m, apenas acionadores manuais (alarme) podem ser exigidos.
>    **A CONFIRMAR diretamente com CBMSC ou na leitura da IN-012 + IN-1 Parte 2.**

| Critério | Regra (a confirmar com IN-012) | Status |
|---|---|---|
| Acionadores manuais de alarme | A partir de h > 12 m — um a cada 30 m de corredor, nas escadas | ⚠️ A confirmar |
| Detecção automática (detectores) | A partir de h ≥ 40 m (A-2): corredores comuns + 1 ponto por unidade | ⚠️ A confirmar |
| Detecção automática (h ≥ 100 m) | Dentro das unidades (cozinha + quartos) | ⚠️ A confirmar |
| Central de alarme | Local de fácil acesso, identificado no projeto | ⚠️ A confirmar |

**O que checar**: (a) acionadores manuais próximos às escadas (se h > 12m);
(b) detectores automáticos em corredores comuns (se h ≥ 40m);
(c) central de alarme localizada no projeto.

> Se confirmado h ≥ 40m para detecção: Jurerê Spot III (h=18,66m) → **acionadores manuais apenas**.
> Impacto: item B13 do Relatório de Conformidade v00 precisa ser revisado.

### 3.7 Sinalização de emergência (IN-010/CBMSC)

Exigida em todos os grupos. Inclui: saídas, extintores, hidrantes, escadas, rotas.
**O que checar**: planta de sinalização ou legenda no projeto preventivo.

---

## 4. Protocolo de incêndio (CBMSC) — documentos para o alvará

Para obter o **protocolo preventivo de incêndio** (exigido pela PMF para o alvará):
1. Projeto de incêndio assinado por responsável técnico (ART/RRT).
2. Planta baixa de cada pavimento + corte + implantação.
3. Memorial descritivo dos sistemas.
4. ART/RRT do projetista.

> O protocolo preventivo é feito no site do CBMSC (cbmsc.sc.gov.br/sistema-ppi).
> Atualmente: sistema PPrev. Verificar se houve mudança de plataforma.

---

## 5. Régua Seazone por item (gestão define — revisar a cada piloto)

| Item | Régua atual | Justificativa |
|---|---|---|
| Tipo de escada correto (EEE vs EP) | 🔴 Crítico | Bloqueante para aprovação preventiva CBMSC |
| PCF em todos os andares da escada | 🔴 Crítico | Exigência de protocolo |
| Hidrante interno em cada andar | 🔴 Crítico | Obrigatório; exigido em vistoria |
| Extintores indicados em planta | 🔴 Crítico | Exigido em protocolo |
| Iluminação de emergência | 🔴 Crítico | Exigido em protocolo |
| Detecção automática (h ≥ 40m A-2) | 🔴 Crítico | Obrigatório — threshold a confirmar com IN-012 |
| Acionadores manuais de alarme (h > 12m) | 🔴 Crítico | Obrigatório — a confirmar com IN-012 |
| RTI dimensionada | 🟡 Atenção | Pode ser calculada em projeto hidrossanitário separado |
| Hidrante externo (coluna seca) | 🟡 Atenção | Exigido mas frequentemente corrigido em comunique |
| Plano de emergência / brigada | 🟡 Atenção | Mais relevante na fase de uso; pode ser pós-aprovação |
| Sprinkler | ✅ Preciosismo | Não exigido para A-2 ≤ 30 pavimentos em SC |

> ⚠️ Esta régua é a posição inicial — validar no piloto (Jurerê Spot III ou próxima entrega).

---

## 6. Histórico de atualizações da base

| Data | Versão | O que mudou | Impacto em projetos em andamento |
|---|---|---|---|
| 2026-06-25 | v1.0 | Criação da base com Decreto 741/2013 e IN-CBMSC | — |
| 2026-06-26 | v1.1 | Correção grupos ocupação (A-4 → A-2; H-1 hospedagem → B-2); correção INs (escadas: IN-009; detecção: IN-012); threshold detecção automática (h > 12m → h ≥ 40m A CONFIRMAR); iluminação IN pendente. Via busca online em documentoscbmsc.cbm.sc.gov.br. | Rever item B13 do Relatório Jurerê Spot III v00; rever classificação A-2 vs B-2 no relatório |

> Próxima verificação programada: 2026-09-25 (90 dias)
> Responsável pelo abastecimento: [a definir — ver plano de ação]
