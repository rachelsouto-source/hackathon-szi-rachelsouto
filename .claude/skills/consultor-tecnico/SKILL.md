---
name: consultor-tecnico
description: >-
  Skill unificado SZI Lançamentos — cobre DD Técnica (auditoria única na compra
  do terreno) e Consultor Técnico (verificação contínua por entrega arquitetônica).
  USE para: "auditar DD técnica do [X]", "due diligence do terreno [X]",
  "parecer de viabilidade do terreno [X]", "checar [disciplina] [empreendimento]",
  "conferir bombeiro / NBR / SST do [X]", "abastecer [disciplina]",
  "auditar entregas do [X]", "confirmar se algo quebrou nos comuniques".
---

# Consultor Técnico & Auditor de DD Técnica — SZI Lançamentos

> **Skill unificado.** Dois momentos da jornada, uma forma de raciocinar.
>
> — **DD Técnica** (Modo A): auditoria única na compra do terreno — responde "é viável?"
> — **Consultor Técnico** (Modo B–D): verificação contínua por entrega arquitetônica — responde "está em conformidade?"

---

## Modos de uso

| Invocação | Modo | Quando usar |
|---|---|---|
| `auditar DD técnica do [X]` / `due diligence do [X]` | **A — DD Técnica** | Compra do terreno — única vez |
| `checar [disciplina] [empreendimento]` | **B — Checador** | A cada entrega arquitetônica (AP, AE, PL, PD) |
| `abastecer [disciplina]` | **C — Abastecedor** | Mensal ou quando houver alerta de norma nova |
| `auditar entregas do [X]` / `conferir comuniques` | **D — Auditor de Trilha** | Antes de protocolar; após cada rodada de comuniques |

---

## Disciplinas disponíveis (Modos B–D)

| Código | Disciplina | Base de regras | Status |
|---|---|---|---|
| `bombeiro` | Corpo de Bombeiros Militar SC (CBMSC) | `claude.md/references/base-bombeiro-sc.md` | ✅ Ativo |
| `nbr` | ABNT — NBR 9050 (acessibilidade) + NBR 15575 (desempenho) | `claude.md/references/base-nbr.md` | ✅ Ativo |
| `sst` | Segurança e Saúde no Trabalho (NRs MTPS) | `claude.md/references/base-sst.md` | 🔜 Stub |

---

## 0. Navegar o Drive — padrão para todos os modos

O Drive da SZI usa a mesma estrutura de pastas para todos os empreendimentos:

```
<Pasta do empreendimento>/          ← pasta raiz (ID fornecido ou buscado por nome)
  (raiz)/                           ← arquivos soltos na raiz
  01 - Orçamentos/
  02 - Projetos/
    01 - Estudos/
    02 - Estudo Preliminar/
    03 - Projeto Legal/
    09 - Imagens de Drone/
    ...
  03 - Financeiro/
  05 - Jurídico/
    01 - Terreno/
      00 - Documentos e certidões.../
        Imóvel 1/  Imóvel 2/        ← matrículas, IPTU, confrontantes
      02 - Proposta de compra e venda/
  07 - Lançamento/
  09 - Valorização/
  ...
```

**Regras de navegação:**
1. Use o MCP de Google Drive (`get_file_permissions`, `COMPOSIO_SEARCH_TOOLS`, `COMPOSIO_MULTI_EXECUTE_TOOL`) para listar filhos de uma pasta.
2. **Profundidade padrão**: listar 2 níveis (área → arquivos). Para DD Técnica (matrículas, certidões), descer 3–4 níveis conforme necessário pelos caminhos conhecidos acima.
3. **Ignorar**: pastas e arquivos com prefixo `OLD`, `old`, `BACKUP`, e o Doc `DIÁRIO — ` (gerado automaticamente).
4. **Última versão**: sempre usar o PDF mais recente; ignorar versões antigas dentro de uma pasta.
5. **Fonte rastreável**: para cada documento lido, registrar `nome do arquivo | subpasta | link do Drive`.

**Busca por nome do empreendimento:**
- Pasta mãe dos empreendimentos estruturados: nome começa com código numérico `[NNNN]` + nome do spot.
- Exemplo: `1.25 - [3352] Marista 144 Spot` — o `[ID]` é o código do empreendimento na NEKT.
- Se o ID for desconhecido, buscar pelo nome do spot na pasta mãe.

---

## A. MODO DD TÉCNICA

> Auditoria única na compra do terreno. Responde: **"é viável prosseguir?"**

### A.1 — Documentos a localizar

Usar o playbook completo: `claude.md/references/dd-tecnica-playbook.md`.

| # | Documento | Onde no Drive |
|---|---|---|
| 1 | Matrícula (inteiro teor) | `05 - Jurídico/01 - Terreno/00 - Documentos e certidões.../Imóvel 1\|2` |
| 2 | Certidão cadastral (IPTU) | Mesma pasta |
| 3 | Certidão de confrontantes | Mesma pasta |
| 4 | Viabilidade Técnica Construtiva (PMF) | `02 - Projetos/03 - Projeto Legal/` ou `02 - Projetos/01 - Estudos/` |
| 5 | Levantamento topográfico | `02 - Projetos/` |
| 6 | EVA (ambiental) | `02 - Projetos/` |
| 7 | Sondagem (SPT) | `02 - Projetos/` |
| 8 | Estrutura (quantitativo) | `02 - Projetos/` |
| 9 | Fundação (premissas) | `02 - Projetos/` |
| 10 | Validação do Estudo Preliminar (arquiteto) | `02 - Projetos/02 - Estudo Preliminar/` |
| 11 | Documentação SPU (só marinha) | `05 - Jurídico/01 - Terreno/` |
| 12 | Proposta de compra e venda | `05 - Jurídico/01 - Terreno/02 - Proposta de compra e venda/` |
| 13 | Imagens de drone/localização | `02 - Projetos/09 - Imagens de Drone/` |

Montar o **mapa de completude** antes de começar os cruzamentos. Documento ausente = ⬜ Pendente — nunca presumir conteúdo.

### A.2 — Cruzamentos (regras de auditoria)

Aplicar as regras R1–R7 do playbook `dd-tecnica-playbook.md`:

| Regra | O que verifica |
|---|---|
| R1 | Consistência de área: matrícula × IPTU × confrontantes × topográfico. dif% > 3% → 🔴 retificar |
| R2 | Nº de unidades coerente: EVA × Estrutura × Estudo Preliminar |
| R3 | Parâmetros urbanísticos (TO, CA, TP, recuos, gabarito) do projeto × Viabilidade Construtiva |
| R4 | Ambiental: APP, marinha (+ documentação SPU), UC, supressão vegetal, condicionantes de esgoto |
| R5 | Geotécnico: tipo de fundação da sondagem coerente com estrutura; impacto custo/prazo |
| R6 | Completude: documentos obrigatórios ausentes = Pendente |
| R7 | Bombeiro: faixa de altura → tipo de escada (EEE vs EP); problemas na validação do arquiteto |

Bombeiro resumido para DD: usar `claude.md/references/base-bombeiro-dd-resumo.md`.

### A.3 — Entregáveis da DD Técnica

1. **Parecer Técnico** → template `claude.md/templates/parecer-tecnico.md`
2. **Planilha de controle** → template `claude.md/templates/checklist-controle.csv`
3. **Resumo GO / NO-GO** com impacto custo/prazo, red flags priorizados e recomendação

---

## B. MODO CHECADOR

> Verificação de conformidade a cada entrega arquitetônica.

### B.1 — Inputs necessários

- **Disciplina** (`bombeiro`, `nbr`, `sst`)
- **Documentos do projeto** (PDF ou link Drive): planta baixa, cortes, implantação, memorial descritivo, projeto específico da disciplina
- **Histórico de comuniques** — comuniques anteriores com data e status de cada item
- **Data da entrega** — para versionar a legislação vigente

### B.2 — Fluxo de execução

1. **Carregar a base** — leia `claude.md/references/base-[disciplina].md`. Verificar data de atualização: se > 90 dias, alertar para rodar o Abastecedor primeiro.
2. **Extrair dados do projeto**:
   - Altura total (h = piso do último pavimento habitável → nível da rua) e nº de pavimentos
   - Área total construída (m²), uso/ocupação (A-2, B-2, misto, etc.)
   - Quantidade de unidades e vagas de garagem
   - Sistemas já projetados (tipo de escada, hidrante, extintores, etc.)
3. **Classificar a edificação** → grupo/divisão de uso + faixa de altura → sistemas exigidos.
4. **Checar cada item da base**:
   - 🟢 **Atende** — evidência clara nos documentos
   - 🔴 **Não atende** — obrigatório ausente ou em desacordo
   - 🟡 **Atenção** — atende parcialmente ou requer vistoria
   - ⬜ **Pendente** — documento ausente ou ilegível
   - ➖ **Não se aplica** — com justificativa
5. **Verificar regressões** — para cada item "atendido" em comunique anterior, conferir se a entrega atual MANTÉM. Se quebrou: 🔴 **REGRESSÃO** (severidade máxima). Indicar: _"Comunique [X] item [Y], atendido em [data], está em risco nesta versão."_
6. **Gerar o relatório** → template `claude.md/templates/relatorio-conformidade.md`
7. **Listar decisões de gestão** — pontos que dependem da régua Seazone (Rachel decide mínimo obrigatório vs. atenção)

---

## C. MODO ABASTECEDOR

> Atualiza a base de regras de uma disciplina. Rodar mensalmente ou quando houver alerta de norma nova.

### C.1 — Fluxo de execução

1. Verificar data de última atualização em `claude.md/references/base-[disciplina].md`.
2. Buscar atualizações:
   - **Bombeiro**: cbmsc.sc.gov.br/sci/instrucoes-normativas (novas IN ou revisões)
   - **NBR**: normas.abnt.org.br (novas edições ou erratas)
   - **PMF**: novas exigências para aprovação de projetos em Florianópolis
3. Comparar com a base vigente: nova regra / revisão / revogação.
4. Atualizar `claude.md/references/base-[disciplina].md`: itens modificados + Histórico de atualizações + incrementar versão.
5. Gerar relatório → template `claude.md/templates/relatorio-abastecimento.md`
6. Alertar dependências: se afeta parâmetros urbanísticos → alertar Projeto B (calculadora/funil).

---

## D. MODO AUDITOR DE TRILHA

> Verifica se o processo rodou corretamente e se nenhum ponto aprovado foi quebrado.

### D.1 — Fluxo de execução

1. **Mapa de entregas** — listar versões do projeto (AP, AE, PL, PD) e confirmar se o Checador rodou em cada uma.
2. Para cada versão checar: Checador rodou? Base estava atualizada? Houve REGRESSÃO?
3. **Mapa de comuniques** — status de atendimento por item e por versão.
4. **Indicadores de reincidência** — itens exigidos >1x = candidatos a entrar na base de regras.
5. Gerar relatório → template `claude.md/templates/trilha-auditoria.md`

---

## 1. FORMA DE RACIOCINAR — 7 perguntas por achado

> **Obrigatório em todos os modos.** Cada achado relevante (🔴, 🟡, ou qualquer item que impacte decisão) deve ser apresentado respondendo as 7 perguntas abaixo. Isso garante rastreabilidade, contexto e acionabilidade.

Para cada achado, estruturar assim:

```
### [Severidade] [Código] — [Título curto]

1. **O que foi encontrado?**
   Descrição factual do achado — o que está presente, ausente ou em desacordo.

2. **Como foi identificado?**
   Método de identificação: "lendo o corte longitudinal (pág. X)", "cruzando área da matrícula com topográfico", "comparando com IN-009 art. 5.2", etc.

3. **Qual documento comprova?**
   Nome do arquivo + link + página/seção relevante. Rastreabilidade obrigatória.

4. **Existe precedente?**
   Já apareceu em comunique anterior? Estava atendido? Se sim, é REGRESSÃO (🔴 máxima).
   Se é achado novo: indicar.

5. **Qual o risco?**
   O que pode acontecer se ignorado: reprovação no CBMSC, vistoria negativa, atraso de alvará, custo não previsto, etc.

6. **Qual o impacto?**
   Custo estimado (se possível), prazo adicional, documentos bloqueados, decisões de negócio afetadas.

7. **Qual a mitigação?**
   Ação recomendada: quem faz, o quê, em que prazo. Indicar se é decisão técnica ou de gestão (régua Seazone).
```

---

## 2. MATRIZ DE RISCO

> Consolidar ao final de cada análise (Modos A, B e D). Uma linha por achado ativo (🔴 e 🟡).

| Código | Achado | Probabilidade | Impacto | Criticidade | Mitigação | Responsável | Documento de referência |
|---|---|---|---|---|---|---|---|
| R-01 | [título] | Alta/Média/Baixa | Alto/Médio/Baixo | 🔴/🟡 | [ação] | [quem] | [norma/artigo] |

**Criticidade** = combinação de Probabilidade × Impacto:
- 🔴 Alta probabilidade + alto impacto
- 🟡 Qualquer combinação intermediária
- 🟢 Baixa probabilidade + baixo impacto

---

## 3. ENTREGÁVEIS (7 itens)

Cada análise completa deve produzir:

| # | Entregável | Modo | Template |
|---|---|---|---|
| E1 | **Resumo GO / GO com ressalvas / NO-GO** | A, B | — (inline) |
| E2 | **Parecer Técnico** com achados detalhados (Forma de Raciocinar) | A, B, D | `parecer-tecnico.md` / `relatorio-conformidade.md` |
| E3 | **Comparativo de versões** (quando há mais de uma entrega) | B, D | `trilha-auditoria.md` |
| E4 | **Matriz de Risco** consolidada | A, B, D | inline na análise |
| E5 | **Checklist de conformidade** por item/disciplina | A, B | `checklist-controle.csv` |
| E6 | **Recomendações de gestão** (decisões que dependem da régua Seazone) | A, B | — (seção dedicada) |
| E7 | **Lessons Learned** | A, B, D | inline ao final |

---

## 4. APRENDIZADO CONTÍNUO (Lessons Learned)

> Ao final de **toda** análise, gerar uma seção de Lessons Learned com no mínimo 3 itens.

Estrutura:

```
## Lessons Learned — [Empreendimento] [Disciplina] [Data]

| # | Aprendizado | Origem | Ação sugerida |
|---|---|---|---|
| LL-01 | [o que foi aprendido] | [qual achado gerou] | [adicionar à base? alertar outro processo?] |
```

**Filtros para Lessons Learned:**
- Itens exigidos >1x em comuniques → candidatos a entrar na base como item obrigatório
- Achados com impacto alto que não estavam na base → propor adição ao Abastecedor
- Padrões de erro recorrentes no projeto → sinalizar para o time de Projetos/arquitetura
- Pontos de ambiguidade de norma que exigiram interpretação → documentar para consistência futura

---

## 5. PRINCÍPIOS

- **Fonte obrigatória**: todo dado citado tem nome de arquivo + link. Sem fonte = Pendente.
- **Nunca inventar**: documento ausente = ⬜ Pendente. Jamais presumir conteúdo.
- **REGRESSÃO acima de tudo**: quebrar um ponto já aprovado tem severidade máxima (🔴 incondicional).
- **A pessoa valida**: a saída é um rascunho técnico de alta qualidade. Rachel (ou arquiteto responsável) faz a revisão final.
- **Régua Seazone**: a skill aponta. Rachel define o mínimo técnico obrigatório vs. atenção vs. preciosismo.
- **NEKT é a fonte de dados de projeto**: não usar Lake ou planilhas desatualizadas.
- **Parametrizável por município**: a legislação muda fora de Floripa — ver `claude.md/references/legislacao-municipios.md`.

---

## 6. INTEGRAÇÃO COM OUTROS PROCESSOS

- **Projeto B (calculadora/funil)**: Abastecedor notifica quando norma impacta parâmetros de viabilidade.
- **NEKT**: fonte primária para dados de projetos (unidades, área, fase, cronograma).
- **Google Drive**: documentos em `02 - Projetos/` (projeto) e `05 - Jurídico/` (documentos de terreno).
- **Bombeiro resumo para DD**: `claude.md/references/base-bombeiro-dd-resumo.md` (flags de custo, não compliance detalhada).

---

## 7. CASO-BASE VALIDADO

**Jurerê Spot III** — Florianópolis/SC.
- Relatório de conformidade: `claude.md/exemplos/jurere-iii-relatorio-conformidade-v00.md`
- Dados: h = 18,66 m (Alta), A-2 presumido (B-2 possível), 69 unidades, 0 vagas, área ~2.890 m²
- Achados ativos: EEE (porta sentido de abertura incorreto), unidades acessíveis não identificadas
