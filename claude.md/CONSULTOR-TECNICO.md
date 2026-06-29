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
| `bombeiro` | Corpo de Bombeiros Militar SC (CBMSC) | `references/base-bombeiro-sc.md` | ✅ Ativo |
| `nbr` | Normas ABNT (foco NBR 9050 acessibilidade + NBR 15575 desempenho) | `references/base-nbr.md` | ✅ Ativo |
| `sst` | Segurança e Saúde no Trabalho (NRs MTPS) | `references/base-sst.md` | 🔜 Stub |

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
- **Histórico de comuniques** — liste os comuniques anteriores com data e status de cada item:
  - Comunique Nº X (data): item A → atendido; item B → pendente
- **Data da entrega** — para versionar a legislação vigente na data

### Fluxo de execução

1. **Carregar a base da disciplina** — leia `references/base-[disciplina].md` para ter as
   regras vigentes e a data de última atualização.
2. **Extrair dados do projeto** — dos documentos fornecidos, extraia:
   - Altura total (m) e número de pavimentos
   - Área total construída (m²)
   - Uso/ocupação (residencial multifamiliar, apart-hotel, misto, etc.)
   - Quantidade de unidades
   - Quantidade de vagas de garagem
   - Sistemas já projetados (escada tipo, hidrante, extintores, etc.)
3. **Classificar a edificação** — use a tabela da base de regras para determinar:
   - Grupo/Divisão de uso
   - Faixa de altura
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
6. **Gerar o relatório** — use o template `templates/relatorio-conformidade.md`.
7. **Listar decisões de gestão** — liste separadamente os pontos que dependem da
   **régua Seazone** (o que é mínimo vs. preciosismo) — a skill aponta, a gestão decide.

### Princípios
- **Fonte obrigatória**: cada item tem a norma/artigo de referência.
- **Nunca inventar**: documento ausente = Pendente.
- **REGRESSÃO acima de tudo**: quebrar um ponto já aprovado tem severidade máxima.
- **Parametrizável por município**: a legislação de bombeiros muda fora de SC.

---

## PAPEL 2 — ABASTECEDOR

### Quando rodar
- Mensalmente (sugestão) ou quando houver alerta de revisão de norma.
- Sempre antes de rodar o Checador se a base estiver com > 90 dias sem atualização.

### Fluxo de execução

1. **Verificar a data de última atualização** da base (`references/base-[disciplina].md`).
2. **Buscar atualizações** — pesquise por:
   - **Bombeiro**: novos decretos CBMSC, novas IN ou revisão das IN vigentes no site
     do CBMSC (cbmsc.sc.gov.br/normas-tecnicas).
   - **NBR**: novas edições ou erratas no site da ABNT (normas.abnt.org.br).
   - **SST**: novas NRs ou portarias do MTPS (trabalho.gov.br/normas-regulamentadoras).
   - **PMF**: novas exigências da Prefeitura de Florianópolis relevantes para aprovação
     de projetos (comuniques-padrão novos, mudanças no checklist de protocolo).
3. **Comparar com a base vigente** — para cada mudança identificada:
   - Classificar como: nova regra / revisão de threshold / revogação / acréscimo.
   - Avaliar se impacta projetos em andamento (🔴) ou somente novos projetos (🟡).
4. **Atualizar a base** — edite `references/base-[disciplina].md`:
   - Atualize os itens modificados.
   - Acrescente linha no **Histórico de atualizações** com data, norma modificada e sumário.
   - Incremente a versão (ex: v1.2 → v1.3).
5. **Gerar o relatório** — use `templates/relatorio-abastecimento.md`.
6. **Alertar dependências**:
   - Se a atualização afeta parâmetros urbanísticos ou indicadores de viabilidade:
     alertar o **Projeto B (funil/calculadora)** para reavaliar o impacto.
   - Se a atualização for uma mudança crítica (revogação de norma, novo requisito
     obrigatório), criar alerta de urgência para a frente de Projetos/aprovação.

---

## PAPEL 3 — AUDITOR

### Quando rodar
- Antes de protocolar qualquer projeto na PMF.
- Após cada rodada de comuniques (para garantir que o Checador rodou na versão corrigida).
- Periodicamente (sugestão: a cada nova entrega arquitetônica).

### Fluxo de execução

1. **Mapa de entregas do projeto** — liste as versões do projeto arquitetônico e datas
   (EP, AP, AE, PL, PD, revisões pós-comunique).
2. **Para cada versão, checar**:
   - O Checador rodou nesta versão? Se não: 🔴 lacuna de processo.
   - A base de regras usada estava atualizada na data da entrega? Se não: 🟡 risco.
   - Houve REGRESSÃO em algum item entre a versão anterior e a atual? Se sim: 🔴.
3. **Mapa de comuniques** — para cada comunique recebido:
   - Lista de itens exigidos.
   - Status de atendimento (atendido / pendente / contestado).
   - Versão do projeto em que cada item foi atendido.
4. **Indicadores de reincidência** — aponte itens exigidos mais de uma vez (reincidentes)
   — são candidatos a entry na base de regras ou ajuste na régua.
5. **Gerar o relatório** — use `templates/trilha-auditoria.md`.

---

## Integração com outros processos

- **NEKT (fonte de dados)**: qualquer consulta a dados de projetos (unidades, áreas,
  parâmetros) deve apontar para a NEKT — não usar planilhas ou Lake desatualizado.
- **Projeto B (funil/calculadora)**: o Abastecedor notifica quando uma atualização de
  norma impacta parâmetros de viabilidade (CA, TO, exigências que afetam a área útil).
- **Frente de Projetos/aprovação**: o Checador é disparado a cada entrega arquitetônica —
  alinhar com a frente de projetos o gatilho (ex: upload na pasta do Drive = disparo).
- **Google Drive**: documentos do projeto ficam em `02 - Projetos` — mesma estrutura
  usada pela DD Técnica.

## Régua Seazone (gestão define — não é a skill que decide)

A skill aponta. A gestão (Rachel) define o que é:
- **Mínimo técnico obrigatório** — exigência bloqueante para aprovação.
- **Atenção** — pode ser exigido em vistoria ou no comunique, mas não trava.
- **Preciosismo** — além do que a prefeitura exige; a depender do posicionamento do produto.

Cada base de regras tem uma coluna "Régua" com a classificação atual.
A régua é revisada a cada ciclo de validação (ver Fase 2 do plano de ação).
