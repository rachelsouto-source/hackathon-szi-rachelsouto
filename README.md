# Auditor de DD Técnica — SZI Lançamentos

Projeto do **Hackathon SZI – IA First Investimentos** (trilha **Lançamentos**).
Skill do Claude Code que **elabora e audita a DD Técnica** de terrenos/empreendimentos.

## O problema (dor real)
A DD Técnica de um lançamento exige cruzar ~10 documentos (matrícula, cadastral,
confrontantes, viabilidade, topográfico, ambiental, sondagem, estrutura, fundação,
validação do arquiteto) para decidir **se o terreno é viável**. Hoje é manual, demorado,
e divergências (área, nº de unidades, gabarito) passam batido. É a "auditoria que ninguém
faz por falta de tempo".

## A solução
A skill lê os documentos no Google Drive, extrai os campos-chave de cada um, roda
**regras de cruzamento**, e gera:
1. **Parecer Técnico de DD** (documento, no formato oficial SZI);
2. **Planilha de controle** por etapa (status colorido);
3. **Conclusão** de viabilidade técnica + negócio (**go / go com ressalvas / no-go**).

## Duas formas de uso
1. **Skill do Claude Code** (`claude.md/SKILL.md`) — roda dentro do Claude Code.
2. **Aplicação web deployável** (`app/`) — publicada no **Coolify**, lê sozinha a pasta
   `02 - Projetos` no Drive, gera Google Doc + planilha, com **página manual** e **monitor
   automático**. Veja **`DEPLOY.md`**. Tem **modo demo offline** (Jurerê III) para testar
   sem credenciais: `cd app && DEMO_MODE=1 uvicorn main:app --reload`.

## Estrutura do repositório
```
auditor-dd-tecnica/
├─ README.md                      ← este arquivo
├─ DEPLOY.md                      ← deploy no Coolify + service account
├─ Dockerfile, requirements.txt, .env.example
├─ app/                           ← APLICAÇÃO WEB (FastAPI + frontend)
│  ├─ main.py                     ← rotas (DD, empreendimentos, monitor, xlsx)
│  ├─ core/                       ← dd_engine (Claude API), drive_client (Service Account),
│  │                                docs_writer (Google Doc + xlsx), monitor, playbook
│  └─ static/                     ← página "Gerar DD" (html/js/css)
├─ claude.md/                     ← CÓDIGO E ARQUIVOS DO PROJETO (skill + design)
│  ├─ CLAUDE.md                   ← contexto p/ retomar o projeto
│  ├─ SKILL.md                    ← a skill (instalar em .claude/skills/)
│  ├─ references/
│  │  ├─ dd-tecnica-playbook.md   ← documentos, campos e REGRAS de cruzamento
│  │  └─ legislacao-municipios.md ← órgãos/leis por município (parametrizável)
│  ├─ templates/
│  │  ├─ parecer-tecnico.md       ← template do parecer
│  │  └─ checklist-controle.csv   ← template da planilha de controle
│  ├─ scripts/
│  │  └─ gerar_checklist.py       ← gera a planilha .xlsx a partir dos achados
│  └─ exemplos/                   ← saídas REAIS do Jurerê Spot III
│     ├─ jurere-iii-achados.json
│     ├─ jurere-iii-parecer.md
│     └─ jurere-iii-controle-dd.xlsx
├─ lessons.md/                    ← erros encontrados, causa e solução
└─ memory.md/                     ← regras, convenções e decisões do projeto
```

## Como usar (resumo)
1. Instale a skill: copie a pasta com `claude.md/SKILL.md` para `.claude/skills/auditor-dd-tecnica/`.
2. Garanta acesso ao **Google Drive** via MCP (ler PDFs/planilhas).
3. Peça: *"Audita a DD técnica do [empreendimento]"* e informe a pasta no Drive.
4. A skill lê, cruza e gera parecer + planilha. Revise antes de oficializar.

## Como gerar a planilha de controle (exemplo)
```bash
pip install openpyxl
python claude.md/scripts/gerar_checklist.py \
  claude.md/exemplos/jurere-iii-achados.json "Jurere Spot III" \
  claude.md/exemplos/jurere-iii-controle-dd.xlsx
```

## Caso de referência
Construído e validado sobre o **Jurerê Spot III** (Florianópolis/SC). As saídas em
`claude.md/exemplos/` foram geradas a partir dos documentos reais e reproduzem os achados
do parecer oficial (divergência de áreas → retificação; 68 × 69 unidades; gabarito T+6 × PD).
