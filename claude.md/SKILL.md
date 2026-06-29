---
name: auditor-dd-tecnica
description: >-
  Elabora e audita a DD Técnica (Due Diligence Técnica) de terrenos/empreendimentos
  da SZI (área de Lançamentos). Lê os documentos da DD no Google Drive (matrícula,
  certidão cadastral, confrontantes, viabilidade construtiva, levantamento topográfico,
  estudo ambiental/EVA, sondagem, estrutura, fundação e validação do arquiteto),
  cruza as informações entre os documentos, aponta divergências e pendências, e gera
  (1) o Parecer Técnico de DD em documento e (2) uma planilha de controle por etapa,
  concluindo com a viabilidade (go/no-go) técnica e de negócio. USE quando a pessoa
  pedir "auditar DD técnica", "fazer DD técnica", "parecer de viabilidade do terreno",
  "due diligence" de um empreendimento, ou mencionar conferir matrícula × topográfico ×
  ambiental × sondagem de um terreno.
---

# Auditor de DD Técnica — SZI Lançamentos

## 🌐 Acesso ao sistema (no ar)
**https://auditor-dd.seazone.properties**
> Interface web completa — escolha o empreendimento, clique em "Gerar DD" e veja o parecer técnico + planilha de controle em segundos. Funciona em modo demo com Jurerê Spot III e Farol da Barra Spot; em produção conecta diretamente ao Google Drive da SZI.

## O que esta skill faz
Automatiza a etapa de **DD Técnica** de um lançamento: parte de uma pasta do
empreendimento no Google Drive, **lê todos os documentos**, **cruza as informações**
entre eles, aponta **divergências/pendências**, e entrega:
1. **Parecer Técnico de DD** (documento, no formato oficial da SZI);
2. **Planilha de controle** por etapa (status: OK / Pendente / Divergência / Não se aplica);
3. **Conclusão de viabilidade** técnica + negócio (go / go com ressalvas / no-go).

## Quando usar
- "Auditar a DD técnica do [empreendimento]"
- "Fazer a DD técnica / parecer de viabilidade do terreno [X]"
- "Conferir se a matrícula bate com o topográfico do [X]"
- "Esse terreno é viável?"

## Fluxo de execução (passo a passo)

### 1. Localizar os documentos
- Pergunte (ou receba) o **nome do empreendimento** ou o **link/ID da pasta** no Drive.
- Use o MCP de Google Drive (`search_files`, `read_file_content`) para localizar e ler:
  matrícula, certidão cadastral (espelho IPTU), certidão de confrontantes, **Viabilidade
  Técnica Construtiva** (documento do site da prefeitura com o zoneamento e as exigências
  legais), levantamento topográfico, EVA (ambiental), sondagem, estrutura (quantitativo +
  tabela de carga), fundação, a validação do EP pelo arquiteto e — **se terreno de marinha** —
  a documentação da **SPU**.
- A **DD Jurídica não faz parte** desta DD Técnica (é consulta separada) — não incluir.
- Monte o **mapa de completude**: o que existe, o que falta. Veja
  `references/dd-tecnica-playbook.md` para a lista canônica de documentos.

### 2. Extrair os campos-chave de cada documento
Para cada documento, extraia os campos listados no playbook (ex.: da matrícula → nº,
cartório, área, proprietário, ônus; do topográfico → área real; do EVA → zoneamento,
TO/TP, APP, marinha, UC, condicionantes; da sondagem → tipo de fundação recomendado; etc.).
Registre **a fonte (nome do arquivo + link)** de cada dado — rastreabilidade é obrigatória.

### 3. Rodar os cruzamentos (auditoria)
Aplique TODAS as regras de `references/dd-tecnica-playbook.md`, em especial:
- **Consistência de área**: matrícula × cadastro PMF × confrontantes × topográfico.
  Se |área_topográfica − área_matrícula| / área_matrícula > **3%** ⇒ exigir
  **retificação de matrícula** (e avaliar amembramento se houver mais de uma matrícula).
- **Nº de unidades** coerente entre EVA, estrutura e estudo preliminar.
- **Gabarito / parâmetros urbanísticos** (TO, CA, recuo, TP) do estudo × Plano Diretor.
- **Ambiental**: APP, terreno de marinha (exigir afastamento **e conferir documentação da
  SPU**), UC, supressão vegetal, condicionantes de esgoto/licenciamento.
- **Geotécnico**: sondagem → fundação recomendada → coerência com doc estrutural → custo.
Cada achado vira um item com: **severidade** (🔴 crítico / 🟡 atenção / 🟢 ok),
**descrição**, **fonte** e **ação recomendada**.

### 4. Gerar as saídas
- **Parecer**: use `templates/parecer-tecnico.md`. Preencha IMÓVEL, PROPRIETÁRIO,
  lista de documentos (com links), CONCLUSÃO por subseção (Topografia, Ambiental,
  Validação do EP, Sondagem, Estrutura/Fundação) e a CONCLUSÃO final.
- **Planilha de controle**: use `scripts/gerar_checklist.py` (ou o template
  `templates/checklist-controle.csv`) para gerar o status por etapa.
- **Conclusão de negócio**: inclua impacto custo/prazo, red flags priorizados,
  aproveitamento × VGV (estimado) e a recomendação **go / go com ressalvas / no-go**.

### 5. Entregar
- Salve o parecer e a planilha; ofereça subir na pasta do empreendimento no Drive.
- Liste os pontos que precisam de decisão humana (a skill **assiste**, não substitui o parecer final).

## Princípios
- **Rastreabilidade**: todo dado citado tem fonte (arquivo + link).
- **Nunca inventar**: se um documento falta ou está ilegível, marque como **Pendente**, não presuma.
- **Parametrizável por município**: a legislação/órgãos mudam fora de Floripa
  (ver `references/legislacao-municipios.md`).
- **A pessoa valida**: a saída é um rascunho técnico de alta qualidade para revisão humana.
