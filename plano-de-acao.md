# D — Consultor Técnico da DD técnica — Plano de Ação (v1)

**Responsável:** Rachel (conduz tudo) | **Supervisão:** Vini | **Validação final:** Caroline | **Status atual:** Conceito novo — provavelmente skill, vira agente se precisar rodar independente a cada entrega | **Data:** 2026-06-23

## Objetivo
O Consultor Técnico é da **DD técnica**: a auditoria que ele faz é da **DD técnica, por disciplina**. Habilitar a verificação técnica completa e contínua dos projetos de lançamento contra a legislação aplicável (NBR, bombeiro, segurança do trabalho e demais disciplinas), algo hoje inviável por falta de capacidade humana. Sai do modelo "rodar o que está na cabeça ou contratar consultor humano pontual" para um processo contínuo, escalável e versionado, em que cada disciplina técnica tem cobertura própria e a régua é definida pelo gestor.

## Orientação ao time
- Quero UM consultor técnico para CADA DD técnica e UM para CADA DISCIPLINA dentro da DD técnica.
- Cada disciplina opera com 3 PAPÉIS:
  1. um que pega a BASE pronta + o projeto e CHECA;
  2. um que busca NOVIDADES/atualizações da legislação e ABASTECE a base;
  3. um que AUDITA o que está acontecendo.
- Tratem como PROCESSO contínuo, não como entrega pontual.
- O objetivo é rodar NBR / bombeiro / segurança do trabalho INTEIRAS — hoje não temos capacidade (ou contratamos consultor humano, ou contamos com o que está na cabeça/mapeado). A NBR inteira a gente não rodava; agora podemos. Olhem tudo o que é bombeiro, NBR e segurança do trabalho.
- A RÉGUA é decisão de gestão: nós definimos o que seguir, o que é preciosismo demais e qual o mínimo técnico esperado para a nossa realidade.
- Testem em UM caso e usem a base como validação antes de replicar.
- Começa como SKILL; vira AGENTE se precisar rodar de forma independente a cada entrega.

## Diagnóstico do estado atual
- **Sem capacidade de cobertura completa:** hoje a NBR inteira não é rodada. A verificação técnica depende de consultor humano contratado pontualmente ou do conhecimento mapeado/na cabeça das pessoas.
- **Cobertura parcial e não rastreável:** não há garantia de que todas as disciplinas (bombeiro, NBR, segurança do trabalho) sejam checadas a cada entrega de projeto.
- **Aprovação na nossa mão, mas com retrabalho evitável:** corrigir um ponto exigido por um comunique pode estragar outro ponto que já estava atendido — falta histórico/versionamento do que já foi exigido e atendido.
- **Régua técnica implícita:** não há definição explícita, por disciplina, do que é mínimo esperado vs. preciosismo, para a realidade da Seazone.

## Arquitetura de agentes proposta (os 3 papéis por disciplina; skill vs agente)
Granularidade: um consultor por DD técnica e, dentro dela, um por disciplina (bombeiro, NBR, segurança do trabalho, etc.). Cada disciplina opera com 3 papéis:

1. **Checador (BASE + projeto → checa)** — recebe a base de regras consolidada da disciplina e o projeto/entrega da arquitetura; verifica conformidade contra a legislação vigente na data, versionando o protocolo, e contra o comunique atual E os anteriores (histórico). Saída: relatório de conformidade com pontos atendidos/não atendidos.
2. **Abastecedor (busca novidades → abastece a base)** — monitora atualizações de legislação/normas da disciplina; quando há mudança, atualiza a base de regras e sinaliza. Saída: base de regras versionada + alerta de mudança (inclusive para o funil — projeto B).
3. **Auditor (audita o que está acontecendo)** — audita execução do processo: se o checador rodou em cada entrega, se a base está atualizada, se nenhum comunique já atendido foi quebrado. Saída: trilha de auditoria + indicadores de reincidência.

**Skill vs agente:** começar como SKILL (invocada a cada entrega de projeto, sob comando). Migrar para AGENTE quando houver necessidade de rodar de forma independente/automática a cada entrega ou em cadência própria (ex.: abastecimento contínuo da legislação). Decisão a ser tomada após o piloto. [A DEFINIR]

## Plano de ação por fases

### Fase 0 — Discovery / escolher disciplina piloto
| Passo | Responsável | Entregável |
|---|---|---|
| Escolher a disciplina piloto (candidatas: bombeiro, NBR, segurança do trabalho) | Rachel | Disciplina piloto definida + justificativa |
| Selecionar 1 caso real (empreendimento/entrega) para o piloto | Rachel | Caso piloto definido |
| Definir a RÉGUA da disciplina (mínimo esperado vs. preciosismo, para nossa realidade) | Rachel (gestor) | Régua técnica documentada da disciplina |
| Mapear a base de regras inicial da disciplina | Rachel | Base de regras v0 |

### Fase 1 — Piloto em 1 caso
| Passo | Responsável | Entregável |
|---|---|---|
| Construir a skill com os 3 papéis para a disciplina piloto | Rachel | Skill do consultor técnico (piloto) |
| Rodar o Checador sobre o caso piloto (legislação vigente + comuniques atual e anteriores) | Rachel | Relatório de conformidade do caso piloto |
| Configurar o Abastecedor e o Auditor | Rachel | Base versionada + trilha de auditoria |

### Fase 2 — Validação na base
| Passo | Responsável | Entregável |
|---|---|---|
| Rodar o piloto contra a base (casos conhecidos) para validar acertos/erros | Rachel | Resultado validado vs. base |
| Aplicar revisão obrigatória + feedback Slack (joinha/negativo, modelo NEKT) | Rachel / equipe | Feedback consolidado |
| Ajustar a régua e a base conforme validação | Rachel (gestor) | Régua e base v1 |

### Fase 3 — Escala por disciplina / DD
| Passo | Responsável | Entregável |
|---|---|---|
| Replicar o padrão de 3 papéis para as demais disciplinas | Rachel | Consultor por disciplina |
| Compor as disciplinas em uma DD técnica completa | Rachel | DD técnica coberta |
| Decidir skill→agente onde fizer sentido rodar independente | Rachel | Definição skill vs agente por disciplina |
| Conectar ao funil (B) e à frente de Projetos/aprovação | Rachel | Integrações ativas |

## Responsáveis e papéis
- **Rachel (responsável — conduz tudo):** define a régua técnica por disciplina, escolhe disciplina e caso piloto, valida resultados, reordena prioridades no funil.
- **Vini (supervisão):** supervisiona a condução do projeto.
- **Caroline (validação final):** validação final das entregas.
- **Tatiana Souza:** sponsor do programa "Processos com IA".
- **Frente de Projetos/aprovação:** dona das entregas de arquitetura que disparam a consultoria a cada versão.
- **Construção da skill/agentes:** [A DEFINIR]
- **Curadoria da base de legislação por disciplina:** [A DEFINIR]

## Dependências e alinhamentos
- **D ↔ B (funil):** o Consultor Técnico (papel Abastecedor) avisa quando há atualização de legislação que abastece a calculadora do funil; o gestor reordena prioridades. Alinhar formato e canal do alerta.
- **D ↔ Projetos/aprovação:** a consultoria roda a CADA entrega da arquitetura, checando a legislação vigente naquela data (versionamento de protocolo) e a aderência ao comunique atual E aos anteriores (histórico). Quick win: a aprovação está "na nossa mão"; deixar de atender o que já foi exigido é evitável.
- **Fonte de dados:** NEKT (substitui o Lake). Apontar qualquer consulta/automação para a NEKT desde o início.

## Riscos e pontos de atenção
- **Régua mal calibrada:** preciosismo demais trava o projeto; régua frouxa demais perde a aprovação. Cabe ao gestor calibrar por disciplina.
- **Quebra de pontos já atendidos:** corrigir um comunique pode estragar outro já aprovado — exige histórico/versionamento e o papel Auditor ativo.
- **Base desatualizada:** se o Abastecedor falhar, o Checador roda contra legislação velha. Auditar a frescura da base.
- **Confiabilidade da interpretação normativa:** rodar "a NBR inteira" exige revisão humana obrigatória antes de tratar a saída como verdade técnica.
- **Escopo explodindo:** muitas disciplinas × muitos empreendimentos. Validar em 1 caso antes de replicar.
- **Skill vs agente prematuro:** não transformar em agente autônomo antes do piloto validar o valor.

## Métricas de sucesso
- **Cobertura de disciplinas cobertas** (nº de disciplinas com consultor ativo / total mapeado).
- **% de comuniques atendidos sem reincidência** (não voltar a quebrar ponto já atendido).
- **Régua técnica definida por disciplina** (nº de disciplinas com régua documentada).

## Próximos passos imediatos (esta semana)
1. Rachel escolhe a disciplina piloto (bombeiro / NBR / segurança do trabalho).
2. Selecionar 1 caso real para o piloto.
3. Definir a régua técnica da disciplina piloto (mínimo vs. preciosismo).
4. Alinhar com a frente de Projetos/aprovação o gatilho "a cada entrega da arquitetura".
5. Definir quem constrói a skill e quem cura a base de legislação. [A DEFINIR]
