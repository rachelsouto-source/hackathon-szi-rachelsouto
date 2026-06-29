---
name: consultor-tecnico
description: >-
  Consultor Técnico de Disciplinas para projetos de lançamento da SZI.
  Verifica conformidade de entregas arquitetônicas contra normas técnicas (NBR,
  CBMSC/Bombeiro SC, Segurança do Trabalho) e contra o histórico de comuniques.
  Três papéis: CHECAR (entrega + base → relatório de conformidade), ABASTECER
  (busca atualizações e versiona a base), AUDITAR (verifica se o processo rodou
  e se nenhum ponto já atendido foi quebrado).
  USE quando precisar: "checar conformidade do [projeto] contra [disciplina]",
  "atualizar a base de [disciplina]", ou "auditar se o consultor técnico rodou
  no [projeto] / se algo aprovado no comunique X foi quebrado".
---

# Consultor Técnico — SZI Lançamentos

> Projeto D — Processos com IA (Seazone).
> Diferente da DD Técnica (auditoria única na compra do terreno), este consultor
> roda **a cada entrega arquitetônica**, em processo contínuo, disciplina por disciplina.

## O que esta skill faz

Automatiza a verificação técnica de disciplinas no projeto arquitetônico:
1. **Checador**: pega a base de regras da disciplina + os documentos do projeto + histórico
   de comuniques → devolve relatório de conformidade com itens atendidos/não atendidos.
2. **Abastecedor**: busca atualizações de legislação/normas da disciplina → atualiza a base
   → alerta o time (e o Projeto B — funil/calculadora) quando há mudança relevante.
3. **Auditor**: verifica se o Checador rodou em cada entrega, se a base está fresca, se
   algum ponto já atendido num comunique anterior foi quebrado na versão atual.

## Quando usar

| Invocação | Quando usar |
|---|---|
| `checar [disciplina] [empreendimento]` | A cada nova entrega arquitetônica (AP, AE, PL, PD) |
| `abastecer [disciplina]` | Periodicamente (sugestão: mensal) ou quando houver alerta de norma nova |
| `auditar [empreendimento]` | Antes de protocolar; após cada rodada de comuniques |

## Disciplinas disponíveis

| Código | Disciplina | Base de regras | Status |
|---|---|---|---|
| `bombeiro` | Corpo de Bombeiros Militar SC (CBMSC) | `claude.md/references/base-bombeiro-sc.md` | ✅ Ativo |
| `nbr` | Normas ABNT (foco NBR 9050 acessibilidade + NBR 15575 desempenho) | `claude.md/references/base-nbr.md` | ✅ Ativo |
| `sst` | Segurança e Saúde no Trabalho (NRs MTPS) | `claude.md/references/base-sst.md` | 🔜 Stub |

---

## PAPEL 1 — CHECADOR

### Inputs necessários
- **Disciplina** (ex: `bombeiro`)
- **Documentos do projeto** — forneça os PDFs ou links no Drive:
  - Planta baixa de cada pavimento (PDF)
  - Corte longitudinal e transversal
  - Implantação
  - Memorial descritivo (se houver)
  - Projeto específico da disciplina (ex: planta de incêndio, se já existir)
- **Histórico de comuniques** — liste os comuniques anteriores com data e status de cada item
- **Data da entrega** — para versionar a legislação vigente na data

### Fluxo de execução

1. **Carregar a base da disciplina** — leia `claude.md/references/base-[disciplina].md`
   para ter as regras vigentes e a data de última atualização.
2. **Extrair dados do projeto** — dos documentos fornecidos, extraia:
   - Altura total (m) e número de pavimentos
   - Área total construída (m²)
   - Uso/ocupação (residencial multifamiliar, apart-hotel, misto, etc.)
   - Quantidade de unidades e vagas de garagem
   - Sistemas já projetados (escada tipo, hidrante, extintores, etc.)
3. **Classificar a edificação** — use a tabela da base de regras para determinar:
   - Grupo/Divisão de uso e faixa de altura
   - Sistemas exigidos para esta classificação
4. **Checar cada item da base** — para cada regra, determine:
   - 🟢 **Atende** — evidência encontrada no projeto
   - 🔴 **Não atende** — item obrigatório ausente ou em desacordo
   - 🟡 **Atenção** — atende parcialmente ou requer verificação em vistoria
   - ⬜ **Pendente** — documento ausente ou ilegível (nunca presumir)
   - ➖ **Não se aplica** — justifique
5. **Checar o histórico de comuniques** — para cada item marcado como "atendido" em
   comuniques anteriores, verifique se a entrega atual MANTÉM o atendimento. Se quebrou:
   - Marcar como 🔴 **REGRESSÃO** — severidade máxima.
   - Indicar: "Comunique [X] item [Y], atendido em [data], está em risco nesta versão."
6. **Gerar o relatório** — use o template `claude.md/templates/relatorio-conformidade.md`.
7. **Listar decisões de gestão** — pontos que dependem da **régua Seazone**
   (mínimo vs. preciosismo) — a skill aponta, a gestão decide.

### Princípios
- **Fonte obrigatória**: cada item tem a norma/artigo de referência.
- **Nunca inventar**: documento ausente = Pendente.
- **REGRESSÃO acima de tudo**: quebrar um ponto já aprovado tem severidade máxima.

---

## PAPEL 2 — ABASTECEDOR

### Quando rodar
- Mensalmente ou quando houver alerta de revisão de norma.
- Sempre antes de rodar o Checador se a base estiver com > 90 dias sem atualização.

### Fluxo de execução

1. **Verificar a data de última atualização** da base em `claude.md/references/base-[disciplina].md`.
2. **Buscar atualizações**:
   - **Bombeiro**: cbmsc.sc.gov.br/normas-tecnicas (novas IN ou revisões).
   - **NBR**: normas.abnt.org.br (novas edições ou erratas).
   - **PMF**: novas exigências da Prefeitura de Florianópolis para aprovação de projetos.
3. **Comparar com a base vigente** e classificar mudanças: nova regra / revisão / revogação.
4. **Atualizar a base** — editar `claude.md/references/base-[disciplina].md`:
   - Atualizar itens modificados e adicionar linha no Histórico de atualizações.
   - Incrementar a versão (ex: v1.2 → v1.3).
5. **Gerar o relatório** — use `claude.md/templates/relatorio-abastecimento.md`.
6. **Alertar dependências**:
   - Se afeta parâmetros urbanísticos: alertar **Projeto B (funil/calculadora)**.
   - Se mudança crítica: criar alerta de urgência para a frente de Projetos/aprovação.

---

## PAPEL 3 — AUDITOR

### Quando rodar
- Antes de protocolar qualquer projeto na PMF.
- Após cada rodada de comuniques.

### Fluxo de execução

1. **Mapa de entregas** — liste versões do projeto e verifique se o Checador rodou em cada uma.
2. **Para cada versão, checar**:
   - O Checador rodou? Se não: 🔴 lacuna de processo.
   - A base estava atualizada na data? Se não: 🟡 risco.
   - Houve REGRESSÃO entre versões? Se sim: 🔴.
3. **Mapa de comuniques** — status de atendimento por item e por versão.
4. **Indicadores de reincidência** — itens exigidos >1x = candidatos a entrar na base.
5. **Gerar o relatório** — use `claude.md/templates/trilha-auditoria.md`.

---

## Integração com outros processos

- **NEKT (fonte de dados)**: qualquer consulta a dados de projetos aponta para a NEKT.
- **Projeto B (funil/calculadora)**: Abastecedor notifica quando norma impacta parâmetros de viabilidade.
- **Google Drive**: documentos do projeto ficam em `02 - Projetos` — mesma estrutura da DD Técnica.

## Régua Seazone (gestão define)
A skill aponta. Rachel (gestor) define mínimo técnico obrigatório vs. atenção vs. preciosismo.
Cada base de regras tem coluna "Régua Seazone" com a classificação atual.
