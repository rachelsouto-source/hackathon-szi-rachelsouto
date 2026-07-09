# CLAUDE.md — Auditor de DD Técnica + Consultor Técnico (contexto do projeto)

Contexto para qualquer pessoa (ou Claude) retomar este projeto sem reconstruir tudo.
Produto publicado em: **https://auditor-dd.seazone.properties**

## Duas skills — dois momentos diferentes

| Skill | Arquivo | Quando usar |
|---|---|---|
| **Auditor de DD Técnica** | `SKILL.md` | Uma vez — na compra do terreno. Audita ~10 documentos para decidir viabilidade. |
| **Consultor Técnico** | `CONSULTOR-TECNICO.md` | A cada entrega arquitetônica. Verifica NBR, Bombeiro, SST. Tem 3 papéis (Checador, Abastecedor, Auditor). |

---

## Skill 1 — Auditor de DD Técnica

### O que é
Skill do Claude Code que **elabora e audita a DD Técnica** de lançamentos da SZI.
Trilha Lançamentos do Hackathon SZI. Caso-base: **Jurerê Spot III** (Florianópolis/SC).

## Como funciona (visão técnica)
1. **Tool use — Google Drive (MCP):** localiza a pasta do empreendimento e lê os
   documentos (`search_files`, `read_file_content`). Os PDFs/Docx/Sheets são lidos em
   linguagem natural pelo MCP — não há parser próprio.
2. **Extração estruturada:** para cada documento, extrai os campos do
   `references/dd-tecnica-playbook.md`, sempre com **fonte** (arquivo + link).
3. **Auditoria por regras (R1–R7):** cruza os dados entre documentos (área, unidades,
   gabarito/urbanístico, ambiental, geotécnico, jurídico, completude). Cada achado tem
   severidade (🔴/🟡/🟢), observação, fonte e ação.
4. **Saídas:** parecer (`templates/parecer-tecnico.md`) + planilha
   (`scripts/gerar_checklist.py` → `.xlsx`) + leitura de negócio (custo/prazo, red flags,
   aproveitamento×VGV, go/no-go).

## Arquivos-chave
- `SKILL.md` — definição e fluxo da skill (é o que o Claude Code carrega).
- `references/dd-tecnica-playbook.md` — **o cérebro**: documentos, campos e regras de cruzamento.
- `references/legislacao-municipios.md` — órgãos/leis por município (Floripa é o caso-base).
- `templates/` — formato do parecer e da planilha.
- `scripts/gerar_checklist.py` — gera a planilha de controle (requer `openpyxl`).
- `exemplos/` — saídas reais do Jurerê III (prova de funcionamento).

## Decisões importantes
- **A skill assiste, não substitui** o parecer final — sempre exige revisão humana.
- **Rastreabilidade obrigatória**: nada é afirmado sem fonte; documento ausente = Pendente.
- **Parametrizável por município**: a legislação muda fora de Floripa.
- A extração é feita pelo modelo + MCP do Drive (sem OCR/par/ parser dedicado), o que
  mantém o projeto simples e robusto a formatos variados de PDF.

## Próximos passos — Skill 1 (roadmap)
- Conectar a leitura direta da planilha geral (ID do empreendimento) para puxar metadados.
- Subir o parecer/planilha automaticamente na pasta do empreendimento no Drive.
- Expandir `legislacao-municipios.md` para os demais municípios da carteira.
- Cruzar com a "Checklist de Alvarás" para acompanhar pós-DD.
- **Integração com a Base de Conhecimento de DD Técnica (projeto do Vini)** — ver
  `references/base-conhecimento-integracao.md`. Passo 0 e seção "Precedentes" já
  adicionados ao fluxo (09/07/2026); falta decidir com o Vini o mecanismo real de
  consulta (Nekt SQL vs. Sheets API) antes de rodar em produção, e validar o valor
  prático com os 4 empreendimentos-piloto já extraídos (Campeche Spot, Jurerê Spot,
  Japaratinga, Jurerê Beach).

---

## Skill 2 — Consultor Técnico (Projeto D — Processos com IA)

### O que é
Skill do Claude Code que **verifica conformidade de entregas arquitetônicas** contra normas
técnicas (NBR, CBMSC/Bombeiro, SST) e histórico de comuniques. Roda a cada entrega,
não só na compra do terreno. Arquitetura de 3 papéis por disciplina.

### Arquivos-chave
- `CONSULTOR-TECNICO.md` — definição e fluxo da skill (3 papéis × 3 disciplinas).
- `references/base-bombeiro-sc.md` — base de regras CBMSC (disciplina piloto).
- `references/base-nbr.md` — base de regras NBR 9050 (acessibilidade) + NBR 15575.
- `references/base-sst.md` — base SST (stub — a desenvolver).
- `templates/relatorio-conformidade.md` — output do Checador.
- `templates/relatorio-abastecimento.md` — output do Abastecedor.
- `templates/trilha-auditoria.md` — output do Auditor.

### Decisões importantes
- **Começa como SKILL** — migra para agente autônomo só após validação do piloto.
- **REGRESSÃO tem prioridade máxima** — quebrar um ponto já atendido no comunique é
  mais grave do que não ter atendido ainda.
- **A régua é da gestão** — a skill aponta; Rachel (gestor) define mínimo vs. preciosismo.
- **Fonte de dados**: NEKT (não usar Lake/planilhas desatualizadas).
- **Piloto recomendado**: Bombeiro (CBMSC) — já referenciado em Jurerê Spot III (EEE).

### Próximos passos — Skill 2
- [ ] Rachel escolhe disciplina piloto e caso real (Fase 0 do plano de ação).
- [ ] Definir régua técnica da disciplina piloto (revisar coluna "Régua Seazone" na base).
- [ ] Rodar o Checador sobre o caso piloto (Jurerê III ou próxima entrega).
- [ ] Definir quem abastece a base e em que cadência.
- [ ] Conectar ao Projeto B (funil) o alerta do Abastecedor.
