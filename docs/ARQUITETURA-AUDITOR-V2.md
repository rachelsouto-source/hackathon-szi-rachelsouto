# Auditor de DD Técnica — Diagnóstico e Arquitetura Alvo (v2)

> **Status:** documento de arquitetura para validação. Nenhuma linha de código foi alterada.
> **Data:** 29/07/2026
> **Base de análise:** transcrição da revisão funcional de 29/07/2026 (Rachel Souto × Vinícius Melo, 44 min),
> código de `app/` e `base-conhecimento/` neste repositório, `seazone-tech/base-conhecimento-dd-tecnica`,
> `seazone-tech/diario-lancamentos`, e a PR [#2](https://github.com/rachelsouto-source/hackathon-szi-rachelsouto/pull/2).

---

## Nota de método (leia antes)

Três coisas sobre como este documento foi construído:

1. **A transcrição foi lida integralmente.** Ela contém requisitos que o resumo em 10 problemas
   não capturou — e um deles muda a arquitetura de forma estrutural (§1.3, item I1). Onde a
   transcrição e o resumo divergem, sigo a transcrição e sinalizo.
2. **O diagnóstico é feito sobre o código, não sobre a impressão.** Toda afirmação sobre o
   comportamento atual aponta arquivo e linha. Onde eu não pude verificar, digo que não pude.
3. **Existem quatro conflitos reais entre o que foi pedido na reunião e o que a base de
   conhecimento/código já estabelecem.** Eu não os resolvo sozinho — estão isolados em §16
   como decisões suas. Resolver isso antes de codar economiza uma refatoração.

Convenção de marcação usada ao longo do texto:

| Marca | Significado |
|---|---|
| ✅ | Verificado no código ou citado literalmente na transcrição |
| ⚠️ | Divergência entre fontes, ou requisito bloqueado por dependência externa |
| ❓ | Decisão pendente — precisa de você, não de mim |

---

## 1. Diagnóstico completo do Auditor atual

### 1.1 O que o sistema é hoje, tecnicamente

O Auditor não é um agente. É um **pipeline linear de uma única chamada ao modelo**, sem
ferramentas, sem memória e sem recuperação.

O caminho completo de uma auditoria, em produção ([app/main.py:127](../app/main.py#L127)):

```
POST /api/dd {id, nome}
  └─ locator.localizar(folder_id)          ← whitelist de 11 tipos de documento
  └─ drive_client.download_file_by_id(...) ← baixa bytes de cada um
  └─ dd_engine.audit(nome, docs)           ← 1 (UMA) chamada messages.create
  └─ locator.anexar_links(achados, fontes) ← cola links por keyword matching
  └─ docs_writer.render_parecer_md(...)
  └─ docs_writer.create_google_doc(...)
```

O núcleo é [app/core/dd_engine.py:88](../app/core/dd_engine.py#L88): um `client.messages.create`
com todos os PDFs em *document blocks* e o playbook como *system prompt* cacheado. Recebe
documentos, devolve JSON. **Não há loop, não há `tools=[...]`, não há segunda rodada.**

Isso explica, de uma vez, quase todas as dores levantadas na reunião: um modelo que só recebe
um pacote de PDFs e devolve JSON **não tem como** investigar, consultar a SPU, comparar com o
Patacho ou perceber que lhe falta informação. Não é uma falha de prompt. É uma falha de
arquitetura: faltam as capacidades, não as instruções.

### 1.2 Os dez problemas — validação um a um

Você pediu que eu validasse se os problemas listados são realmente esses. São, **com quatro
correções de diagnóstico** que mudam o que precisa ser feito.

---

#### ✅ **P1 — Não reexecuta análises. CONFIRMADO, mas a causa raiz é outra.**

Na transcrição, 22:44 — Vinícius: *"quando você clica em gerar DD ele não roda novamente, ele
tá pegando o que ele já fez em algum momento."*

O diagnóstico intuitivo é "cache". Não é cache. São **duas causas independentes**, e só uma
delas é a que vocês estão vendo:

**Causa A — o app em produção está em modo DEMO.** [app/main.py:37](../app/main.py#L37):

```python
def demo_mode() -> bool:
    if os.getenv("DEMO_MODE", "").lower() in {"1", "true", "yes"}: return True
    return not (drive_client.is_configured() and os.getenv("ANTHROPIC_API_KEY"))
```

Sem service account do Drive **ou** sem `ANTHROPIC_API_KEY`, o app cai em demo silenciosamente.
Em demo, `/api/empreendimentos` devolve uma lista fixa de 3 itens hardcoded
([app/main.py:80](../app/main.py#L80)) e `_demo_result()` lê **JSON estático versionado no
repositório** (`claude.md/exemplos/*-achados.json`).

Ou seja: o que o painel em `auditor-dd.seazone.properties` mostrou na reunião **não foi gerado
naquele momento**. É o arquivo `sao-miguel-achados.json` que está commitado no Git. Ele nunca
vai mudar por mais que se aperte "Gerar", porque nenhuma leitura do Drive acontece.

Isso reconcilia a fala de Rachel em 26:24 — *"eu rodo aqui no Claude e ele roda na base de
conhecimento, só que ele não tá atualizando o meu auditor"*. São literalmente dois sistemas
desconectados: a sessão do Claude Code (que faz o trabalho bom) e o app publicado (que serve
um snapshot congelado de dias atrás).

**Causa B — mesmo em produção, não há estratégia de reexecução.** `_RESULTS` é um
`dict` em memória ([app/main.py:34](../app/main.py#L34)), perdido a cada restart do
container, e não há nenhum controle de "o que mudou no Drive desde a última auditoria".

**Consequência para a arquitetura:** o requisito não é "invalidar cache". É **detecção de
delta + reexecução total + changelog entre rodadas**. Rachel formulou isso com precisão em
15:02 — *"levantamento topográfico pendente, tá ausente, só que a gente teve atualização"*.
O que ela quer não é só o parecer novo: é saber **o que mudou desde o anterior**.

---

#### ✅ **P2 — Não consulta fontes externas. CONFIRMADO. Parcialmente bloqueado por credencial.**

Transcrição 17:31 — Vinícius: *"Ele tem o número do RIP lá, ele não foi atrás de mais
informações de acordo com o RIP."* E 18:06: *"ele deveria ter olhado, falar 'tem uma área de
marinha, tenho esse RIP, vou buscar as informações'."*

Tecnicamente: `dd_engine.audit()` não passa `tools` na chamada. O modelo **não tem como** buscar
nada, nem se quisesse. Não é que ele deixa de buscar — ele não tem o verbo.

⚠️ **Correção importante ao requisito.** O item 2 da sua lista assume que basta "acessar
automaticamente a base adequada". Isso é verdade para *parte* das fontes SPU e falso para a
parte mais importante:

| Fonte SPU | Automatizável? | Evidência |
|---|---|---|
| **GeoPortal SPUNET** — shapefiles de LPM, LTM, polígono de terreno de marinha, atributos de homologação | ✅ **Sim** | Foi o canal que funcionou no 12235; os shapefiles oficiais foram baixados de lá |
| `geoportal.spu.gestao.gov.br` | ❌ Fora do ar (erro 525) | Testado 29/07 |
| **Consultar Dados Cadastrais de Imóvel da União** (dá a *área* da União no cadastro) | ❌ **Não** — exige login gov.br Bronze+ e resolve reCAPTCHA | Formulário renderiza vazio sem login |
| **Consultar Histórico Financeiro** (dá a taxa de ocupação → VDP → laudêmio) | ❌ **Não** — mesma barreira | Idem |
| Painel Qlik Transparência Ativa / API dados.gov.br | ❌ Cobrem imóveis de uso especial, não ocupações privadas; API exige chave | Testado 29/07 |

Isto é material: **o número que disparou todo o alerta do São Miguel — os 6.473 m² de área da
União no cadastro — vem justamente da consulta que exige login humano.** Um agente não faz
login gov.br nem resolve captcha.

**Consequência para a arquitetura:** a ferramenta de SPU precisa de dois modos — *autônomo*
(SPUNET, geometria, atributos de homologação) e *handoff humano* (cadastro e financeiro, onde
o agente **para, explica exatamente o que precisa e para quê, e espera**). Um agente que
finge ter consultado o cadastro é pior que um que declara a lacuna. Isso conecta direto com P6.

---

#### ✅ **P3 — Não compara com casos anteriores. CONFIRMADO — e é a maior deficiência, como você suspeitou. Com um bloqueio que ninguém mapeou.**

Transcrição 17:31 — *"ele não comparou com nenhum caso anterior, então subir tudo lá do Patacho"*.
E 19:23, no formato exato da saída desejada:

> *"Vocês tiveram um caso parecido no Patacho Spot, onde [terreno] foi perdido por área de marinha
> e acabou que lá a gente teve uma área de marinha maior do que a gente achava que tinha. Então é
> um ponto de atenção para essa nossa análise."*

No código: **não existe uma única linha em `app/` que consulte a base histórica.** O arquivo
`base-conhecimento/10-consulta-a-base-historica.md` descreve o fluxo de consulta em três passos
(sintese → granulares → documento no Drive) — mas é um documento de método lido por humano/skill.
O motor do app não o executa. O `SYSTEM_PROMPT` é uma string estática
([app/core/playbook.py:56](../app/core/playbook.py#L56)) sem nenhum canal de recuperação.

⚠️ **E aqui está o bloqueio que precisa entrar no radar imediatamente: o Patacho não está na base.**

O estado real de `seazone-tech/base-conhecimento-dd-tecnica` (`docs/RETOMADA.md`, 06/07):

- Base contém **5.005 linhas granulares / 206 sínteses**, de **exatamente 4 empreendimentos**:
  `2595` Campeche Spot, `6665` Jurerê Spot, `0584` Japaratinga, `2811` Jurerê Beach.
- **A fila dos 68 restantes está PAUSADA**, por decisão do Vini em 06/07, até que os 4 pilotos
  provem valor no dia a dia. `RETOMADA.md` é explícito: *"NÃO iniciar extração nova sem OK do Vini."*
- O Patacho está entre os **24 empreendimentos com sufixo PERDIDO** dessa fila pausada. O Vini
  decidiu que perdidos e cancelados **ficam** na fila — *"são os que mais trazem aprendizados"* —
  mas a fila não anda.

Ou seja: **a comparação que o Vinícius pediu duas vezes na reunião é hoje tecnicamente impossível,
e o desbloqueio depende dele, não de você.** Japaratinga (`0584`) está na base e é um precedente
de Alagoas válido — mas o Patacho, que é o caso emocionalmente central (Rachel, no kick-off do
Silas: *"vai ser o mesmo caso de Patacho"*), não está.

Isto vira o item nº 1 de dependências externas em §15.

---

#### ✅ **P4 — Não usa conhecimento acumulado. CONFIRMADO. E a lista de fontes está incompleta.**

Nenhuma das fontes é consultada pelo motor. Zero conexões.

⚠️ **A reunião criou uma sétima fonte que não está na sua lista de seis.** Em 07:01, Vinícius
propõe — e em 30:47/31:00 detalha — **um repositório GitHub por lançamento**:

> 07:01 — *"eu tô pensando em criar um GitHub por lançamento (...) tudo que a gente trabalhar a
> gente sobe para ele, para a gente ter o histórico detalhado."*
>
> 31:00 — *"eu vou fazer análise da topografia, faço a análise por dentro dele. Você vai fazer
> análise do EP (...) você pega e faz por ele e pede para ele subir. Andressa tá recebendo os
> estudos, ela joga para o Claude e fala 'recebi esse estudo, joga para o GitHub'."*

E em 32:01 ele fecha o modelo mental com **três fontes**, cada uma com um papel distinto:

| Fonte | O que é | Granularidade | Existe? |
|---|---|---|---|
| **Diário de Lançamentos** | Conversas e decisões do time (reuniões + Slack) | Histórico **resumido** | ✅ existe e roda |
| **Base de Conhecimento** | Documentos interpretados e destilados | **Síntese** por emp×disciplina×categoria | ✅ existe, 4 empreendimentos |
| **Repo do lançamento** | As análises que pessoa+IA fizeram, com o raciocínio | Histórico **completo** | ❌ **não existe — decidido nesta reunião** |

Nas palavras dele: *"a base é construída conforme os documentos da pasta e gera um resumo; o
nosso [repo] teria o histórico completo (...) essas três fontes de informação, quando a gente
precisa descobrir algo, revisitar algo, ou cruzar a informação de um empreendimento com [outro]."*

**Consequência para a arquitetura:** não são 6 fontes num saco. São **três camadas com
propósitos diferentes** — decisão (Diário), destilação (BC) e raciocínio (repo do lançamento) —
mais os documentos do empreendimento e a legislação. Tratá-las como equivalentes num índice
único destrói a informação mais útil, que é *de que tipo* é cada evidência.

---

#### ✅ **P5 — Não explica o raciocínio. CONFIRMADO. E há um requisito mais forte escondido aqui.**

O que existe hoje de rastreabilidade é [app/core/locator.py:160](../app/core/locator.py#L160):

```python
def anexar_links(achados, fontes):
    for ach in achados:
        et = _norm(ach.get("etapa", ""))
        for tipo, palavras in TIPO_PARA_ETAPA.items():
            if any(_norm(p) in et for p in palavras):
                ...  # cola o link
```

O link é colado **depois**, por *keyword matching no nome da etapa*. O modelo nunca declara
qual documento usou. Se ele escreve um achado com etapa `"Situação jurídica"`, nenhuma palavra
do `TIPO_PARA_ETAPA` casa e o achado sai **sem link nenhum**.

Foi exatamente isso que o Vinícius encontrou ao vivo, em 17:11 — *"aí a gente vai abrir, ele
não vai abrir no link específico; ele teria que abrir aqui essa certidão SPU, teria que estar
naquele link."* Não é um bug pontual. É que **a citação não é produzida pelo raciocínio, é
inferida por string matching depois dele.**

⚠️ **O requisito escondido — e é um dos achados mais fortes da transcrição.** Em 35:05, ao
descrever como ele mesmo chegou às conclusões do São Miguel, o Vinícius conta que sua **primeira
pergunta** ao Claude não foi sobre o terreno. Foi sobre a *fonte do fornecedor*:

> *"pedi: leia os documentos e me diga de onde ele tá tirando a linha de marinha e de onde tá
> tirando aquela linha do ambiental. (...) Aí o que ele me trouxe: aparentemente são linhas que
> ele mediu no levantamento, ele não cita fonte, ele não cita nada. Opa, calma aí, tem coisa aí."*
>
> 38:05 — *"nem a planta nem o relatório citam de onde veio. Eu falei: tá errado, então você não
> tem fonte, o cara tirou da cabeça dele."*

Isto **não é** rastreabilidade do Auditor. É o Auditor **auditando a rastreabilidade do
entregável de terceiro**. E foi a pergunta que destravou o caso inteiro do São Miguel — porque
revelou que a prancha da MCZ estava metricamente correta mas apoiada numa **premissa errada**
(traçou a LPM *atual*, maré de hoje, quando a lei define terreno de marinha pela preamar-média
de **1831** — DL 9.760/1946, art. 2º).

Isso vira uma regra nova de auditoria, hoje inexistente no playbook. Chamo de **R10** em §5:

> *Todo dado técnico determinante em documento de terceiro deve declarar sua fonte e sua
> premissa normativa. Documento sem fonte declarada é achado, independentemente da qualidade
> da medição. Medição boa sobre premissa errada é o modo de falha mais caro da DD.*

---

#### ✅ **P6 — Não sabe quando buscar mais informação. CONFIRMADO. Com um contra-requisito.**

Hoje é estruturalmente impossível: uma chamada única sempre produz uma resposta completa. O
schema de saída ([app/core/playbook.py:192](../app/core/playbook.py#L192)) **obriga** o modelo a
preencher `conclusao.final` e `negocio.recomendacao`. Não existe estado "não sei ainda".

O playbook tem `R6.c — pendência herda a criticidade do que esconde`, que é a regra certa —
mas ela transforma lacuna em *achado de severidade alta*, e mesmo assim segue para a conclusão.
Falta o degrau acima: **interromper**.

⚠️ **Contra-requisito, de 38:29** — Vinícius: *"Ele deu uma sugestão que eu ignorei completamente,
porque geralmente ele dá sugestões que não fazem sentido."*

Ou seja, o problema não é só "ele não pede informação quando falta". É que **ele preenche o
vazio com palpite**, e o custo disso já foi pago em confiança. Um agente que declara "não sei"
com precisão vale mais do que um que sempre conclui. Isso exige que cada afirmação carregue
**tipo** (fato / inferência / precedente / hipótese) e **confiança** — e que hipótese de baixa
confiança seja *suprimida do parecer*, não enfeitada.

---

#### ✅ **P7 — Não executa processo investigativo. CONFIRMADO. O fluxo que você desenhou está certo.**

O fluxo de 12 passos da sua lista é uma boa descrição do alvo. Só falta operacionalizar duas
coisas que ele não diz: **quando o loop para**, e **o que acontece quando duas iterações se
contradizem**. Ambas em §4 e §6.

---

#### ⚠️ **P8 — Sistema iterativo. CONFIRMADO NO ESPÍRITO, ERRADO NA FORMA. Esta é a correção mais importante deste documento.**

Sua lista descreve iterações **autônomas**: `Iteração 1 → descobri um RIP → Iteração 2 → consultar
SPU → Iteração 3 → comparar com Patacho → ...`. Um pipeline de N estágios que roda sozinho.

Não foi isso que foi pedido. Em 42:01, o Vinícius descreve o ciclo que ele quer, e o humano
está **dentro** dele:

> *"Eu dei o caminho todo para ele. Eu fui jogando informação e ele me dando resposta; **aí eu
> analiso a resposta e falo 'não é bem isso', jogo de volta**, ele tem resposta, jogo de volta,
> tem resposta — **até a gente chegar numa explicação razoável**, não sobrar mais dúvidas."*
>
> 42:24 — *"ele pega o que a gente tem, compara com os outros, **traz a resposta, você retorna
> para ele**, ele usa mais informação que você deu, analisa, retorna, analisa, retorna."*
>
> 43:02 — **"Ele não vai ter todas as respostas sozinho, sabe?"**

E o caso real do São Miguel foi resolvido exatamente assim — inclusive com o humano **corrigindo
o agente e o agente aceitando a correção** (41:27):

> *"Eu falei para ele: na demarcação tem uma parte do terreno próxima da praia que você não tá
> considerando como de marinha, mas ela é de marinha, porque a linha de preamar tá aqui e eu
> tenho terreno para baixo dela — ela é terreno acrescido de marinha. E ele falou 'é isso mesmo,
> você tá correto'. E aí ele recalculou e chegou à conclusão de que a área total dá 6.900 m²."*

**A diferença arquitetural é enorme:**

| Se for autonomia (sua lista) | Se for diálogo (a transcrição) |
|---|---|
| Job batch, dispara e espera | **Sessão persistente com turnos** |
| Estado interno, descartável | **Estado auditável e endereçável** — o humano precisa apontar *qual* afirmação está errada |
| Termina quando o pipeline acaba | Termina quando **o humano não tem mais objeção** |
| Reexecuta tudo a cada rodada | Reabre **só o subgrafo afetado** pela contestação |
| Painel é output | Painel é **superfície de contestação** — e isso justifica o painel que a Rachel quer manter |

A forma autônoma é um subconjunto: o agente investiga sozinho **até onde consegue**, e então
apresenta o estado para contestação. As duas convivem. Mas se o sistema for construído como
batch puro, o "jogo" não tem onde acontecer, e a assertividade que o Vinícius atribui ao processo
dele (*"eu fiz ele ser assertivo"*, 34:33) não se reproduz.

Isso reposiciona o painel de "não é prioridade" para "é a interface do loop de contestação" —
o que resolve elegantemente a tensão da §1.4.

---

#### ✅ **P9 — Aprendizado contínuo. CONFIRMADO. Com uma restrição de governança e uma distinção que falta.**

O mecanismo está desenhado em `10-consulta-a-base-historica.md` §Realimentação e é o correto.
O que falta reconhecer:

⚠️ **Restrição:** a base histórica é o repo do Vini e **você tem acesso somente leitura**
(`push: false`). A realimentação automática não pode escrever lá. Precisa ser: gerar as linhas
no schema exato de `engine/schema.py` → área de staging no seu repo → PR / entrega ao Vini.

⚠️ **Distinção que falta na sua lista:** aprender tem **dois canais**, e misturá-los é um erro
comum e caro:

1. **Memória de caso** → uma linha granular em `aprendizados` ("no 12235 a demarcação de 2004
   colocou 80% do lote sob a União"). Alimenta *precedentes*.
2. **Correção de método** → uma regra nova em `base-conhecimento/04-regras-de-auditoria.md`
   ("medição correta sobre premissa errada"). Alimenta *como auditar*.

A PR #2 já é um exemplo do canal 2 funcionando manualmente: R3.a, R3.b, R6.a, R7, R8, R9
nasceram todas de falhas reais encontradas na reauditoria do Novo Campeche. O que falta é
tornar isso um ciclo, não um heroísmo pontual.

---

#### ⚠️ **P10 — "O Painel NÃO é prioridade". CONFIRMADO EM PARTE. A formulação está mais dura que o combinado.**

O que foi realmente dito, na íntegra:

> 26:32 — Vinícius: *"a gente não precisa desse painel que você fez, ele consegue rodar tudo isso
> pelo terminal ou pelo próprio aplicativo e só gerar um parecer em Word."*
>
> 30:16 — *"pra mim não faz diferença, ele não agrega nada; no fim das contas, ser por ele ou por
> um doc dá na mesma. **Pode manter, não é um problema. Ele só não pode ser um motivo de
> travamento para você.** Se em algum momento ele for um motivo de travamento, você mata ele e faz
> um doc."*
>
> 30:35 — **"não vejo problema nenhum em manter, para falar a verdade."**

E a Rachel, duas vezes:

> 26:50 — *"minha intenção era trazer essa visibilidade, porque eu realmente não queria morrer
> com esse painel."*
>
> 28:32 — *"eu quero manter esse auditor. Como arquiteta, (...) para a gente às vezes querer ver
> algo um pouco mais didático e rápido, a gente poderia manter um painel. E aí esse painel
> obviamente no final gera o doc — **só que ele precisa estar contemplando tudo que você trouxe**."*

O acordo real não é "o painel não é prioridade". É: **o painel é permitido e desejado, desde que
(a) não esteja no caminho crítico e (b) reflita tudo que o núcleo produz.** A exigência
arquitetural — núcleo headless, painel como um renderer entre vários — é a mesma. Mas a
prioridade de produto é diferente, e vale registrar assim para não jogar fora um trabalho que a
Rachel quer manter e o Vinícius não se opõe a manter.

E, como argumentei em P8, o painel deixa de ser cosmético: **é onde a contestação acontece.**

---

### 1.3 Requisitos implícitos que não estavam na lista de dez

Você pediu explicitamente que eu lesse a intenção técnica por trás das falas. Estes são os itens
que emergem da transcrição e **não** aparecem no resumo de 10 problemas. Numerados I1–I9.

---

**I1 — O humano é parte do loop, não o consumidor do resultado.**
Já tratado em P8. É o item de maior impacto arquitetural do documento.

---

**I2 — Auditar a fonte e a premissa do entregável de terceiro (regra R10).**
Já tratado em P5. *"Não cita fonte, o cara tirou da cabeça dele"* (38:05).

---

**I3 — Proximidade geográfica é chave de recuperação, não só similaridade semântica.**

> 25:56 — *"ele já poderia ter olhado a sondagem dos empreendimentos próximos. Tenho algum
> próximo? Ah, tenho o Patacho que tá a **x km**, deixa eu dar uma olhadinha e trazer um parecer
> com base nele."*
>
> 23:35 — *"Japaratinga, que são lugares próximos (...) **a gente tem a localização dos terrenos**,
> ele deveria olhar isso também."*

O item 3 da sua lista fala em "recuperação semântica baseada em contexto". Correto, mas
insuficiente: para **sondagem**, o preditor não é semântica — é **distância física**, porque o
perfil geotécnico é uma propriedade do lugar. Para **licenciamento**, o preditor é o **órgão**
(mesmo município). Para **marinha**, é o **regime dominial** e o **trecho de demarcação**.

Isso significa que o ranqueamento de precedentes é **multi-critério e depende da disciplina**,
não um único score de similaridade. Detalho em §10.

---

**I4 — O status de homologação da linha de marinha é metadado, é por trecho, e o time de Terrenos não o tem.**

> 03:50 — Vinícius: *"a gente teve a confirmação com o Cláudio: **depende, porque ela é por
> trechos e a validade é por trecho**. Tem linhas aqui que estão homologadas, tem linhas que
> estão no processo de demarcação que não foi concluído. Nesse caso aqui, ela tá homologada."*
>
> 05:01 — *"**tem como extrair a situação da demarcação**, se ela tá homologada ou não. E claro,
> isso foi possível com a IA — que aí já consegue ler todos os metadados muito fácil. Mas **hoje
> elas [o time de Terrenos] não têm essa indicação** se a linha tá homologada ou não."*

Dois requisitos aqui, e o segundo é fácil de perder:

1. A ferramenta de geoprocessamento tem de ler **atributos das feições**, não só a geometria.
   "Está homologada?" é uma coluna do shapefile, e a resposta é *por trecho*.
2. ⚠️ **Esse conhecimento tem de voltar para o time de Terrenos.** Vinícius, em 04:28: *"não dá
   para falar que o pessoal de terreno está errado — eles estão [errados], mas era conhecimento
   que a gente não tinha na época. Talvez valha a pena trocar uma ideia com a Maria e com a Thaís."*
   O Auditor produz conhecimento que corrige o processo **a montante**. Isso é uma saída do
   sistema, não só uma entrada.

---

**I5 — Precedente que contradiz a análise é sinal, não ruído. E o falso positivo tem custo.**

O trecho mais interessante da reunião, 10:05–12:11:

> Vinícius: *"tem um Mirage, Patacho — como é que eles estão fazendo o empreendimento se a linha
> de marinha deles vem aqui? (...) Se isso aqui tudo tá homologado, **como é que eles estão
> lidando com isso? Não faz sentido na minha cabeça, eu não consigo entender.**"*
>
> Rachel: *"a gente entrou nesse parafuso também (...) **às vezes a gente tá até perdendo o
> terreno nesse sentido**, sabe?"*
>
> Rachel: *"será que é uma terra sem lei?"*

Dois requisitos, e o segundo contraria a tendência natural do sistema:

1. **Anomalia do entorno gera hipótese.** Se a análise conclui "inviável" e há empreendimentos
   vizinhos construídos sob a mesma restrição, isso é uma **contradição a investigar**, não um
   detalhe. A explicação pode ser um instrumento que a Seazone não conhece — e o próprio Silas
   deu duas pistas: **incorporação antes da venda** (08:15) e **aforamento / retificação de
   georreferenciamento** (memória do kick-off).
2. ⚠️ **O Auditor atual é assimétrico: só procura risco.** Todas as regras R1–R9 são detectores
   de problema. Nada no sistema pergunta *"esse risco está superestimado?"*. Rachel diz
   literalmente que isso já custou terreno. Um auditor calibrado precisa de um contrapeso —
   proponho o agente **Calibrador de Entorno** em §6.

---

**I6 — O mesmo fato físico tem risco diferente conforme o modelo de negócio.**

> 08:15 — Rachel: *"perguntei ao Silas como vocês estão lidando com empreendimentos que têm uma
> área grande na SPU. Ele falou que já pegou um que é tipo 50% do terreno e que o trâmite é
> tranquilo, **porque eles fazem incorporação — eles incorporam antes**. Não é igual a gente,
> que não faz incorporação agora."*
>
> 08:46 — *"então **para a gente é muito mais risco**. Esse é o porém."*

70% de área de marinha é aceitável para a Citecon e crítico para a Seazone, pelo **instrumento
jurídico da operação**, não pela geografia. O Auditor precisa do **perfil de operação da Seazone**
como parâmetro de contexto — senão importa precedentes de terceiros com a severidade errada.

---

**I7 — A fronteira com a DD Jurídica está sendo redesenhada. ⚠️ E isso contradiz frontalmente o código e a base de conhecimento atuais.**

> 21:40 — Vinícius: *"nesse caso, para mim essa parte está errada, porque **a DD jurídica vem do
> jurídico**. Então ele precisa pegar a DD jurídica — ele pode dar um parecer para eliminar, mas
> **o jurídico, até onde eu sei, já aprovou a compra desse terreno** em termos jurídicos, de
> documentação, débitos, ok. Então **ele deveria olhar esse material e trazer esse parâmetro**,
> porque é óbvio que o jurídico vai solicitar uma matrícula atualizada — faz parte da diligência
> jurídica. Então **ele já deveria se atualizar com o resultado da diligência** e já trazer o
> parecer de que tá tudo certo."*

Hoje, o código diz o oposto, em dois lugares:

- [app/core/playbook.py:64](../app/core/playbook.py#L64) — `"A DD JURÍDICA NÃO faz parte desta DD
  Técnica (é consulta separada) — ignore."`
- `memory.md/memory.md` — *"DD Jurídica NÃO entra nesta DD Técnica"*, registrada como **lição L6**,
  validada com a coordenadora.

A leitura correta da divergência, na minha avaliação: **não são posições opostas, são dois papéis
diferentes da matrícula.** O que o Vinícius rejeita é o Auditor *refazer* a análise dominial e
emitir exigências que já são do jurídico. O que ele quer é que o Auditor **consuma o resultado
da DD Jurídica como um input com fonte** — "o jurídico aprovou, matrícula X, sem ônus, em tal
data" — e o use como parâmetro nas regras técnicas (área da matrícula para R1, regime dominial
para R4, restrições para R8).

Ou seja: a matrícula deixa de ser **objeto de análise primária** e passa a ser **resultado
consumido de outra diligência**, com o jurídico como fonte de verdade. Isso é uma mudança de
regra concreta e barata de implementar — mas ❓ **precisa da sua validação**, porque contradiz uma
lição que já foi validada com a Caroline. Está em §16.

---

**I8 — Transcrição de reunião é fonte de evidência de primeira classe.**

> 43:24 — Vinícius: *"você pode jogar essa transcrição para ele também, que ele vai conseguir."*

E é o que o Diário já faz — ele é construído *de* transcrições e Slack. Confirmado no
`diarios/12235-sao-miguel-dos-milagres.md`, onde cada risco carrega link para a transcrição e
uma âncora estável (`<!--anc:reuniao:<docId>:<slug>-->`). Essa âncora é ouro para rastreabilidade:
permite citar **a frase exata da reunião** como evidência.

---

**I9 — Ingestão é multi-ator.**
31:00 — a Andressa recebe estudos e os envia ao repo. O Auditor não pode assumir que a Rachel é
a única fonte de entrada. Implicação de governança em §14 (quem pode inserir evidência, e com
que nível de confiança).

---

### 1.4 Achados de código que a reunião não pegou

Diagnóstico próprio, sobre o código. Três são bugs que afetam o comportamento observado.

**A. ⚠️ O monitor automático nunca dispara.**
[app/core/monitor.py:27](../app/core/monitor.py#L27):

```python
arquivos = drive_client.list_files(folder_id)     # SÓ a raiz do empreendimento
nomes = [f["name"] for f in arquivos if f["mimeType"] != "...folder"]
```

`list_files` não é recursivo, e os documentos da DD vivem em `02 - Projetos/<NN>/` e
`05 - Jurídico/...`. A raiz de um empreendimento contém **pastas**, quase nenhum arquivo. Logo
`nomes` sai praticamente vazio, `faltando` inclui tudo, e
`elegivel = (not faltando) and (not ja_tem_dd)` é **sempre falso**. A DD automática do
`/api/monitor/run` nunca roda. Não custa nada corrigir e hoje é código morto.

**B. ⚠️ A whitelist do `locator` é a razão pela qual o Auditor não enxerga o que importa.**
[app/core/locator.py:108](../app/core/locator.py#L108) define `SOURCES` — 11 tipos de documento,
cada um com caminho de pasta e aliases de nome fixos. **Um arquivo que não casa com nenhuma
entrada é invisível para o Auditor.** Por construção.

Aplicado ao São Miguel: a pasta `02 Projetos / 03 Levantamento Topográfico / **06 Confronto SPU**`
(`13FLcSrMKMkV5_ec2l_fIQ22wk5YMeocN`), o `CONFRONTO_SPU_x_MCZ.dxf`, os shapefiles do SPUNET, o
`linha_marinha.dxf`, os KMZ — **nada disso existe para o Auditor**. E é onde está a resposta.
Some-se `depth=1` em `_all_files_recursive` e a cegueira fica mais profunda.

Isto é o oposto de `R6.b — varredura exaustiva antes de concluir`, que a própria PR #2
introduziu. **A regra existe no prompt e o código a impede de ser cumprida.** O Cartógrafo (§6)
existe para resolver isso.

**C. Limites operacionais.**
- `MAX_TOKENS = 8000` ([dd_engine.py:20](../app/core/dd_engine.py#L20)) — o parecer do Novo
  Campeche tem 18 achados e 6 seções de conclusão em prosa. Risco real de truncamento silencioso;
  o `_parse_json` falharia com "JSON inválido" sem dizer que foi truncamento.
- `MODEL` default `claude-sonnet-4-5` ([dd_engine.py:19](../app/core/dd_engine.py#L19)) —
  desatualizado; a família Claude 5 é a atual. Trocar por `claude-opus-5` para o raciocínio de
  auditoria e reservar modelos menores para tarefas mecânicas (classificação de arquivo,
  extração) é ganho direto de qualidade e de custo.
- **Três cópias locais divergentes do app**, conforme a própria PR #2 registra. Eleger uma
  oficial antes de qualquer refatoração, ou o trabalho se perde.

---

## 2. Fluxo atual

```
┌──────────────┐
│ Painel (web) │  clique em "Gerar DD"
└──────┬───────┘
       ▼
┌─────────────────────────────────────────────────────────┐
│ demo_mode()?  ──── SIM ──▶ lê JSON estático do repo ────┼──▶ FIM (congelado)
└──────┬──────────────────────────────────────────────────┘
       │ NÃO
       ▼
┌────────────────────────┐
│ locator.localizar()    │  whitelist de 11 tipos · caminhos fixos · depth=1
│                        │  ❌ tudo fora da whitelist é invisível
└──────┬─────────────────┘
       ▼
┌────────────────────────┐
│ download dos bytes     │
└──────┬─────────────────┘
       ▼
┌─────────────────────────────────────────────────────────┐
│ dd_engine.audit()  ── UMA chamada messages.create ──────│
│   system = SYSTEM_PROMPT (playbook estático, cacheado)  │
│   user   = [PDF, PDF, PDF, ...]                         │
│   tools  = ∅   ❌ sem ferramentas                        │
│   loop   = ∅   ❌ sem iteração                           │
│   memória= ∅   ❌ sem precedentes, sem diário            │
└──────┬──────────────────────────────────────────────────┘
       ▼
┌────────────────────────┐
│ anexar_links()         │  ❌ citação por keyword matching, pós-hoc
└──────┬─────────────────┘
       ▼
┌────────────────────────┐
│ render → Google Doc    │  força GO / GO COM RESSALVAS / NO-GO
│         → .xlsx        │
│         → _RESULTS{}   │  ❌ dict em memória, perdido no restart
└────────────────────────┘
```

**Resumo em uma frase:** um resumidor de documentos muito bem instruído. O playbook é excelente —
R1–R9 são regras de auditor sênior de verdade. O problema é que ele é aplicado sobre um conjunto
de documentos incompleto, escolhido por uma whitelist, numa única passada, sem poder verificar
nada externamente e sem lembrar de nada.

---

## 3. Fluxo ideal

```
                    ┌───────────────────────────────────────────┐
                    │  GATILHO                                  │
                    │  humano · cron · webhook do Drive · API   │
                    └────────────────┬──────────────────────────┘
                                     ▼
╔═══════════════════════════ FASE 1 · ENQUADRAR ════════════════════════════╗
║  Cartógrafo                                                                ║
║    · varre a árvore INTEIRA do empreendimento (sem whitelist)              ║
║    · classifica CADA arquivo: lido / não lido / não aplicável   [R6.b]     ║
║    · diff contra o manifest da rodada anterior → o que mudou               ║
║    · monta o Perfil do Caso: cidade, UF, coordenadas, regime dominial,     ║
║      flags (marinha? APP? tombado? demolição? MP/liminar?), produto,       ║
║      instrumento de aquisição                                              ║
╚═══════════════════════════════════╤═══════════════════════════════════════╝
                                    ▼
╔══════════════════════ FASE 2 · LER (paralelo por disciplina) ═════════════╗
║  jurídico-cartorial · topografia · ambiental · urbanístico ·               ║
║  geotécnico · incêndio · negócio                                           ║
║                                                                            ║
║  cada leitor emite AFIRMAÇÕES no Livro de Evidências,                      ║
║  cada uma com fonte, trecho, tipo e confiança — nunca prosa solta          ║
╚═══════════════════════════════════╤═══════════════════════════════════════╝
                                    ▼
╔══════════════════════ FASE 3 · LEMBRAR (paralelo) ════════════════════════╗
║  Historiador → base histórica: precedentes por cidade/UF/distância/        ║
║                disciplina/regime · sempre incluindo erros e gargalos       ║
║  Cronista    → Diário: riscos e decisões já registrados pelo time          ║
║              → repo do lançamento: análises anteriores e seu raciocínio    ║
╚═══════════════════════════════════╤═══════════════════════════════════════╝
                                    ▼
╔══════════════════════ FASE 4 · CRUZAR ════════════════════════════════════╗
║  Motor de regras R1–R10 sobre o Livro                                     ║
║    → gera achados, LACUNAS e HIPÓTESES                                     ║
║  Calibrador de Entorno: o risco está superestimado?          [I5]         ║
╚═══════════════════════════════════╤═══════════════════════════════════════╝
                                    ▼
              ┌─────────────────────────────────────────┐
              │  Há lacuna crítica que uma ferramenta   │
              │  ainda não tentada poderia resolver?    │
              └────────┬───────────────────────┬────────┘
                    SIM│                       │NÃO
                       ▼                       │
╔═══════════ FASE 5 · INVESTIGAR ═══════════╗  │
║  Investigador escolhe e chama ferramentas: ║  │
║    SPU/SPUNET · geoprocessamento · legis-  ║  │
║    lação vigente · web · Drive (busca      ║  │
║    dirigida) · base histórica (2ª volta)   ║  │
║                                            ║  │
║  ⚠️ Ferramenta indisponível ou que exige   ║  │
║     credencial humana (gov.br) →           ║  │
║     emite PEDIDO AO HUMANO, não palpite    ║  │
╚═════════════════════╤══════════════════════╝  │
                      └──── volta à FASE 4 ─────┤   (máx. N iterações)
                                                ▼
╔══════════════════════ FASE 6 · CONTESTAR ═════════════════════════════════╗
║  Contraditor: tenta REFUTAR cada afirmação crítica                        ║
║    · a premissa normativa está certa?                     [R10 / LPM 1831]║
║    · a fonte sustenta a conclusão?                                        ║
║    · há leitura alternativa dos mesmos dados?                             ║
║  Sobreviveu → confirmada · Caiu → refutada · Empatou → indeterminada      ║
╚═══════════════════════════════════╤═══════════════════════════════════════╝
                                    ▼
╔══════════════════════ FASE 7 · APRESENTAR ════════════════════════════════╗
║  Redator renderiza DO LIVRO (não escreve livre):                          ║
║    · parecer · achados com evidência · precedentes citados                ║
║    · LACUNAS ABERTAS e o que é preciso para fechá-las                     ║
║    · PERGUNTAS AO HUMANO                                                  ║
║    · CHANGELOG contra a rodada anterior                                   ║
║  Superfícies: painel · Word/GDoc · .xlsx · JSON via API · terminal        ║
╚═══════════════════════════════════╤═══════════════════════════════════════╝
                                    ▼
                 ┌──────────────────────────────────────┐
                 │  O HUMANO CONTESTA                   │  ← o "jogo" [I1]
                 │  "não é bem isso" numa afirmação     │
                 └──────────┬───────────────┬───────────┘
                    contesta│               │aceita
                            ▼               ▼
              reabre SÓ o subgrafo    ╔══ FASE 8 · APRENDER ═══════════════╗
              afetado → FASE 4        ║  Curador (só após aceite humano):  ║
                                      ║   · achados → linhas granulares na ║
                                      ║     taxonomia do Vini → staging/PR ║
                                      ║   · falhas de método → proposta de ║
                                      ║     regra nova em 04-regras        ║
                                      ║   · correções a montante → Terrenos║
                                      ╚════════════════════════════════════╝
```

**As cinco diferenças que importam:**

| | Atual | Alvo |
|---|---|---|
| Escopo de leitura | Whitelist de 11 tipos | Árvore inteira, classificada |
| Capacidades | Nenhuma | Ferramentas com log de chamada |
| Passadas | 1 | N, com critério de parada explícito |
| Memória | Nenhuma | Precedentes + Diário + repo do lançamento |
| Unidade de saída | Texto | **Afirmação com evidência** — o texto é renderizado dela |

---

## 4. Arquitetura recomendada

### 4.1 Princípio organizador: o Livro de Evidências

Toda a arquitetura gira em torno de uma decisão: **o parecer não é o artefato central; o Livro de
Evidências é.** O parecer é uma renderização dele.

Isso soa abstrato mas resolve, de uma vez, seis dos dez problemas:

| Problema | Como o Livro resolve |
|---|---|
| P5 rastreabilidade | Impossível existir afirmação sem evidência — é campo obrigatório do schema |
| P6 saber que falta | `estado = lacuna` é um estado de primeira classe, não uma frase no texto |
| P7 investigação | Lacuna aberta **é** a fila de trabalho do Investigador |
| P8 contestação | O humano contesta um `id` — o sistema sabe exatamente o que reabrir |
| P1 reexecução | Diff entre Livros de duas rodadas = o changelog que a Rachel pediu |
| P9 aprendizado | Afirmação confirmada tem os campos que a linha granular exige |

**Schema da Afirmação:**

```python
Afirmacao:
  id: str                       # "AF-014" — endereçável na contestação
  disciplina: str               # taxonomia do Vini (engine/schema.py)
  texto: str                    # "A área da União no cadastro SPU é 6.473 m²"
  tipo: "fato" | "inferencia" | "precedente" | "hipotese" | "lacuna"
  confianca: "alta" | "media" | "baixa"
  evidencias: [Evidencia]       # >= 1 obrigatório, exceto para tipo=lacuna
  regra: str | None             # "R4" — qual regra produziu
  premissa_normativa: str|None  # "DL 9.760/1946 art. 2º (preamar-média 1831)"  [R10]
  depende_de: [str]             # ids — é isto que define o subgrafo a reabrir
  contestacoes: [Contestacao]
  estado: "aberta" | "confirmada" | "refutada" | "indeterminada"
  severidade: "OK" | "Atencao" | "Critico" | None

Evidencia:
  origem: "documento_emp" | "base_historica" | "diario" | "repo_lancamento"
        | "fonte_externa" | "legislacao" | "humano"
  ref: str                      # file_id · id da linha granular · âncora do Diário · URL
  link: str
  trecho: str                   # a citação literal — não o nome do arquivo
  localizacao: str              # "p. 4" · "camada MCZ_LPM_TM" · "00:41:27 da reunião"
  data_do_documento: str
  fonte_declarada_pelo_doc: str | None   # ⚠️ None ⇒ dispara R10
```

O campo `fonte_declarada_pelo_doc = None` é o que transforma o teste do Vinícius (*"não cita
fonte, o cara tirou da cabeça dele"*) em verificação automática.

O campo `depende_de` é o que torna a contestação barata: contestar AF-014 reabre AF-014 e seus
dependentes, não a auditoria inteira.

### 4.2 Camadas

```
┌───────────────────────────────────────────────────────────────────────┐
│ INTERFACES  (finas, intercambiáveis — nenhuma contém lógica)          │
│   CLI · API REST · Painel web · Skill Claude Code · cron              │
└───────────────────────────────┬───────────────────────────────────────┘
                                ▼
┌───────────────────────────────────────────────────────────────────────┐
│ ORQUESTRAÇÃO                                                          │
│   Sessão de Auditoria (persistente, com turnos)                       │
│   Loop investigativo · critério de parada · roteamento de agentes     │
└───────────────────────────────┬───────────────────────────────────────┘
                                ▼
┌───────────────────────────────────────────────────────────────────────┐
│ AGENTES                                                               │
│   Cartógrafo · Leitores(7) · Historiador · Cronista · Investigador ·  │
│   Calibrador · Contraditor · Redator · Curador                        │
└───────────────────────────────┬───────────────────────────────────────┘
                                ▼
┌───────────────────────────────────────────────────────────────────────┐
│ LIVRO DE EVIDÊNCIAS  (estado versionado da auditoria)                 │
│   + Motor de Regras R1–R10 (determinístico onde der)                  │
└───────────────────────────────┬───────────────────────────────────────┘
                                ▼
┌───────────────────────────────────────────────────────────────────────┐
│ FERRAMENTAS  (§7 — toda chamada é registrada como evidência)          │
└───────────────────────────────┬───────────────────────────────────────┘
                                ▼
┌───────────────────────────────────────────────────────────────────────┐
│ FONTES                                                                │
│  Drive · BC(Nekt/Sheets) · Diário(repo) · Repo do lançamento ·        │
│  SPU/SPUNET · Legislação · Web · Jurídico                             │
└───────────────────────────────────────────────────────────────────────┘
```

### 4.3 Decisões de arquitetura, com a razão

| # | Decisão | Por quê |
|---|---|---|
| D1 | **Núcleo é biblioteca Python pura.** FastAPI vira um *cliente* do núcleo, não o núcleo | *"ele consegue rodar tudo isso pelo terminal ou pelo próprio aplicativo"* (26:32). Hoje a lógica está dentro do handler HTTP ([main.py:127](../app/main.py#L127)) — inteiramente inacessível ao terminal e à skill |
| D2 | **Estado em disco/DB, não em memória** | `_RESULTS` morre no restart. Uma sessão de contestação pode durar dias |
| D3 | **Auditoria é job assíncrono; painel faz polling** | Com loop + ferramentas, uma DD passa de ~1 min para 5–20 min. Um `POST` síncrono estoura timeout do proxy |
| D4 | **Regras determinísticas em Python, julgamento no modelo** | R1 (comparar áreas, gatilho de 3%) é aritmética — deve ser código testável, não inferência. R3.a (incentivos excludentes) exige leitura de nota jurídica — é do modelo. Hoje R1 é feita pelo modelo, o que é caro e não reprodutível |
| D5 | **Uma chamada por disciplina, não uma por auditoria** | Contorna o teto de 8k tokens, permite paralelismo, e o prompt caching do playbook continua funcionando (o system prompt é comum) |
| D6 | **Cache de extração ≠ cache de conclusão** | Reler um PDF de 40 MB que não mudou é desperdício; reutilizar a *conclusão* é o bug P1. Cachear texto extraído por `file_id+modifiedTime`; **nunca** cachear afirmação |
| D7 | **Modelos por tarefa** | `claude-opus-5` para auditoria, refutação e síntese; modelo menor para classificar arquivo e extrair campo. O benchmark do repo do Vini já adota essa lógica |
| D8 | **Painel = superfície de contestação** | Justifica manter o painel sem violar D1 (I1 + P10) |
| D9 | **Sem escrita automática na base do Vini** | Acesso é read-only; ingestão é papel dele. Saída vai para staging + PR |

---

## 5. Componentes necessários

| # | Componente | Substitui | Esforço | Notas |
|---|---|---|---|---|
| C1 | **Livro de Evidências** — schema, persistência, versionamento, diff | — | M | O componente central. Tudo depende dele |
| C2 | **Cartógrafo do Drive** — árvore completa, classificação, manifest+diff | `locator.SOURCES` | M | Reaproveitar `engine/drive_utils.py` e a lógica de manifest do repo do Vini, que já resolveu isso |
| C3 | **Motor de Regras R1–R10** — determinístico onde possível, com testes | prompt monolítico | M | R1/R2/R5 viram código puro. Cada regra declara os inputs de que precisa → é isto que gera a lista de lacunas automaticamente |
| C4 | **Orquestrador de Sessão** — turnos, loop, parada, contestação | — | G | O maior item. É o coração do I1/P8 |
| C5 | **Camada de Ferramentas** — registro, execução, log-como-evidência | — | M | §7 |
| C6 | **Recuperador de Precedentes** — multi-critério + geográfico | — | M | §10. Bloqueado por Patacho (§15) |
| C7 | **Conector do Diário** | — | **P** | Ler markdown de um repo Git. Melhor relação valor/esforço do projeto inteiro |
| C8 | **Conector do repo do lançamento** | — | M | ⚠️ Depende de o repo existir (§16) |
| C9 | **Redator** — renderiza do Livro para MD/DOCX/GDoc/XLSX | `docs_writer` | P | Aproveitar quase tudo do atual; mudar a entrada |
| C10 | **Curador** — achados → linhas granulares + propostas de regra | — | M | §11 |
| C11 | **Painel v2** — contestação, lacunas, changelog | `static/` | M | Depois de C1–C4 |
| C12 | **Registro de execuções** — quem rodou, quando, o que mudou, custo | — | P | Sem isto não há como calibrar nem cobrar |

*P = pequeno (dias) · M = médio (1–2 semanas) · G = grande (3+ semanas), em regime de trabalho parcial.*

---

## 6. Agentes necessários

Cada agente tem **entrada, saída e limite** explícitos. Nenhum escreve prosa livre no parecer —
todos escrevem no Livro. O Redator é o único que produz texto para humano.

| Agente | Entrada | Saída | Limite (o que NÃO faz) |
|---|---|---|---|
| **Cartógrafo** | folder_id | Inventário classificado + Perfil do Caso + diff | Não interpreta conteúdo |
| **Leitor: jurídico-cartorial** | Matrícula, CND SPU, ônus, **resultado da DD Jurídica** ⚠️ I7 | Afirmações: área, cadeia, regime, ônus | Não emite exigência jurídica — consome a do jurídico |
| **Leitor: topografia** | Prancha, DXF/DWG, memorial | Área real, cotas, **fonte e premissa de cada linha** [R10] | Não conclui dominialidade sozinho |
| **Leitor: ambiental** | EVA, consulta ambiental, licenças | APP, UC, supressão, condicionantes, validade | — |
| **Leitor: urbanístico** | Viabilidade Construtiva, PDM, EP | TO/CA/TP/recuos/gabarito, incentivos, exclusões | Nunca cita lei de memória — só de texto legal recuperado |
| **Leitor: geotécnico** | Sondagem, fundação, estrutura | Perfil, NA, fundação recomendada, custo | — |
| **Leitor: incêndio** | EP, estrutura, base CBMSC | Altura, grupo/classe, tipo de escada, custo | Risco de custo/prazo — não conformidade completa |
| **Leitor: negócio** | Proposta/CCV, log de assinatura | Preço, área considerada, assinaturas, prazos | — |
| **Historiador** | Perfil do Caso | Precedentes rankeados com link | **Precedente nunca vira fato sobre este terreno** |
| **Cronista** | emp_id | Riscos/decisões do Diário + análises do repo | Não decide — traz preocupação como pergunta |
| **Investigador** | Lacunas + hipóteses | Evidência nova, ou **pedido ao humano** | ⚠️ Nunca preenche lacuna com plausibilidade |
| **Calibrador de Entorno** | Achados críticos + geografia | "há precedente construído sob esta mesma restrição?" | Não absolve o risco — abre hipótese [I5] |
| **Contraditor** | Afirmações críticas | Veredito: confirmada / refutada / indeterminada | Prompt **adversarial** — tarefa é derrubar, não concordar |
| **Redator** | Livro | Parecer, achados, lacunas, perguntas, changelog | **Não pode afirmar o que não está no Livro** |
| **Curador** | Livro **aceito pelo humano** | Linhas granulares + propostas de regra | Só roda pós-aceite. Nunca escreve na base do Vini |

Dois comentários sobre escolhas que podem parecer excessivas:

**O Contraditor não é luxo.** O caso do São Miguel foi resolvido por refutação, não por leitura:
a prancha da MCZ estava internamente coerente, com 1,2 cm de divergência entre 15 arestas — um
levantamento metricamente muito bom. O erro estava na **premissa** (LPM atual vs. preamar 1831),
e só apareceu quando alguém perguntou *"de onde veio essa linha?"*. Um leitor cuidadoso teria
validado o documento. Foi preciso um refutador.

**O Calibrador é o contrapeso do sistema.** Todas as regras R1–R9 procuram problema; nada
pergunta se o problema está superdimensionado. Rachel diz que isso já custou terreno (*"às vezes
a gente tá até perdendo o terreno nesse sentido"*, 10:21). Sem esse agente, o Auditor tem viés
estrutural para o NO-GO, e o viés não aparece em nenhuma métrica.

---

## 7. Ferramentas necessárias

Este é o capítulo que hoje é **um conjunto vazio**. Cada ferramenta: assinatura, o que devolve,
e o quanto dá para automatizar honestamente.

### Drive
| Ferramenta | Devolve | Status |
|---|---|---|
| `drive.arvore(folder_id, profundidade=∞)` | Árvore inteira com id/nome/mime/modifiedTime/link | ✅ trivial |
| `drive.ler(file_id, paginas?)` | Texto/PDF nativo; OCR quando escaneado | ✅ `extract_text.py` do Vini já faz, inclusive OCR via cópia→Doc |
| `drive.buscar(query, escopo)` | Busca dirigida por nome/conteúdo | ✅ |
| `drive.diff(folder_id, manifest)` | Novos / alterados / removidos | ✅ padrão já implementado no engine do Vini |

### Base histórica
| Ferramenta | Devolve | Status |
|---|---|---|
| `bc.sintese(filtros)` | Sínteses por emp/disciplina/categoria/cidade/UF | ✅ Nekt `nekt_operacional_silver.szi_dd_tecnica_sintese` no ar |
| `bc.granulares(linhas_ref \| filtro)` | Linhas com `resumo`, `desfecho`, `link` | ✅ |
| `bc.vizinhos(lat, lon, raio_km)` | Empreendimentos por distância | ⚠️ **falta a coluna de coordenadas** — hoje só há `cidade`/`uf`. Requisito de I3 |
| `bc.negativos(disciplina, escopo)` | Só `categoria ∈ {erro, gargalo}` | ✅ canal separado — §10 |

### Diário e repo do lançamento
| Ferramenta | Devolve | Status |
|---|---|---|
| `diario.riscos(emp_id)` / `diario.decisoes(emp_id)` | Eventos com data, fonte, link, **âncora** | ✅ ler markdown de `diarios/<emp_id>-*.md`. **Barato e de alto valor** |
| `lancamento.buscar(emp_id, query)` | Análises anteriores e o raciocínio delas | ❌ repo não existe (§16) |

### Externas
| Ferramenta | Devolve | Status |
|---|---|---|
| `spu.camadas(bbox)` | Shapefiles LPM/LTM/terreno de marinha **+ atributos de homologação por trecho** | ✅ **GeoPortal SPUNET funciona** — canal validado no 12235 |
| `spu.cadastro(rip)` | Área da União, natureza, situação de ocupação | ❌ **login gov.br Bronze+ e reCAPTCHA** → handoff humano obrigatório |
| `spu.financeiro(rip)` | Taxa de ocupação → VDP → laudêmio | ❌ idem |
| `geo.confronto(poligono, camada)` | Interseções, áreas por zona, larguras, distâncias | ✅ técnica já validada — parsing de OCGs do PDF CAD + georreferenciamento por Procrustes, resíduo de 1,4 cm no MCZ. **Deve virar ferramenta, não script de sessão** |
| `legislacao.vigente(municipio, tema)` | Texto legal + vigência + data de verificação | ⚠️ Floripa: repo MVP. **Resto do Brasil: lacuna aberta** (20:46 — *"para Milagres ela não vai ter"*) |
| `web.buscar(query)` | Resultados com fonte e data | ✅ com allowlist |
| `juridico.dd(emp_id)` | Resultado da DD Jurídica como parâmetro | ❓ depende de I7 e de haver um formato de entrega |

### Regra que vale para todas

**Toda chamada de ferramenta gera uma Evidência com timestamp e parâmetros.** Isso é o que
permite ao Investigador saber o que já tentou (critério de parada), ao Contraditor saber em que
se apoiar, e ao humano auditar o caminho — que é o que o Vinícius fez manualmente em 35:38–41:57.

⚠️ **E uma regra de honestidade:** ferramenta que falha **não pode degradar em silêncio para
inferência**. Se `spu.cadastro` exige login, o resultado é `PedidoAoHumano("preciso da consulta
de dados cadastrais do RIP 2873.0100022-91 no portal SPU — exige login gov.br; sem ela não
consigo fechar a área da União nem estimar laudêmio")`. Não é uma estimativa com ressalva.

---

## 8. Fluxo RAG recomendado

### 8.1 A decisão central: não fazer RAG vetorial ingênuo

A tentação natural é jogar tudo (5.005 linhas granulares + Diários + documentos) num vector
store e buscar por similaridade. **É a arquitetura errada aqui**, por três razões concretas:

1. **A base já está estruturada e destilada.** `sintese` e `aprendizados` têm `emp_id`,
   `disciplina`, `categoria`, `cidade`, `uf`, `tema` — campos que respondem à maioria das
   perguntas com um filtro, de forma exata e barata. Embutir isso em texto e recuperar por
   cosseno é *perder* informação que já foi paga.
2. **A pergunta certa raramente é semântica.** "Sondagem do empreendimento mais próximo" é
   geográfica. "Exigência do CBMSC em apart-hotel" é `disciplina=incêndio ∧ produto=apart-hotel`.
   "O que deu errado" é `categoria ∈ {erro, gargalo}`. Nenhuma dessas é um problema de embedding.
3. **A diretriz do projeto já é essa.** `10-consulta-a-base-historica.md`: *"Não leia 50 projetos
   a cada análise: consulte a base leve, escolha os ~3 empreendimentos mais compatíveis e
   aprofunde apenas neles."* É literalmente o diagnóstico da Tati em `CONTEXTO.md`.

O padrão certo é **híbrido, estruturado primeiro, semântico por último**.

### 8.2 Os quatro níveis

```
NÍVEL 0 · ROTEAMENTO POR FATOS  (determinístico, custo ~zero)
   Perfil do Caso → filtro estruturado sobre `sintese`
   ex.: São Miguel → uf=AL ∧ disciplina∈{jurídico-cartorial, ambiental}
                     ∧ flag=marinha ∧ produto=apart-hotel
   ⇒ conjunto candidato de empreendimentos e sínteses

NÍVEL 1 · RANQUEAMENTO MULTI-CRITÉRIO  (código, não modelo)
   score(precedente) = Σ pesos, VARIÁVEIS POR DISCIPLINA (§10)
   ⇒ top-3 empreendimentos + o canal de negativos (sempre)

NÍVEL 2 · SEMÂNTICO, DENTRO DO ESCOPO JÁ FILTRADO
   embeddings SOMENTE sobre as granulares dos selecionados
   + a mesma disciplina em toda a base
   chunk = a linha granular (já é uma unidade destilada, ~1 evento)
   embed  = resumo + desfecho + tema
   ⇒ 10–20 linhas relevantes

NÍVEL 3 · DOCUMENTO ORIGINAL
   só para as linhas que o agente decidiu usar → coluna `link` → leitura nativa
   ⇒ a citação literal que vai para a Evidência
```

Custo por auditoria: níveis 0–1 são consultas SQL/Sheets. Nível 2 roda sobre dezenas de linhas,
não milhares. Nível 3 abre 3–8 documentos, não 400.

### 8.3 Regras de recuperação

- **Canal de negativos sempre ativo.** `categoria ∈ {erro, gargalo}` é recuperado
  **separadamente e sem competir por ranking** com o resto. Motivo: é o sinal mais valioso e é
  minoria numérica — num ranking único ele é diluído por dezenas de linhas de
  `conhecimento-geral`. Decisão do Vini de manter perdidos/cancelados na fila é exatamente por isso.
- **Legislação NUNCA vem do vector store.** É a regra que atravessa todo o projeto: *nunca citar
  lei de memória*. Legislação é sempre `legislacao.vigente()` sobre texto primário, com data de
  verificação registrada na Evidência. Um embedding de lei revogada não tem como se autodenunciar.
- **Precedente entra no Livro como `tipo=precedente`, nunca `tipo=fato`.** Formalização da regra
  já escrita em `10-consulta-a-base-historica.md`: *"Precedente não é prova."*
- **Toda linha recuperada carrega `emp_id` e `link` até o parecer.** Sem isso, o output vira
  "casos semelhantes indicam que..." — genérico, exatamente o que a Tati diagnosticou como o
  problema original.

### 8.4 O formato de saída — narrativa não basta, tem que CRUZAR

> **Revisão de 30/07.** A primeira versão desta seção previa apenas um bloco narrativo de
> precedente, numa seção própria do parecer. **É insuficiente**, e a crítica foi direta:
> um achado dizia *"verba de fundação em valor padrão (~R$ 790 mil), a confirmar após
> sondagem"* e parava aí — quando já existe sondagem feita em empreendimento próximo.
> Precedente numa aba e achado em outra obriga quem lê a fazer o join de cabeça, **e o
> valor está no join.**

O formato correto tem três partes, e as três ficam **dentro do achado**:

**1. O quadro comparativo — mesmo parâmetro, lado a lado.**

| Parâmetro | Este caso | Patacho (38 km) | Japaratinga (17 km) | O que significa aqui |
|---|---|---|---|---|
| Sondagem realizada | **❌ não realizada** | 6 furos | 4 furos | risco geotécnico DESCONHECIDO, não baixo |
| Perfil do subsolo | **—** | areia + turfa | areia fofa até 6 m | define o tipo de fundação |
| Nível d'água | **—** | 0,80 m | 1,20 m | define necessidade de rebaixamento |
| Fundação adotada | **verba padrão** | estaca hélice | estaca hélice | os dois exigiram fundação profunda |
| Custo da fundação | **R$ 790 mil previsto** | R$ 1,9 mi | R$ 1,4 mi | verba provavelmente subdimensionada |

Regras do quadro: a coluna do caso nomeia **o empreendimento E a relação** — a distância é
o que justifica a comparação; `este caso` pode ser "❌ não realizada", e é justamente aí
que o cruzamento vale mais; a última coluna diz o que a diferença **significa aqui**, não
repete o número.

**2. A premissa de trabalho** — o que transforma "pendente" em acionável:

> → Os dois casos comparáveis do litoral de AL exigiram fundação profunda, a 1,8–2,4× a
> verba padrão. **Provisionar fundação profunda até a sondagem sair.**
> *(analogia · confiança média)*

**3. A ressalva** — nunca omitida:

> ⚠️ Analogia geográfica, não medição. **NÃO substitui a sondagem** (AGS, contratada).

**Por que a premissa de trabalho não viola "precedente não é prova":** ela sai como
`tipo=hipotese`, com confiança explícita e ressalva anexada. A diferença entre isso e um
palpite é que aqui o raciocínio inteiro está visível — dados de origem, distância,
implicação e limite. O que se proíbe é a inferência silenciosa, não a analogia declarada.

**Auto-cobrança.** A regra `R-CRUZAMENTO` (`regras.py`) verifica ao fim da auditoria se
sobrou achado crítico ou lacuna **sem** comparativo, havendo precedente recuperado. Se
sobrou, vira um achado sobre o próprio parecer — é falha do Auditor, não do terreno.

**A forma narrativa continua valendo** para o que não é parametrizável (uma exigência de
órgão, um desfecho processual):

```markdown
> **Precedente — [Patacho Spot] (Maragogi/AL · 38 km · disciplina: jurídico-cartorial)**
>
> Lá, a área de marinha apurada foi **maior** do que a estimada na aquisição, e o terreno
> acabou perdido.
>
> **Aplicação a este caso:** o São Miguel apresenta a mesma assinatura — divergência entre a
> área da União no cadastro (6.473 m²) e a apurada por geometria (6.953 m²), 7,4% a mais.
> Ponto de atenção, não conclusão.
>
> Fonte: `aprendizados` linha #A-2291 · [documento no Drive](…) · extraído em 06/07/2026
```

Três elementos obrigatórios: **o que aconteceu lá**, **por que se aplica aqui**, **link
verificável**. E o desfecho ("acabou perdido") é o que dá peso — por isso o `desfecho` é coluna
do schema do Vini e precisa sobreviver até o parecer.

---

## 9. Estratégia de atualização automática

### 9.1 A regra de ouro

**Nenhuma conclusão é reutilizada. Nunca.** Toda execução reconstrói o Livro de Evidências do
zero a partir das fontes. O que se reutiliza é apenas **extração de texto de documento não
alterado** — que é caro e imutável.

Esta é a distinção que resolve P1 sem tornar cada rodada proibitivamente cara.

### 9.2 Mecânica

```
1. drive.diff(folder_id, manifest_anterior)
      → novos · alterados · removidos · inalterados

2. Para cada documento:
      inalterado → reaproveita TEXTO do cache (chave: file_id + modifiedTime)
      novo/alterado → extrai de novo (e invalida o texto antigo)
      removido → marca as Evidências que o citavam como ÓRFÃS
                 → toda Afirmação apoiada em evidência órfã volta a `aberta`

3. Reconstrói o Livro: todos os leitores, todas as regras, do zero

4. Diff(Livro_novo, Livro_anterior) → CHANGELOG

5. Grava versão nova. NUNCA sobrescreve a anterior
```

O passo 2/removido merece atenção: documento que **some** do Drive é tão significativo quanto
documento que aparece, e nenhum sistema costuma tratar isso.

### 9.3 O changelog é a entrega, não um efeito colateral

É o que a Rachel pediu em 15:02 — *"levantamento topográfico pendente, tá ausente, só que a
gente teve atualização"*. O valor da segunda rodada não é o parecer novo; é saber o que mudou.

```markdown
## Mudanças desde a auditoria de 27/07/2026

### Documentos
+ `MCZ_PC_ORIGAMI-SEAZONE.pdf` (23/07) — Levantamento Topográfico
+ `06 Confronto SPU/` — 4 arquivos novos (DXF, shapefiles SPUNET)
~ `EP-ARQ-DCT-GER-XXX` R03 → R04 (29/07)

### Achados
🔴 NOVO   AF-021 · A área da União (6.473 m² cadastro / 6.953 m² geometria)
                   corresponde a 75–80% do lote
🟢 FECHADO AF-004 · "Levantamento topográfico ausente" — recebido em 23/07
🔴 AGRAVADO AF-011 · Afastamento de 50 m: era hipótese, agora é inviabilidade
                   demonstrada (97% das seções têm largura < 50 m)

### Lacunas
− FECHADA  Demarcação SPU — homologada em 05/03/2004, atributo lido no SPUNET
+ ABERTA   VDP não apurado — bloqueia laudêmio e taxa de ocupação
           ⚠️ requer login gov.br (§7)
```

### 9.4 Gatilhos

| Gatilho | Quando | Notas |
|---|---|---|
| Manual | Botão / CLI / skill | O que existe hoje |
| **Agendado** | Diário, por empreendimento ativo | Modelo já provado: a tarefa agendada do Windows do repo do Vini roda às 14:00 com catch-up |
| **Evento do Drive** | Push notification em mudança de pasta | O `diario-lancamentos` já tem `eventos-drive` desenhado — reaproveitar |
| **Evento do Diário** | Risco novo registrado que toca o empreendimento | Fecha o ciclo do item 13 |

⚠️ **Consertar antes de agendar:** o monitor atual nunca marca ninguém como elegível
(§1.4-A). E o critério `elegivel = completo ∧ não tem DD` é o critério errado para o modelo novo
— no modelo novo, **auditoria incompleta é uma saída válida** (com lacunas explícitas). O
critério passa a ser "mudou algo desde a última rodada".

---

## 10. Estratégia de comparação entre empreendimentos

### 10.1 Similaridade é dependente de disciplina

O erro a evitar é um único score de "empreendimento parecido". O que torna um precedente
relevante muda conforme a pergunta:

| Disciplina | O que prediz | Chave de recuperação dominante |
|---|---|---|
| Geotécnico / sondagem | O subsolo é do lugar | **Distância geográfica** (raio de km) |
| Ambiental / licenciamento | Mesmo órgão, mesmo rito | **Município**, depois estado |
| Urbanístico / alvará | Mesma lei, mesmo zoneamento | **Município + zoneamento** |
| Jurídico-cartorial / marinha | Mesmo regime, mesma demarcação | **Regime dominial + trecho de demarcação** |
| Incêndio | Mesma classificação de ocupação | **Produto + altura**, depois UF (é norma estadual) |
| Negócio / instrumento | Mesma estrutura de aquisição | **Instrumento + porte** |

Por isso o Historiador não faz *uma* busca — faz uma por disciplina ativa, com pesos próprios.

### 10.2 Função de score

```
score(candidato, disciplina) =
      w_geo(disc)      · f_distancia(km)          # decaimento: 1/(1+km/10)
    + w_cidade(disc)   · [mesma cidade]
    + w_uf(disc)       · [mesmo estado]
    + w_regime(disc)   · [mesmo regime dominial]  # marinha/ocupação/aforamento/alodial
    + w_produto(disc)  · [mesmo produto]          # Spot / apart-hotel / retrofit
    + w_porte(disc)    · f_similaridade(área, nº UH)
    + w_orgao(disc)    · [mesmo órgão licenciador]
    + BÔNUS_DESFECHO   · [desfecho ∈ {perdido, cancelado, embargado}]
```

O `BÔNUS_DESFECHO` é deliberado: casos que deram errado são sub-representados numericamente e
sobre-representados em valor. É a formalização do *"são os que mais trazem aprendizados"*.

### 10.3 O que o Auditor deve dizer

Três modos de saída, e o terceiro é o que ninguém constrói:

1. **Precedente positivo** — "aconteceu isto lá, atenção aqui" (formato de §8.4).
2. **Ausência de precedente** — *"não há precedente na base para terreno de marinha com acrescido
   em AL; o mais próximo é Japaratinga (0584), sem componente dominial de União."* Declarar a
   ausência é informação. Hoje o silêncio é ambíguo: pode ser "não há" ou "não olhei".
3. ⚠️ **Contraprecedente (o Calibrador)** — *"há 3 empreendimentos num raio de 2 km construídos
   sobre área de marinha homologada; a restrição não impediu a operação deles. Hipótese: usam
   incorporação prévia (relato do Silas) ou aforamento. Investigar antes de tratar como
   impeditivo."*

O modo 3 é a resposta direta ao *"não entra na minha cabeça"* do Vinícius (11:13). O sistema
atual jamais o produziria — e é o modo que protege contra descartar terreno bom.

### 10.4 ⚠️ Dependência bloqueante

A tabela abaixo é o estado real da base, e ela determina o que a comparação consegue fazer hoje:

| Empreendimento | emp_id | Na base? | Relevância para os casos ativos |
|---|---|---|---|
| Campeche Spot | 2595 | ✅ 1.798 linhas | Alta para Floripa |
| Jurerê Spot | 6665 | ✅ 735 | Alta para Floripa |
| Japaratinga | 0584 | ✅ 945 | **Alta para AL / São Miguel** |
| Jurerê Beach | 2811 | ✅ 1.527 | Alta para Floripa |
| **Patacho** | — | ❌ **fila pausada** | **A comparação pedida na reunião, duas vezes** |
| São Miguel | 12235 | ❌ base local pronta, não ingerida | 18 granulares + 14 sínteses prontas em `base-conhecimento-sao-miguel-12235/` |
| Novo Campeche III | 10045 | ❌ | Reauditoria feita na PR #2 |
| + 66 outros | — | ❌ fila pausada | |

Três caminhos, e recomendo o segundo:

1. Pedir ao Vini para retomar a fila → melhor resultado, prazo fora do seu controle.
2. **Pedir extração pontual só do Patacho** → escopo mínimo, justificativa forte (é o caso de
   referência do 12235), desbloqueia a demonstração. **Recomendado.**
3. Extração local no schema do Vini + PR → você já provou que sabe fazer (o 12235 está pronto
   nesse formato), mas gasta seu tempo em trabalho que é dele e a ingestão continua dependendo
   do OK dele.

---

## 11. Estratégia de aprendizado contínuo

### 11.1 Dois canais, nunca misturados

| | Canal A — Memória de caso | Canal B — Correção de método |
|---|---|---|
| Pergunta | "o que aconteceu?" | "como auditar melhor?" |
| Artefato | Linha granular em `aprendizados` | Regra em `04-regras-de-auditoria.md` |
| Destino | Base do Vini (via PR) | Este repositório |
| Frequência | Toda DD | Quando uma falha se repete |
| Exemplo | "12235: demarcação de 2004 colocou 80% sob a União" | "R10: documento sem fonte declarada é achado" |

A PR #2 é o Canal B rodando manualmente — R3.a, R3.b, R6.a, R7, R8, R9 nasceram todas de falhas
concretas da reauditoria. O objetivo é tornar isso rotina.

### 11.2 Gatilho: aceite humano, não geração

⚠️ Ponto crítico de projeto: **nada entra na base porque o Auditor concluiu.** Entra porque um
humano aceitou a conclusão. Um sistema que aprende com as próprias saídas não validadas amplifica
os próprios erros — e este produz conclusões críticas sobre compras de milhões.

```
Parecer gerado
   → Rachel revisa e contesta (o "jogo")
   → Afirmações em estado `confirmada` E marcadas como aceitas
   → SÓ ELAS vão para o Curador
```

Isso é também o que casa com o modelo do Vini: validação **em bloco** (decisão de 04/07), não
linha a linha.

### 11.3 Saída do Canal A

Uma Afirmação confirmada já carrega quase todos os campos que `engine/schema.py` exige:

| Coluna do schema | Vem de |
|---|---|
| `empreendimento`, `emp_id`, `cidade`, `uf` | Perfil do Caso |
| `disciplina` | Campo da Afirmação (taxonomia fixa) |
| `categoria` | Derivada: achado crítico resolvido → `gargalo`; exigência de órgão → `exigência-de-órgão`; erro nosso → `erro` |
| `tema` | Aberto — do achado |
| `resumo` | Texto da Afirmação |
| `desfecho` | ⚠️ **Só existe depois** — exige um segundo momento (§11.5) |
| `documento`, `link`, `data_doc` | Da Evidência principal |
| `fonte_extracao` | `"auditor-dd v2 · sessão <id>"` |

Fluxo: gerar CSV no schema exato → `staging/base-conhecimento/<emp_id>/` neste repo → PR ao repo
do Vini, ou entrega para ele ingerir. **Nunca escrita direta** (read-only).

### 11.4 Saída do Canal B

Quando o Contraditor derruba uma afirmação, ou o humano corrige o agente, a pergunta seguinte é:
*qual regra teria pego isso?*

Exemplo real, do São Miguel: o agente aceitou a prancha da MCZ como fonte de dominialidade. O
humano apontou a premissa errada. A regra que faltava é **R10**. Ela deveria nascer
automaticamente como uma **proposta** — nunca aplicada sozinha:

```markdown
## Proposta de regra — R10 (gerada em 29/07/2026, sessão #a3f1)
**Origem:** AF-007 refutada por contestação humana no [12235] São Miguel
**Falha:** o levantamento estava metricamente correto (resíduo de 1,4 cm em 15 arestas)
mas apoiado na LPM atual, quando DL 9.760/1946 art. 2º define preamar-média de 1831.
**Regra proposta:** todo dado técnico determinante de terceiro deve declarar fonte e
premissa normativa. Ausência de fonte é achado, independentemente da qualidade da medição.
**Status:** aguardando validação · não aplicada
```

### 11.5 O desfecho é o que falta em todo sistema desses

`desfecho` é a coluna mais valiosa do schema do Vini — *"acabou que lá a gente teve uma área de
marinha maior do que a gente achava"* só vale como precedente porque tem final. E o desfecho
**não existe no momento do parecer**. Ele chega meses depois: o alvará saiu ou não, o prazo foi
X, o terreno foi comprado ou perdido.

Sem um mecanismo para voltar e fechar o desfecho, a base acumula previsões sem resultado — o que
a torna incapaz de calibrar. Proposta: cada Afirmação confirmada gera um **item de acompanhamento**
com `desfecho = pendente`, e o Diário (que já observa o dia a dia) ou uma revisão trimestral os
fecha. É baixo custo e é o que diferencia uma base que aprende de um arquivo morto.

### 11.6 Terceiro canal: correção a montante

Do item I4: o Auditor descobriu que o status de homologação da linha é metadado legível e é por
trecho — e que o time de Terrenos não tem essa informação. Isso não vai para a base histórica nem
para as regras. Vai para **outro time**. Vale um tipo de saída próprio: *recomendação de processo*,
endereçada a quem opera a etapa anterior.

---

## 12. Estratégia de geração de parecer

### 12.1 O Redator não escreve — ele renderiza

Regra dura: **o Redator só pode afirmar o que está no Livro.** Se não há Afirmação, não há frase.
Isso mata a categoria inteira de erro em que o modelo escreve prosa fluente e plausível sobre
algo que não verificou.

Consequência prática: o parecer fica **mais curto e mais desigual** — denso onde há evidência,
explicitamente vazio onde não há. Isso é o comportamento correto, e é uma mudança visível de
qualidade percebida que vale avisar ao time antes de acontecer.

### 12.2 Estrutura

Mantém o template oficial (`06-estrutura-do-parecer.md`, `templates/parecer-tecnico.md`) —
Rachel confirma que o Jurerê ficou fiel: *"ele montou essa DD técnica igual eu faço"* (29:31).
Não mexer no que funciona. Adicionar **três seções novas**:

| Seção nova | Conteúdo | Resolve |
|---|---|---|
| **Lacunas e o que falta** | O que impede a conclusão, o que é preciso e de quem depende | P6 |
| **Precedentes consultados** | Casos, por que foram escolhidos, e a **declaração de ausência** quando não há | P3 |
| **Mudanças desde a rodada anterior** | Changelog (§9.3) | P1 |

E, na trilha de evidências, cada achado passa a exibir: fonte, **trecho literal**, localização
(página/camada/timestamp), regra aplicada, e o veredito do Contraditor.

### 12.3 ❓ O conflito do GO / NO-GO

Este é o ponto que **exige decisão sua**, porque três fontes discordam.

**Vinícius, 18:46:**
> *"eu não espero que o Claude traga um GO ou não GO — eu acho que esse não é [o papel]. O que
> eu quero que ele traga é: **existe essa situação, encontrei uma divergência** em relação à área
> de marinha, **encontrei um ponto de atenção**. Qual é o ponto de atenção? Tenho boa parte do
> terreno em regime de ocupação, segundo a SPU a área da União é de 6 mil e tantos metros
> quadrados. **Vocês tiveram um caso parecido no Patacho** (...) então é um ponto de atenção
> para essa nossa análise. É isso que eu espero que ele traga."*

**Rachel, 18:51:** *"Não, que a gente vai decidir."* — concorda.

**Mas o código e o método dizem o contrário:**
- [playbook.py:215](../app/core/playbook.py#L215) — `"recomendacao": "GO|GO COM RESSALVAS|NO-GO"`, campo obrigatório do schema
- `base-conhecimento/06-estrutura-do-parecer.md` — GO / GO COM RESSALVAS / NO GO
- `memory.md` — *"conclusão com go / go com ressalvas / no-go"* como **saída obrigatória**
- A PR #2 entrega justamente uma mudança de recomendação (GO COM RESSALVAS → NO-GO) como o
  resultado principal da reauditoria

**Minha recomendação — separar duas coisas que hoje estão fundidas:**

1. **Exposição técnica** (o Auditor emite): situação, evidência, severidade, precedente, custo e
   prazo estimados das ressalvas, lacunas abertas. Objetivo e rastreável.
2. **Recomendação de negócio** (o humano emite): GO / GO COM RESSALVAS / NO-GO, num campo
   explicitamente marcado como **decisão humana**, com autor e data.

Assim o parecer continua saindo com uma recomendação (o time e a diretoria esperam isso, e a PR
#2 depende disso), mas fica visível quem a assinou. O Auditor deixa de fingir autoridade que o
Vinícius não quer dar a ele, sem que o entregável perca a conclusão que o processo exige.

⚠️ Vale confirmar com a **Caroline** também — ela é a validação final e a lição L6 registra que
o escopo já foi ajustado uma vez por ela.

### 12.4 Superfícies

Uma geração, quatro renderizações — nenhuma privilegiada:

| Superfície | Uso | Nota |
|---|---|---|
| **Word / GDoc** | Entregável oficial | Usar o formato-padrão já definido: Letter, margens 1440/1800, corpo Cambria 11, títulos Calibri, accent `#4F81BD`. É o template do time |
| **Painel** | Revisão e **contestação** | I1 |
| **.xlsx** | Controle por etapa | Já existe, aproveitar |
| **JSON via API / CLI** | Integração, terminal, skill | *"pelo terminal ou pelo próprio aplicativo"* |
| **Markdown no repo do lançamento** | Histórico versionado | Modelo do Diário: *"fica no GitHub em markdown feio, que para a IA é bom, e depois joga para um doc"* (27:12) |

---

## 13. Estratégia de utilização do Diário de Lançamentos

### 13.1 Por que este é o melhor investimento imediato

Ler o Diário é **ler arquivos markdown de um repositório Git**. Sem API, sem credencial, sem
custo de LLM. E o conteúdo é exatamente o que falta ao Auditor: o que o time **sabe e teme**, que
não está em documento nenhum.

Concretamente, o `diarios/12235-sao-miguel-dos-milagres.md` já contém, com link para a fonte:

- suspensão de alvarás no SOUS da Praia do Toque, sem previsão
- recomendação do MPF ao IMA/AL e ao cartório de Porto de Pedras
- risco de embargo mesmo com proposta de acesso público
- sondagem adiada por hóspedes no local, impacto no cronograma
- exigência possível de unidades PCD

Nenhum desses fatos está numa matrícula, num EVA ou numa sondagem. **Todos são materiais para a
DD.** E o Vinícius pediu exatamente isso, em 24:33:

> *"ele deveria estar conectado no Diário de Lançamento (...) para que ele acesse os dados do
> diário. E ele fala assim: 'espera aí, **o pessoal tá bem preocupado com esse negócio aqui de
> suspensão de alvarás — deixa eu dar uma pesquisada no que que é isso**', aí dá um parecer sobre
> isso. Ele precisa estar conectado também no Diário porque ali ele vai captando as nossas
> conversas, as nossas preocupações, e com isso ele vai tirando ações também."*

Note o verbo: **"deixa eu dar uma pesquisada"**. O Diário não é fonte de conclusão — é **fonte de
pergunta**. Preocupação do time vira item de investigação.

### 13.2 Como consumir

O Diário tem estrutura estável e uma âncora por evento:

```html
<!--anc:reuniao:1ul7PyOIGy...:os-alvaras-estao-suspensos-na-praia-do-toque-->
<!--anc:slack:C0BEW322JF5:mpf-orientou-o-ima-al-a-segurar-licencas-ambientais-->
```

Isso permite citar **a frase exata, da reunião exata**, como Evidência rastreável:

```
Evidencia(
  origem = "diario",
  ref    = "anc:slack:C0BEW322JF5:estao-suspensos-novos-alvaras-...",
  link   = "https://seazone-fund.slack.com/archives/C0BEW322JF5/p1784993054200339",
  trecho = "Estão suspensos novos alvarás e os efeitos dos já emitidos no SOUS da
            Praia do Toque, onde fica o terreno 12235.",
  data_do_documento = "2026-07-25",
)
```

### 13.3 Os três papéis do Diário na auditoria

| Papel | Mecânica | Exemplo |
|---|---|---|
| **Gerador de pergunta** | Risco do Diário → lacuna no Livro → fila do Investigador | "suspensão de alvarás" → investigar a decisão municipal de 09/04/2026 e a recomendação do MPF |
| **Corroborador / contraditor** | Confronta a conclusão documental com o vivido | Documento diz licenciamento normal; Diário diz alvarás suspensos ⇒ conflito explícito |
| **Fonte de cronograma real** | Datas efetivas de eventos | Sondagem adiada 2×; o Auditor não deve tratar "sondagem prevista" como "sondagem em curso" |

### 13.4 ⚠️ Um cuidado

O Diário é **fala de reunião e mensagem de Slack** — o material menos confiável de todas as
fontes, e o mais fácil de tratar como fato. A própria reunião mostra por quê: o Silas afirmou
que a liminar do Toque *"vai ser derrubada"*, com informação do secretário de infraestrutura.
É exatamente o mesmo padrão do risco nº 1 da DD do 12235 (orientação verbal sem documento).

Portanto: **evidência de origem `diario` tem teto de confiança `media`** e **nunca sustenta
sozinha uma afirmação de tipo `fato`.** Ela gera pergunta, corrobora, ou contradiz. Não conclui.

### 13.5 Repo do lançamento (o terceiro pilar)

⚠️ Não existe ainda — foi decidido nesta reunião (07:01, 30:47, 31:00). Difere do Diário:

| | Diário | Repo do lançamento |
|---|---|---|
| Origem | Reuniões + Slack, automático | Análises de pessoa+IA, deliberado |
| Conteúdo | O que foi **dito** | O que foi **concluído, e por quê** |
| Granularidade | Resumo | Completo, com raciocínio |
| Quem alimenta | Bot | Rachel, Vini, Andressa, Bianca… |

Para o Auditor é a fonte mais rica que existirá: contém o *raciocínio*, não só o resultado. Mas
depende de o repo ser criado e de haver disciplina de uso — está em §16 como decisão pendente,
e a arquitetura deve funcionar sem ele (degradação graciosa).

---

## 14. Estratégia de rastreabilidade das conclusões

### 14.1 O que muda de fundo

| | Hoje | Alvo |
|---|---|---|
| Unidade | Achado (texto) | **Afirmação com evidência obrigatória** |
| Citação | Link colado por keyword, pós-hoc | Trecho literal declarado por quem afirmou |
| Precisão | Arquivo | **Página / camada / timestamp / linha da base** |
| Cadeia | Inexistente | `depende_de` — grafo completo |
| Fonte externa | Inexistente | Toda chamada de ferramenta é evidência com timestamp |
| Refutação | Inexistente | Veredito do Contraditor anexado |
| Fonte do terceiro | Não verificada | `fonte_declarada_pelo_doc` — R10 |

### 14.2 Os cinco níveis

```
NÍVEL 1 · A afirmação        "A área da União no cadastro SPU é 6.473 m²"
NÍVEL 2 · A evidência        CND SPU / consulta de cadastro · RIP 2873.0100022-91
                             trecho literal · consultado em 29/07/2026
NÍVEL 3 · A regra            R4 (ambiental/dominial) + R10 (fonte declarada)
NÍVEL 4 · A cadeia           AF-021 ← AF-014 (RIP identificado na matrícula)
                                    ← AF-003 (matrícula lida, fl. 2)
NÍVEL 5 · A contestação      Contraditor: "a geometria dá 6.953 m² (+7,4%) —
                             cadastro e geometria divergem" → INDETERMINADA
                             ⇒ lacuna aberta, não conclusão
```

O nível 5 é o que faltava no São Miguel e o que produziu o achado mais importante do caso: as
duas fontes **não batem**, e dizer isso vale mais do que escolher uma.

### 14.3 Rastreabilidade da ausência

Tão importante quanto rastrear o que foi usado é rastrear **o que não foi**. Implementa `R6.b`
de verdade (hoje o código a impede — §1.4-B):

```markdown
### Cobertura documental — [12235] São Miguel
Varridos: 247 arquivos em 38 pastas

✅ Lidos (31) ....... matrícula, CND SPU, MCZ_PC prancha+DXF, EP R04, shapefiles SPUNET…
⏭️ Não aplicáveis (198) ... renders, fotos de visita, atas comerciais…
❌ NÃO LIDOS (18) ... ⚠️ 4 críticos:
     · Certidão de Ônus (Origami) — OCR só retornou a folha de validação ONR
     · Análise PDM — planilha em branco
     · CURVAS_NIVEL-0.5m.dxf — não parseado
     · 2 PDFs escaneados sem OCR
```

*"Existe e não foi lido" tem a mesma severidade de "não existe"* — a regra já está escrita em
`R6.b`. Isto é a interface que a torna executável.

### 14.4 Reprodutibilidade

Cada sessão grava: versão do código, versão do playbook (hash), modelo e parâmetros, manifest do
Drive, consultas feitas à base, chamadas de ferramenta com resposta, e o Livro final. Uma
auditoria de 3 meses atrás deve poder ser reaberta e explicada. Sem isso não há como investigar
um erro, nem defender uma decisão de compra.

### 14.5 Requisitos não-funcionais

| Requisito | Alvo | Nota |
|---|---|---|
| Idioma | pt-BR em toda saída | Já vale |
| Determinismo | Regras aritméticas em código, com teste | D4 |
| Latência | Job assíncrono; painel faz polling | D3 |
| Custo | Prompt caching (já existe) + modelo por tarefa + cache de extração | Loop multiplica chamadas — medir por sessão desde o dia 1 |
| Degradação graciosa | Fonte indisponível ⇒ lacuna declarada, nunca inferência | §7 |
| Offline / demo | Preservar, **com selo visível "DEMO"** | Hoje o demo é indistinguível do real — foi a origem de P1 |
| PII | Dados pessoais de proprietário não vão para repo público nem para a base | Já barrado na prática; formalizar |
| Governança de escrita | Auditor **nunca** escreve na base do Vini | Read-only |
| Autoria da evidência | `origem=humano` registra quem inseriu | I9 — ingestão multi-ator |
| Segurança | Service account, segredos fora do repo, `main` protegida com PR | Padrão já adotado nos dois repos |

---

## 15. Roadmap técnico

Priorizado por **impacto ÷ esforço**, respeitando dependências. Esforço em regime de trabalho
parcial (você tem outras frentes).

### Fase 0 — Destravar (dias) · impacto altíssimo, esforço mínimo

Nada aqui é arquitetura. É consertar o que está quebrado e é barato.

| # | Ação | Impacto | Esforço |
|---|---|---|---|
| 0.1 | **Tirar o app de DEMO em produção** — service account + `ANTHROPIC_API_KEY` no Coolify | 🔴 Máximo — hoje o painel mostra JSON congelado do repo e ninguém percebe | P |
| 0.2 | **Selo visível de modo** — banner "DEMO" quando `demo_mode()` | 🔴 Evita que P1 se repita | XP |
| 0.3 | **Eleger a cópia oficial do app** (a PR #2 registra 3 divergentes) | 🔴 Sem isso, todo trabalho seguinte se perde | P |
| 0.4 | Corrigir `monitor.status_empreendimento` (§1.4-A) | 🟡 Código morto hoje | P |
| 0.5 | `MODEL` → `claude-opus-5`; subir `MAX_TOKENS`; detectar truncamento | 🟡 Qualidade + evita falha silenciosa | XP |
| 0.6 | ❓ **Decidir GO/NO-GO** (§12.3) com Vini e Caroline | 🔴 Bloqueia o schema de saída | — |
| 0.7 | ❓ **Pedir ao Vini a extração do Patacho** (§10.4) | 🔴 Prazo fora do seu controle — pedir hoje | — |

> **Entregável:** o Auditor lê o Drive de verdade em produção, e a comparação com o Patacho está
> encomendada. Sem isto, todas as demais fases operam sobre uma demo.

---

### Fase 1 — Ver tudo e citar direito (1–2 semanas) · a fundação

| # | Ação | Resolve |
|---|---|---|
| 1.1 | **Cartógrafo** — árvore completa, sem whitelist, classificação por arquivo | §1.4-B, R6.b |
| 1.2 | **Livro de Evidências** — schema, persistência, versionamento | Fundação de tudo |
| 1.3 | **Citação declarada pelo modelo** (trecho + página), fim do keyword matching | P5 |
| 1.4 | **R10** — auditar fonte e premissa do documento de terceiro | I2 |
| 1.5 | **Manifest + diff + changelog** entre rodadas | P1 |
| 1.6 | **Seção "Cobertura documental"** no parecer | §14.3 |
| 1.7 | Extrair o núcleo de `main.py` para biblioteca; CLI mínima | D1 |

> **Entregável:** roda o São Miguel e enxerga a pasta `06 Confronto SPU` — que hoje é invisível.
> Rodar duas vezes produz um changelog. **Escolha de sequência:** 1.1 e 1.7 antes de 1.2, porque
> o Livro é mais fácil de desenhar depois de ver o que o Cartógrafo realmente devolve.

---

### Fase 2 — Lembrar (1–2 semanas) · maior impacto percebido

| # | Ação | Resolve |
|---|---|---|
| 2.1 | **Conector do Diário** — ler markdown, riscos/decisões, âncoras | P4, §13 · **melhor valor/esforço do projeto** |
| 2.2 | **Conector da base histórica** — `sintese` + `granulares` via Nekt/Sheets | P3, P4 |
| 2.3 | **Recuperador multi-critério** + canal de negativos | §10 |
| 2.4 | Coordenadas por empreendimento (`bc.vizinhos`) | I3 |
| 2.5 | Bloco de precedente no formato de §8.4 | P3 |
| 2.6 | Declaração explícita de ausência de precedente | §10.3 |

> **Entregável:** o Auditor diz *"encontramos um caso semelhante no Patacho…"* com link. É o
> comportamento que o Vinícius pediu de forma mais insistente, e é onde o valor fica visível para
> quem não lê código. **Sequência:** 2.1 primeiro — é barato e entrega sozinho.

---

### Fase 3 — Investigar (2–3 semanas) · o maior refactor

| # | Ação | Resolve |
|---|---|---|
| 3.1 | **Tool use no motor** — de `messages.create` único para loop com ferramentas | P2, P7 |
| 3.2 | **Leitores por disciplina** em paralelo (contorna o teto de tokens) | D5 |
| 3.3 | **Regras determinísticas** R1/R2/R5 em código testado | D4 |
| 3.4 | **Lacunas como estado** + critério de parada + pedido ao humano | P6 |
| 3.5 | `spu.camadas` via SPUNET (atributos de homologação por trecho) | P2, I4 |
| 3.6 | `geo.confronto` — a técnica de OCG+Procrustes vira ferramenta | §7 |
| 3.7 | ⚠️ Handoff humano para SPU cadastro/financeiro | §7 |

> **Entregável:** RIP encontrado ⇒ SPUNET consultado ⇒ homologação verificada ⇒ confronto
> geométrico calculado ⇒ divergência cadastro×geometria apontada — **sem intervenção**. É o
> caminho que o Vinícius percorreu à mão em 35:38–41:57.

---

### Fase 4 — Contestar (1–2 semanas) · o "jogo"

| # | Ação | Resolve |
|---|---|---|
| 4.1 | **Sessão persistente com turnos** | I1, P8 |
| 4.2 | **Contraditor** adversarial sobre afirmações críticas | §6 |
| 4.3 | **Reabertura de subgrafo** por `depende_de` | I1 |
| 4.4 | **Calibrador de Entorno** | I5 |
| 4.5 | Painel v2 como superfície de contestação | P10, D8 |

> **Entregável:** a Rachel aponta uma afirmação, escreve *"não é bem isso"*, e o Auditor reabre
> só o que depende dela. **Nota de sequência:** 4.5 (painel) só depois de 4.1–4.3 — construir a
> UI antes do modelo de sessão é retrabalho garantido.

---

### Fase 5 — Aprender (1–2 semanas)

| # | Ação | Resolve |
|---|---|---|
| 5.1 | **Curador** — afirmações aceitas → CSV no schema do Vini → staging | P9 |
| 5.2 | Propostas de regra (Canal B) | §11.4 |
| 5.3 | Itens de acompanhamento de **desfecho** | §11.5 |
| 5.4 | ❓ Conector do repo do lançamento | §13.5 |
| 5.5 | Saída de "recomendação de processo" para Terrenos | I4, §11.6 |

---

### Fase 6 — Automatizar

| # | Ação |
|---|---|
| 6.1 | Reexecução agendada por empreendimento ativo (modelo da tarefa do Vini) |
| 6.2 | Gatilho por evento do Drive (reaproveitar `eventos-drive` do Diário) |
| 6.3 | Gatilho por risco novo no Diário |
| 6.4 | Registro de execuções: custo, duração, taxa de contestação por disciplina |

---

### Mapa problema → fase

| Problema | Fase |
|---|---|
| P1 não reexecuta | **0** (demo) + **1** (changelog) |
| P2 fontes externas | **3** (parcial — cadastro SPU exige humano) |
| P3 casos anteriores | **2** ⚠️ bloqueado por Patacho (0.7) |
| P4 conhecimento acumulado | **2** + **5** (repo do lançamento) |
| P5 explicar raciocínio | **1** |
| P6 saber que falta | **3** |
| P7 processo investigativo | **3** |
| P8 iterativo | **4** ⚠️ é diálogo, não autonomia |
| P9 aprender | **5** |
| P10 painel | **1** (núcleo headless) + **4** (painel v2) |

---

### Dependências externas — pedir agora, não na hora de precisar

| # | Dependência | De quem | Bloqueia | Urgência |
|---|---|---|---|---|
| E1 | **Extração do Patacho** na base | **Vini** (fila pausada por decisão dele) | Fase 2 — o pedido central da reunião | 🔴 pedir hoje |
| E2 | Credenciais do Drive + API no Coolify | Você / infra | Fase 0 — **tudo** | 🔴 |
| E3 | Consulta gov.br do cadastro SPU | Humano com conta Bronze+ | Fase 3 (parcial) | 🟡 |
| E4 | Repo por lançamento — criar e definir uso | Vini + time | Fase 5 | 🟡 |
| E5 | Formato de entrega da DD Jurídica | Jurídico | I7 / Fase 1 | 🟡 |
| E6 | Legislação fora de Floripa | A definir | Qualidade fora de SC | 🟢 |
| E7 | Decisão GO/NO-GO | Vini + Caroline | Schema de saída | 🔴 |

---

## 16. ❓ Decisões que dependem de você

Seis forks que eu não devo resolver sozinho. Todos são baratos de decidir e caros de descobrir
depois de codar.

| # | Decisão | Contexto | Minha recomendação |
|---|---|---|---|
| **1** | **O Auditor emite GO/NO-GO?** | Vinícius diz não (18:46); código, `06-estrutura-do-parecer.md`, `memory.md` e a PR #2 dizem sim | **Separar**: exposição técnica do Auditor + campo de decisão humana explícito, com autor e data (§12.3). Confirmar com a Caroline |
| **2** | **DD Jurídica: consumir ou ignorar?** | Vinícius quer consumir o resultado (21:40); `playbook.py:64` manda ignorar; é a lição L6, validada com a Caroline | **Consumir como input com fonte**, sem refazer a análise dominial. Muda uma linha do prompt e o schema de entrada (I7) |
| **3** | **Patacho: pedir ao Vini, extrair local, ou seguir sem?** | Fila pausada; Patacho está nos 24 PERDIDO | **Pedir extração pontual ao Vini** com a justificativa do 12235 (§10.4). Baixo atrito, alto retorno |
| **4** | **Quem faz a consulta gov.br do SPU?** | Agente não faz login nem captcha | Definir o dono e desenhar o handoff como etapa formal do fluxo, não como exceção |
| **5** | **Repo por lançamento: criar agora?** | Decidido na reunião, sem dono nem template | Se sim, definir template e dono antes da Fase 5. A arquitetura deve funcionar sem ele |
| **6** | **Onde vive o núcleo v2?** | Hoje é um repo de hackathon pessoal com 3 cópias divergentes | Se o Auditor é produto, migrar para `seazone-tech` com `main` protegida e PR — o padrão dos outros dois repos. Decidir antes da Fase 1 |

---

## Apêndice A — Índice de rastreabilidade

Cada requisito → onde foi dito → onde está tratado.

| Req. | Origem (timestamp da transcrição) | Seção |
|---|---|---|
| Reexecutar sempre | 22:44, 15:02, 24:06 | §9 |
| Buscar SPU pelo RIP | 17:31, 18:06 | §7, §15-F3 |
| Comparar com Patacho / Japaratinga | 17:31, 19:23, 23:35, 25:56 | §10 |
| Cruzar todas as fontes | 20:07, 24:33 | §8 |
| Explicar de onde veio | 17:11, 35:05 | §14 |
| Auditar a fonte do terceiro (R10) | 35:05, 38:05 | §1.3-I2, §5 |
| Parar e perguntar | 38:29 (contra-requisito) | §6, §7 |
| Loop com o humano dentro | 42:01, 42:24, **43:02** | §1.3-I1, §15-F4 |
| Aprender continuamente | 07:38, 07:54 | §11 |
| Painel não trava | 26:32, 30:16, **30:35** | §1.2-P10, §4.3-D8 |
| Conectar o Diário | 24:33, 25:05 | §13 |
| Repo por lançamento | 07:01, 30:47, 31:00, 32:01 | §1.3-I4, §13.5 |
| Homologação é por trecho / metadado | 03:50, 05:01 | §1.3-I4, §7 |
| Anomalia do entorno | 10:05–12:11 | §1.3-I5, §10.3 |
| Risco depende do instrumento | 08:15, 08:46 | §1.3-I6 |
| DD Jurídica como input | 21:40 | §1.3-I7, §16-2 |
| Proximidade geográfica | 23:35, 25:56 | §1.3-I3, §10.1 |
| Transcrição como evidência | 43:24 | §1.3-I8, §13.2 |
| Ingestão multi-ator | 31:00 | §1.3-I9, §14.5 |
| Não emitir GO/NO-GO | 18:46, 18:51 | §12.3, §16-1 |

## Apêndice B — Achados de código (referência rápida)

| ID | Arquivo | Achado |
|---|---|---|
| A | [app/core/monitor.py:27](../app/core/monitor.py#L27) | `list_files` não é recursivo ⇒ `elegivel` sempre falso ⇒ DD automática nunca dispara |
| B | [app/core/locator.py:108](../app/core/locator.py#L108) | Whitelist de 11 tipos + `depth=1` ⇒ tudo fora dela é invisível (ex.: `06 Confronto SPU`) |
| C | [app/main.py:37](../app/main.py#L37) | Fallback silencioso para DEMO; painel serve JSON versionado no repo |
| D | [app/main.py:34](../app/main.py#L34) | `_RESULTS` em memória, perdido no restart |
| E | [app/core/locator.py:160](../app/core/locator.py#L160) | Citação por keyword matching pós-hoc; etapa fora do dicionário sai sem link |
| F | [app/core/dd_engine.py:88](../app/core/dd_engine.py#L88) | Chamada única, sem `tools`, sem loop |
| G | [app/core/dd_engine.py:20](../app/core/dd_engine.py#L20) | `MAX_TOKENS=8000` — risco de truncamento silencioso em pareceres longos |
| H | [app/core/dd_engine.py:19](../app/core/dd_engine.py#L19) | `MODEL` default desatualizado (`claude-sonnet-4-5`) |
| I | [app/core/playbook.py:215](../app/core/playbook.py#L215) | `recomendacao` obrigatória no schema — conflita com §12.3 |
| J | [app/core/playbook.py:64](../app/core/playbook.py#L64) | "DD Jurídica — ignore" — conflita com I7 |
| K | PR #2 (corpo) | Três cópias locais divergentes do app |
