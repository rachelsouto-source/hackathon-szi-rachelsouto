# CLAUDE.md — Auditor de DD Técnica (contexto do projeto)

Contexto para qualquer pessoa (ou Claude) retomar este projeto sem reconstruir tudo.

## O que é
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

## Próximos passos (roadmap)
- Conectar a leitura direta da planilha geral (ID do empreendimento) para puxar metadados.
- Subir o parecer/planilha automaticamente na pasta do empreendimento no Drive.
- Expandir `legislacao-municipios.md` para os demais municípios da carteira.
- Cruzar com a "Checklist de Alvarás" para acompanhar pós-DD.
