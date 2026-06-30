---
name: auditor-dd-tecnica
description: >-
  Auditoria de DD Técnica (Due Diligence) de terrenos/empreendimentos SZI.
  USE quando: "auditar DD técnica do [X]", "fazer DD técnica", "due diligence do
  terreno [X]", "parecer de viabilidade do terreno [X]", "esse terreno é viável?",
  "conferir se a matrícula bate com o topográfico do [X]".
  ATENÇÃO: este skill foi unificado com o Consultor Técnico — toda a lógica está em
  .claude/skills/consultor-tecnico/SKILL.md (Modo A). Ao ser invocado, use o Modo A
  daquele skill diretamente.
---

# Auditor de DD Técnica — SZI Lançamentos

> **Este skill foi unificado com o Consultor Técnico.**
> Toda a lógica de DD Técnica está no **Modo A** do skill unificado:
> `.claude/skills/consultor-tecnico/SKILL.md`
>
> Ao ser invocado, execute diretamente o **Modo A — DD Técnica** conforme descrito lá.

## Resumo do Modo A

- **O que faz**: auditoria única na compra do terreno — lê todos os documentos, cruza informações, gera parecer com GO / NO-GO.
- **Documentos**: matrícula, IPTU, confrontantes, Viabilidade Construtiva (PMF), topográfico, EVA, sondagem, estrutura, fundação, validação do arquiteto (EP), SPU (se marinha), proposta de compra.
- **Regras R1–R7**: área, unidades, parâmetros urbanísticos, ambiental, geotécnico, completude, bombeiro.
- **Entregáveis**: Parecer Técnico + Planilha de controle + Resumo GO/NO-GO + Matriz de Risco + Lessons Learned.
- **Forma de raciocinar**: 7 perguntas por achado (O que? Como? Documento? Precedente? Risco? Impacto? Mitigação?).

Referência de playbook: `claude.md/references/dd-tecnica-playbook.md`
Referência de bombeiro (resumo para DD): `claude.md/references/base-bombeiro-dd-resumo.md`
