# 04 — Regras obrigatórias de auditoria (R1–R7)

**Sempre executar automaticamente**, em toda DD, mesmo quando nada parece errado.
Cada regra produz **achados**, e cada achado tem: descrição, **fonte**, **criticidade**
([05](05-criticidade.md)) e ação recomendada.

Regra que não pôde ser executada por falta de documento **não é "OK"** — é pendência
(ver [R6](#r6--completude-documental)).

---

## R1 — Consistência de áreas

Comparar as áreas informadas por **todas** as fontes disponíveis:

matrícula (soma, se houver mais de uma) × espelho cadastral × confrontantes ×
levantamento topográfico × área considerada na proposta.

```
dif% = | área_topográfica − área_matrícula | / área_matrícula × 100
```

- **dif% > 3% ⇒ classificar como risco** e exigir **retificação de matrícula**.
- Mais de uma matrícula ⇒ avaliar **unificação / amembramento**.
- Qualquer divergência entre as fontes ⇒ listar **todas** as áreas lado a lado no parecer,
  ainda que abaixo de 3%.

Registrar também o impacto: área menor que a registrada reduz potencial construtivo e,
portanto, o valor justo do terreno.

---

## R2 — Quantidade de unidades

Comparar a quantidade de unidades em **todos** os documentos que a informam:
estudo de massa, EVA, validação do EP, estrutural, memorial, proposta.

**Todos devem apresentar o mesmo número.** Caso contrário: **gerar inconsistência**,
apontando documento por documento qual número consta e qual é o vigente.

O mesmo confronto vale para vagas, pavimentos e altura.

---

## R3 — Parâmetros urbanísticos

Comparar os parâmetros do **projeto** (EP / estudo de massa / estrutural) com os
parâmetros **legais** (viabilidade construtiva + plano diretor do zoneamento):

| Parâmetro | Confronto |
|---|---|
| **TO** — taxa de ocupação | projetada ≤ máxima? |
| **CA** — coeficiente de aproveitamento | projetado ≤ máximo? há outorga onerosa envolvida? |
| **TP** — taxa de permeabilidade | projetada ≥ mínima? |
| **Recuos** | frontal, laterais e fundos atendidos? |
| **Gabarito** | nº de pavimentos e altura ≤ máximo? |
| **Uso** | o uso pretendido é permitido na zona? |

Qualquer parâmetro não atendido ⇒ achado de criticidade alta ou crítica + indicação de
readequação do anteprojeto. Se o atendimento depender de **outorga, incentivo, fruição
pública ou operação urbana**, quantificar o **custo** e registrar o risco de mudança de
regra (ver [09 — Florianópolis](09-florianopolis.md)).

Três checagens dentro do R3 que costumam passar batido — faça as três, sempre:

#### R3.a — Incentivos podem ser excludentes, não somáveis 🔴

Quando o projeto usa **mais de um instrumento** para folgar parâmetro (outorga, TDC, uso
misto, arte pública, sustentabilidade, fruição), verifique na viabilidade construtiva se eles
são **cumulativos ou alternativos**. Empilhar instrumentos é a forma mais comum de um projeto
parecer viável e não ser.

> **Caso-teste (Florianópolis):** a nota (OODC) da Consulta Automatizada exclui do aumento de
> 30% da taxa de ocupação (TO×1,3, Art. 70-A da LC 482/2014) **as edificações que fizerem uso
> do incentivo de Uso Misto** e os pavimentos com TO diferenciada do Art. 71. Projeto que usa
> uso misto para ganhar pavimento **e** TO×1,3 para a taxa de ocupação está usando dois
> caminhos que a lei apresenta como alternativos.

Ao encontrar: recalcule o parâmetro sobre a base do zoneamento, informe o excedente **em
pontos percentuais e em m²**, e aponte se o impasse é circular (abrir mão de um instrumento
derruba o benefício que ele concedia).

#### R3.b — Teto de CA com e sem TDC 🔴

O CA máximo total da tabela normalmente só se alcança **com Transferência do Direito de
Construir**. Calcule o teto **sem TDC** (básico + outorga) e compare com o CA do projeto.
Se o projeto excede esse teto, exija a **comprovação de aquisição de TDC** — é compra onerosa
de potencial de terceiros, com custo e processo próprios. Sem documento ⇒ crítico.

Verifique também se o acréscimo de **pavimentos** por TDC é zero: se for, o TDC dá coeficiente
mas não dá pavimento, e não serve de plano B para gabarito.

#### R3.c — Parâmetro por parâmetro, com risco de borda

Nenhum parâmetro pode ficar sem **valor legal** e **valor de projeto** lado a lado. E sinalize
**risco de borda** quando o projeto estiver a menos de 5% de um degrau normativo — informando
a margem em centímetros.

> Exemplo real: afastamento lateral de 1,50 m vale até fachada de 9,50 m e salta para 3,00 m
> acima disso. Projeto com fachada de 9,18 m tem **32 cm** de margem — qualquer ajuste de laje
> ou soleira dobra o afastamento e derruba a contagem de unidades.

---

## R4 — Riscos ambientais

Validar, com fonte, cada um dos itens:

- **APP** — existência, faixa, área não edificável, % de área útil remanescente, e se o
  projeto a respeita.
- **Terreno de marinha** — se sim, exigir afastamento demarcado no topográfico **e** no
  ambiental, e conferir a **documentação da SPU** ([bloco 10](03-ordem-de-analise.md#10-spu--terreno-de-marinha)).
- **SPU** — RIP, ocupação, aforamento, autorização. Marinha sem documentação SPU ⇒ pendência crítica.
- **Supressão** de vegetação — nº de indivíduos, autorização exigida, compensação e custo.
- **UC** — imóvel em unidade de conservação ou zona de amortecimento ⇒ achado crítico até
  prova documental em contrário.
- **Demolição** — construções existentes exigem alvará de demolição (prazo, custo e,
  em alguns municípios, dedução de outorga).
- **Sistema de esgoto** — comprovação de esgotamento sanitário / declaração da
  concessionária; condicionantes judiciais aplicáveis ao município.

---

## R5 — Riscos geotécnicos

Validar, cruzando sondagem × fundação × estrutural:

- **Solo mole** — camadas de baixa resistência, aterro, turfa.
- **Lençol freático** — NA raso, necessidade de rebaixamento e seu licenciamento.
- **Fundações especiais** — tipo recomendado pela sondagem × tipo adotado no projeto.
- **Contenções** — necessidade em função de desnível, divisas e vizinhança.

Toda solução onerosa vira linha no impacto de custo/prazo. Vibração e recalque em
vizinhos edificados são risco de implantação, não só de custo.

---

## R6 — Completude documental

Validar a presença de **todos** os documentos obrigatórios de
[03 — Ordem de análise](03-ordem-de-analise.md) e **informar os documentos faltantes**.

- Documento ausente, ilegível ou desatualizado ⇒ **pendência**, nunca presunção.
- Documento em revisão superada ⇒ registrar e exigir a versão vigente.
- Terreno de marinha ⇒ documentação SPU entra como obrigatória.

#### R6.a — Pasta não é documento 🔴

A estrutura de subpastas do Drive é criada **por template, vazia**. Nunca conclua que um
documento existe porque a pasta dele existe, ou porque ela tem subpastas. Só marque como
entregue se houver **arquivo**, com nome, data e revisão. Pasta com subpastas vazias
(inclusive `00 - OLD` vazia) é **documento ausente**, não "documento disponível".

> Este é o erro mais perigoso da DD: ele produz um ✅ onde não há nada, e ninguém volta a
> olhar um item que já está verde.

#### R6.b — Varredura exaustiva antes de concluir

Antes de fechar qualquer eixo, liste **todos** os arquivos da pasta do empreendimento e
classifique cada um como **lido / não lido / não aplicável**. "Existe e não foi lido" tem a
mesma severidade de "não existe" — os dois impedem a regra de rodar.

#### R6.c — A pendência herda a criticidade do que esconde

Sem sondagem em terreno inundável, o risco geotécnico é **desconhecido**, não baixo.
Nunca classifique ausência como severidade baixa.

A lista de pendências é seção obrigatória do parecer e condiciona a conclusão: pendência
crítica em aberto impede um **GO** limpo.

---

## R7 — Bombeiros / CBMSC

Extrair a **altura do projeto** (piso do último pavimento habitável até o nível de
descarga) e classificar:

| Faixa | Exigência típica | Impacto de custo |
|---|---|---|
| **até 12 m** | escada não enclausurada | baixo |
| **12 a 23 m** | **EEE** — escada enclausurada com exaustão (ou conforme IN vigente) | moderado |
| **acima de 23 m** | **EP** — escada pressurizada | **alto** — shaft, equipamento, manutenção |

Validar ainda:

- **EEE / EP** — o tipo indicado no projeto bate com a altura real?
- **ocupação** e **classe** — grupo de ocupação (residencial multifamiliar × hotel
  residencial / apart-hotel) e classe de risco. Produto de hospedagem pode atrair
  exigências adicionais de brigada e alarme; confirmar com o órgão em caso de dúvida.
- **NBR** aplicáveis (saídas de emergência, escadas, acessibilidade).
- **IN CBMSC** vigentes (Instruções Normativas) para o estado de Santa Catarina.

**Zona de risco:** altura entre ~20 m e ~25 m — pequena variação de projeto muda EEE → EP
e encarece significativamente. Sinalizar sempre, mesmo quando o projeto atual está abaixo
do limite.

Escopo na DD: o objetivo **não** é a análise de conformidade completa do preventivo, e sim
identificar **riscos de custo, prazo ou bloqueio** que afetem a decisão de compra.

Nunca marque bombeiro como **OK** apoiado em uma fonte só. Se dois documentos discordam sobre
o tipo de escada exigido, isso **é** o achado.

---

## R8 — Licenciamento e exigências municipais

Ler a viabilidade construtiva **inteira** — inclusive as seções finais de "outras restrições"
e "informações complementares". É onde ficam as exigências que ninguém mapeia. Checar sempre:

| Item | O que verificar |
|---|---|
| **Esgoto** | O licenciamento costuma ser condicionado a sistema coletivo **ou autônomo**. Exigir declaração da concessionária ou solução autônoma dimensionada (laudo de percolação) |
| **EIV** | Estudo de Impacto de Vizinhança — verificar obrigatoriedade; quando obrigatório, é requisito do licenciamento |
| **Regime de licenciamento** | Imóvel com restrição ambiental costuma ser excluído do regime declaratório ⇒ processo regular, mais lento |
| **Subsolo** | Alguns bairros exigem estudo específico aprovado pelo órgão ambiental ⇒ etapa e custo adicionais |
| **Vala de drenagem** | Exige consulta ao órgão de infraestrutura quanto a afastamentos |
| **Bem tombado / sítio arqueológico** | Edificação antiga ou entorno tombado ⇒ consulta ao órgão de patrimônio |
| **Regularidade dominial** | Divergência entre título, cadastro e realidade deve ser corrigida **antes** do pedido de aprovação — não é posterior nem opcional |
| **Validade das consultas** | Consultas costumam ter prazo (90 dias é comum). Informar a data de vencimento no parecer |

## R9 — Negócio e instrumento

Ler a proposta / CCV e conferir:

- **preço e forma de pagamento**;
- **qual área o negócio considera**, contra matrícula e topográfico;
- **se está assinado por todas as partes** — conferir o **log da assinatura eletrônica**, não o
  nome do arquivo. Arquivo chamado "assinado" pode ter só a assinatura do comprador;
- **os prazos das cláusulas** (trava de preço, entrega de documentos) contra a data de hoje.

Prazo vencido ou assinatura de vendedor ausente ⇒ **crítico**: o preço não está travado, e
qualquer economia obtida nas ressalvas técnicas pode ser devolvida na renegociação.

Consolidar o custo das ressalvas técnicas como **% do preço** — é o que torna o parecer
legível para quem decide.
