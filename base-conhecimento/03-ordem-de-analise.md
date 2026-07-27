# 03 — Ordem obrigatória da análise

**Sempre seguir esta sequência.** Cada bloco é lido já sabendo o que os anteriores
disseram; a coluna "cruzar com" indica o confronto obrigatório no momento da leitura.

| # | Bloco | Cruzar com |
|---|---|---|
| 1 | [Matrícula](#1-matrícula) | — (é a referência registral) |
| 2 | [Espelho cadastral](#2-espelho-cadastral) | Matrícula |
| 3 | [Levantamento topográfico](#3-levantamento-topográfico) | Matrícula, espelho cadastral |
| 4 | [Sondagem](#4-sondagem) | Topográfico |
| 5 | [Estudo de Massa / EVA](#5-estudo-de-massa--eva) | Viabilidade construtiva (posterior), EP |
| 6 | [Validação do Estudo Preliminar](#6-validação-do-estudo-preliminar) | Estudo de massa / EVA |
| 7 | [Viabilidade construtiva](#7-viabilidade-construtiva) | EP, estudo de massa, espelho cadastral |
| 8 | [Estrutural](#8-estrutural) | EP, sondagem |
| 9 | [Fundação](#9-fundação) | Sondagem, estrutural |
| 10 | [SPU / terreno de marinha](#10-spu--terreno-de-marinha) | Matrícula, topográfico, EVA |
| 11 | [Documentação ambiental](#11-documentação-ambiental) | Topográfico, EVA, viabilidade |
| 12 | [Proposta](#12-proposta) | Matrícula, topográfico, viabilidade, EP |

Documento não encontrado → registrar como **pendência** ([R6](04-regras-de-auditoria.md#r6--completude-documental)),
nunca presumir conteúdo.

---

## 1. Matrícula

Certidão de inteiro teor, com ônus e ações. Fonte registral primária.

Extrair:

- **área** registrada
- **confrontantes**
- **proprietário** (nome / CPF / CNPJ)
- **averbações**
- **servidões**
- **restrições**
- **desmembramentos**
- **unificações**
- **ônus** (hipoteca, penhora, alienação fiduciária, usufruto)
- **observações importantes** (ações reais e pessoais reipersecutórias, indisponibilidade)

Se houver **mais de uma matrícula/imóvel**: extrair e somar as áreas por imóvel e avaliar
a necessidade de **unificação/amembramento** antes da incorporação.

---

## 2. Espelho cadastral

Certidão cadastral da prefeitura (espelho de IPTU). Validar:

- **inscrição imobiliária**
- **área** cadastral
- **zoneamento** cadastrado
- **uso permitido**
- **endereço**

**Comparar com a matrícula** — área, endereço e proprietário. Divergência de proprietário
entre cadastro e registro é achado (cadastro desatualizado é comum, mas precisa ser dito).

---

## 3. Levantamento topográfico

Levantamento georreferenciado. Extrair:

- **área levantada**
- **curvas de nível** (e declividade resultante)
- **APP** demarcada
- **cursos d'água**
- **árvores** (indivíduos arbóreos levantados)
- **confrontações**
- **cotas**
- **norte**
- **sistema de coordenadas**

**Comparar com a matrícula** — área e confrontações. Esta comparação dispara a
[R1](04-regras-de-auditoria.md#r1--consistência-de-áreas).

Ausência de norte ou de sistema de coordenadas declarado torna o levantamento
inutilizável para aprovação — registrar como pendência.

---

## 4. Sondagem

Sondagem à percussão (SPT). Validar:

- **tipo de solo** (perfil de camadas por furo)
- **nível d'água** (NA) e a data da leitura
- **NSPT** por camada (e o impenetrável, se atingido)
- **necessidade de fundações especiais**
- **risco geotécnico** (solo mole, aterro, matacão, rocha aflorante)

Conferir se o número e a distribuição dos furos cobrem a área de implantação.

---

## 5. Estudo de Massa / EVA

Extrair:

- **número de unidades**
- **áreas** (terreno, projeção, construída total, computável, privativa)
- **vagas**
- **altura**
- **pavimentos**
- **implantação**

**Comparar posteriormente com o EP** ([bloco 6](#6-validação-do-estudo-preliminar)) e com a
viabilidade construtiva ([bloco 7](#7-viabilidade-construtiva)).

---

## 6. Validação do Estudo Preliminar

Comparar (EP × estudo de massa / EVA):

- **quantidade de unidades**
- **áreas**
- **circulação**
- **implantação**
- **fachadas**
- **produto**

Divergência de unidades dispara a [R2](04-regras-de-auditoria.md#r2--quantidade-de-unidades).
A validação do EP pelo arquiteto costuma **já apontar** problemas de recuo, acessibilidade
e bombeiros — ler esse documento buscando explicitamente essas menções.

---

## 7. Viabilidade construtiva

Documento emitido pela prefeitura — **fonte oficial do zoneamento e das exigências legais**.
Extrair:

- **zoneamento**
- **TO** (taxa de ocupação)
- **CA** (coeficiente de aproveitamento — básico e máximo)
- **TP** (taxa de permeabilidade)
- **Gabarito** (altura / nº de pavimentos)
- **Recuos** (frontal, laterais, fundos)
- **Incentivos** urbanísticos
- **Outorga** onerosa
- **Fruição** pública
- **Operações Urbanas**
- **APP**
- **restrições** e exigências legais apontadas pelo órgão

Confrontar tudo com o EP e o estudo de massa — dispara a
[R3](04-regras-de-auditoria.md#r3--parâmetros-urbanísticos).

Quando o empreendimento estiver em Florianópolis, aplicar automaticamente
[09 — Florianópolis](09-florianopolis.md).

---

## 8. Estrutural

Validar:

- **conceito estrutural** (sistema adotado)
- **pilares** (posicionamento e seções)
- **modulação**
- **interferências** (com vagas, circulação, fachada, instalações)

Conferir nº de pavimentos, altura e nº de unidades contra o EP — o estrutural é uma
terceira fonte para a [R2](04-regras-de-auditoria.md#r2--quantidade-de-unidades).

---

## 9. Fundação

**Validar compatibilidade com a sondagem**: a solução proposta (rasa, estaca hélice,
raiz, pré-moldada, tubulão) precisa ser coerente com o perfil, o NSPT e o NA levantados
no [bloco 4](#4-sondagem).

Fundação profunda, contenção ou rebaixamento de lençol → impacto de **custo e prazo** a
ser consolidado na seção de negócio do parecer.

---

## 10. SPU / terreno de marinha

Executar **quando houver indício de terreno de marinha** (matrícula, topográfico, EVA,
localização costeira ou LPM demarcada). Validar:

- **RIP** (Registro Imobiliário Patrimonial)
- **ocupação**
- **aforamento**
- **necessidade de autorização** da SPU

Terreno de marinha **sem documentação SPU** é pendência de severidade alta — bloqueia
aprovação e pode alterar o valor do negócio (laudêmio, foro, taxa de ocupação).

---

## 11. Documentação ambiental

Validar:

- **APP** (existência, faixa, área não edificável resultante)
- **UC** (unidade de conservação e sua zona de amortecimento)
- **vegetação** (estágio sucessional, bioma)
- **supressão** (nº de indivíduos, autorização exigida, compensação)
- **cursos d'água**
- **mangue**
- **restinga**
- **licenciamento** (modalidade exigida, órgão competente, condicionantes)

Dispara a [R4](04-regras-de-auditoria.md#r4--riscos-ambientais).

---

## 12. Proposta

Proposta de compra e venda. Comparar:

- **área considerada** na proposta × área da matrícula × área topográfica
- **produto vendido** × produto do EP
- **potencial construtivo** assumido × potencial real da viabilidade construtiva

Proposta ancorada em área ou em potencial construtivo que a documentação não sustenta é
achado **crítico** — afeta diretamente o preço pago.
