# Roteiro de demo (vídeo ~3 min) + base de transcrição

Grave uma tela curta (Loom/Meet) mostrando **problema → solução → IA por trás**.
Abaixo, o roteiro e um texto-base que já serve de transcrição.

## Estrutura sugerida (≈3 min)
1. **Problema (30s)** — abrir a pasta de uma DD no Drive cheia de PDFs.
2. **Solução em ação (90s)** — pedir a auditoria no Claude Code e mostrar as saídas.
3. **IA por trás (30s)** — mostrar o playbook de regras e o CLAUDE.md.
4. **Fecho (30s)** — o que isso economiza e como o time usa amanhã.

## Texto-base (pode ler como narração / transcrição)

> "Toda DD Técnica de um lançamento é cruzar uns dez documentos — matrícula, cadastral,
> confrontantes, topográfico, ambiental, sondagem, estrutura, fundação e a validação do
> arquiteto — pra responder uma coisa: **o terreno é viável?** Hoje isso é manual, leva o
> dia, e divergências passam batido.
>
> Construí no Claude Code a skill **Auditor de DD Técnica**. Eu aponto a pasta do
> empreendimento no Drive e peço: *'audita a DD técnica do Jurerê Spot III'*.
>
> Ela lê os documentos, extrai os dados de cada um **com a fonte**, e roda as regras de
> cruzamento. No Jurerê III ela pegou sozinha: a **área da matrícula não bate com o
> topográfico** — diferença de 16%, acima dos 3%, então **exige retificação e amembramento**;
> o **EVA fala em 68 unidades e a estrutura em 69**; e o **gabarito Térreo+6 precisa ser
> validado contra o limite do Plano Diretor**. Tudo isso vira um **parecer no formato
> oficial** e uma **planilha de controle** com status colorido por etapa.
>
> No fim, ela conclui com a leitura de negócio: impacto em custo e prazo, os red flags
> priorizados — aqui o maior é a condicionante de esgoto da ACP — o aproveitamento versus
> VGV, e a recomendação: **GO com ressalvas**.
>
> A inteligência fica em dois lugares: o **playbook de regras** (`dd-tecnica-playbook.md`),
> que é o cérebro da auditoria, e o **CLAUDE.md**, que deixa qualquer pessoa do time retomar
> o projeto. A skill **não substitui** o parecer final — ela entrega um rascunho técnico de
> alta qualidade em minutos, pra revisão humana. Auditoria que ninguém fazia por falta de
> tempo, agora roda em qualquer terreno novo."

## Telas a mostrar (ordem)
1. Pasta do Jurerê III no Drive (vários PDFs).
2. Claude Code: o pedido + a skill lendo os documentos.
3. `exemplos/jurere-iii-parecer.md` (parecer preenchido, seção TOPOGRAFIA e CONCLUSÃO).
4. `exemplos/jurere-iii-controle-dd.xlsx` (planilha colorida).
5. `references/dd-tecnica-playbook.md` (as regras R1–R7).
6. Estrutura de pastas `claude.md/ lessons.md/ memory.md/`.

## Checklist de entrega (hackathon)
- [ ] Pasta no Drive compartilhada com avaliadores contendo `claude.md/`, `lessons.md/`, `memory.md/`.
- [ ] Link da gravação (Loom/Drive/YouTube unlisted).
- [ ] Transcrição (este texto-base serve).
- [ ] Enviar pelo formulário do site até **27/05 18:00**.
