# Playbook da DD Técnica — SZI Lançamentos

Referência canônica de **quais documentos** compõem a DD Técnica, **o que extrair**
de cada um e **quais cruzamentos** rodar. Baseado no parecer real do Jurerê Spot III.

> A DD Técnica responde: **é viável prosseguir com o terreno/empreendimento?**

---

## 1. Documentos da DD (checklist de completude)

| # | Etapa | Documento | Órgão/Origem | Obrigatório |
|---|-------|-----------|--------------|:-----------:|
| 1 | Imóvel | Certidão de inteiro teor da **matrícula** (ônus e ações) | Cartório de Registro de Imóveis | Sim |
| 2 | Imóvel | **Certidão cadastral** (espelho IPTU) | Prefeitura (PMF) | Sim |
| 3 | Imóvel | **Certidão de confrontantes** | Prefeitura (PMF) | Sim (Floripa) |
| 4 | Imóvel | **Viabilidade Técnica Construtiva** (documento do site da prefeitura — traz **zoneamento** e **exigências legais**) | Prefeitura (PMF) | Sim |
| 5 | Estudo | **Levantamento topográfico** (georreferenciado) | Topógrafo | Sim |
| 6 | Estudo | **Estudo de Viabilidade Ambiental (EVA)** | Consultoria ambiental | Sim |
| 7 | Estudo | **Sondagem** (SPT) | Empresa de sondagem | Sim |
| 8 | Estudo | **Estrutura** (quantitativo preliminar + tabela de carga) | Eng. estrutural | Sim |
| 9 | Estudo | **Fundação** (premissas) | Eng. de fundação | Sim |
| 10 | Validação | **Validação do Estudo Preliminar pelo arquiteto** (relatório no EP Lançamentos) | Arquiteto responsável | Sim |
| 11 | Instalações | **Documentação de instalações** (quando existe) | — | Quando aplicável |
| 12 | Marinha | **Documentação SPU** (só se terreno de marinha) | SPU | Condicional |
| 13 | Imagens | **Imagens de localização/drone/panorâmica** (entorno, contexto, vistas) | Pasta 09 - Imagens de Drone | Desejável |
| 14 | Negócio | **Proposta de compra e venda** (valores/condições do negócio) | 05 - Jurídico/01 - Terreno/02 - Proposta | Sim |

**Localização real no Drive (caso Jurerê III):** documentos de estudo ficam em
`<Empreendimento>/02 - Projetos/<NN - subpasta>`; **matrículas/certidões** em
`05 - Jurídico/01 - Terreno/00 - Documentos e certidões.../Imóvel 1|2`; **proposta** em
`05 - Jurídico/01 - Terreno/02 - Proposta de compra e venda`; **imagens** em
`02 - Projetos/09 - Imagens de Drone`. Sempre a **última versão em PDF**; ignorar `OLD`/`Demais arquivos`.

Quando há **mais de uma matrícula/imóvel** (caso Jurerê III: imóveis 01 e 02),
extrair e somar áreas por imóvel e avaliar **amembramento**.

> **A DD Jurídica NÃO faz parte desta DD Técnica** — é uma consulta separada e não entra
> neste ritual nem nas saídas.

---

## 2. Campos a extrair por documento

- **Matrícula**: nº da matrícula, cartório, inscrição imobiliária, endereço,
  **área registrada**, proprietário(s) (nome/CNPJ/CPF), ônus e ações.
- **Certidão cadastral (IPTU)**: inscrição, **área cadastral PMF**, uso, proprietário cadastrado.
- **Certidão de confrontantes**: confrontantes por lado, **área indicada**.
- **Viabilidade Técnica Construtiva** (documento do site da prefeitura — **fonte primária do
  zoneamento e das exigências legais**): **zoneamento** em que o terreno está inserido,
  **parâmetros urbanísticos** (TO máx, CA máx, TP/impermeabilização, recuos, altura/gabarito),
  **usos permitidos** e **exigências legais** apontadas pela prefeitura.
- **Levantamento topográfico**: **área real georreferenciada**, cotas/declividade, confrontações.
- **EVA (ambiental)**: **APP** (sim/não + restrição), **terreno de marinha** (sim/não +
  afastamento), **UC** (sim/não), supressão vegetal (nº de árvores, AuC/compensação),
  infraestrutura (água/esgoto/energia/drenagem), condicionantes (ex.: ACP de esgoto),
  licenciamento exigido, **nº de unidades** considerado, % de área útil. *(O zoneamento e os
  parâmetros urbanísticos vêm da Viabilidade Construtiva; o EVA pode citá-los, mas a fonte
  oficial é a Viabilidade.)*
- **Documentação SPU** (só marinha): cadastro/RIP, certidão SPU, autorização/aforamento/ocupação
  e demais documentos exigidos para terreno de marinha.
- **Sondagem (SPT)**: nº de furos, profundidades, NA (nível d'água), perfil de camadas,
  **tipo de fundação recomendado** (rasa/profunda + tipos de estaca).
- **Estrutura**: nº de pavimentos, altura, **nº de unidades**, sistema estrutural, cargas.
- **Fundação**: solução adotada, coerência com a sondagem.
- **Validação do arquiteto (EP)**: conformidade com TO/CA/recuo/TP, ajustes exigidos no
  anteprojeto (ex.: escada EEE/Bombeiros, NBR-9050, recuos), lista de documentos para
  aprovação e alvará.

---

## 3. Regras de cruzamento (a auditoria)

> Cada regra gera um achado: **severidade** (🔴/🟡/🟢) + descrição + **fonte** + ação.

### R1 — Consistência de área 🔴
Comparar: área_matrícula (soma) × área_cadastro_PMF × área_confrontantes × área_topográfica.
- Calcular `dif% = |área_topográfica − área_matrícula| / área_matrícula * 100`.
- Se **dif% > 3%** ⇒ **exigir retificação de matrícula** (severidade 🔴).
- Se houver >1 matrícula ⇒ avaliar **amembramento**.
- Qualquer divergência entre as quatro fontes ⇒ listar todas as áreas lado a lado.

### R2 — Nº de unidades coerente 🟡
EVA × Estrutura × Estudo Preliminar devem citar o **mesmo nº de unidades**.
Divergência ⇒ apontar (ex.: Jurerê III: EVA 68 × Estrutura 69).

### R3 — Gabarito / parâmetros urbanísticos 🔴
Comparar parâmetros do **estudo/anteprojeto** com o **zoneamento e exigências legais da
Viabilidade Técnica Construtiva** (e com o Plano Diretor do zoneamento):
- **TO** (taxa de ocupação) ≤ máx?
- **CA** (coeficiente de aproveitamento) ≤ máx?
- **TP** (taxa de permeabilidade) / impermeabilização dentro do limite?
- **Recuo obrigatório** atendido? (frontal/lateral/fundos)
- **Altura/gabarito** (nº pavimentos) ≤ máx? (ex.: Jurerê III — PD ~4 pav. × estrutura T+6)
Não atende ⇒ 🔴 + indicar readequação no anteprojeto.

### R4 — Ambiental 🔴/🟡
- **APP**: se há APP ⇒ marcar área não edificável + % útil; conferir se o estudo respeita.
- **Terreno de marinha**: se sim ⇒ (a) exigir **afastamento** no ambiental E no topográfico;
  (b) **conferir a documentação da SPU** (Secretaria do Patrimônio da União) — cadastro/RIP,
  certidão SPU, autorização/aforamento/ocupação e demais documentos exigidos. Marinha sem
  documentação SPU ⇒ 🔴 Pendente.
- **UC**: se em Unidade de Conservação ⇒ 🔴.
- **Supressão vegetal**: nº de árvores, exigência de **AuC** + compensação (FLORAM em Floripa).
- **Esgoto/condicionantes**: ex.: ACP de esgoto ⇒ exigir declaração CASAN/Município.
- **Demolição**: construções existentes ⇒ alvará de demolição.

### R5 — Geotécnico (sondagem → fundação → custo) 🟡
- Tipo de fundação recomendado pela sondagem deve **bater** com o doc de fundação/estrutura.
- Fundação profunda (estaca raiz/hélice/pré-moldada) ⇒ sinalizar **impacto de custo/prazo**.
- NA raso / argila mole ⇒ atenção a custo e vizinhança (vibração).

### R6 — Completude 🟡
Qualquer documento obrigatório ausente/ilegível ⇒ **Pendente** (nunca presumir conteúdo).
Em terreno de marinha, a documentação **SPU** entra como obrigatória.

---

### R7 — Bombeiro / Segurança contra Incêndio 🔴/🟡

> **Escopo na DD**: não é análise de conformidade completa (isso é o Consultor Técnico).
> O objetivo é identificar **riscos de custo, prazo ou bloqueio** que afetam a decisão de compra.
> Referência de regras detalhadas: `claude.md/references/base-bombeiro-sc.md` (CBMSC v1.1).

#### R7.1 — Classificação de altura e impacto de custo

Extrair a **altura do projeto** (h = piso do último pavimento habitável → nível da rua) da
validação do arquiteto ou do corte estrutural. Cruzar com a tabela CBMSC:

| Faixa CBMSC | Tipo de escada | Impacto custo |
|---|---|---|
| h ≤ 12 m (Baixa/Média) | Escada natural (sem enclausuramento especial) | Baixo |
| 12 m < h ≤ 23 m (Alta) | **EEE** (enclausurada com exaustão) | Moderado |
| h > 23 m (Muito Alta) | **EP** (escada pressurizada) | **Alto** — shaft adicional, equipamento, manutenção |

- Se h está **próximo de 23 m** (ex.: 20–25 m): 🟡 **Zona de risco** — pequena variação no projeto
  pode mudar EEE → EP e encarecer significativamente. Sinalizar para revisão do anteprojeto.
- Se h > 23 m confirmado: 🔴 **EP obrigatória** — exige memorial específico e projeto de pressurização.

#### R7.2 — Checagem na Validação do Arquiteto (EP)

A validação do EP pelo arquiteto frequentemente já aponta problemas de bombeiro.
Buscar explicitamente no documento:

| O que procurar | Severidade se encontrado |
|---|---|
| Tipo de escada indicado (EEE ou EP) e se bate com a altura real | 🔴 se divergente |
| Porta da EEE/EP: sentido de abertura, dimensões (PCF) | 🔴 se não atende IN-009 |
| Acesso de viaturas: testada ≥ 6 m? Via de acesso desimpedida? | 🔴 se bloqueado |
| Distância máxima de percurso até escada (≤ 20 m sem sprinkler) | 🟡 se > 20 m |
| Menção a sistema de sprinkler (chuveiros automáticos) obrigatório | 🟡 se exigido |
| Área de refúgio ou resgate aéreo (h > 50 m) | 🟡 se se aproximar do limite |

#### R7.3 — Classificação de ocupação (A-2 vs B-2)

Para empreendimentos com uso **transitório ou hoteleiro** (apart-hotel, Spot, flat):
- Grupo **A-2** (Residencial Multifamiliar) → exigências padrão
- Grupo **B-2** (Hotel Residencial) → pode ter exigências adicionais de brigada e alarme
- **Confirmar com CBMSC** antes de protocolar o preventivo de incêndio se houver dúvida.

> ⚠️ Grupo H no CBMSC = **Saúde** (hospitais/clínicas) — não confundir com hospedagem.

#### O que registrar no parecer

- Grupo CBMSC presumido (A-2 ou B-2) + faixa de altura
- Tipo de escada exigido (EEE ou EP)
- Problemas identificados na Validação do Arquiteto sobre bombeiro
- Recomendação: se EP ou classificação B-2 forem necessários → incluir como **custo adicional**
  no impacto de negócio (seção 4)

---

## 4. Conclusão de negócio (além do técnico)
- **Impacto custo/prazo**: consolidar itens onerosos (fundação profunda, retificação,
  amembramento, supressão, demolição, sistema de esgoto, licenciamento).
- **Red flags priorizados**: lista ordenada do que mais ameaça viabilidade/prazo.
- **Aproveitamento × VGV**: área útil → unidades → potencial de receita (estimado).
- **Recomendação**: **GO** / **GO com ressalvas** / **NO-GO**, com as condicionantes.
