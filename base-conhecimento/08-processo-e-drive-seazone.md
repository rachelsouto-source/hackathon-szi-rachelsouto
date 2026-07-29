# 08 — Processo interno e Drive da Seazone

Você deve conhecer o processo interno utilizado pela Seazone para localizar os documentos
sem depender de o usuário apontar cada arquivo.

## Pasta padrão de projetos

A pasta padrão de um empreendimento normalmente contém:

- **Jurídico**
- **Terrenos**
- **Projeto Legal**
- **Estudo Preliminar**
- **Topografia**
- **Estrutural**
- **Fundação**
- **Sondagem**
- **Comercial**
- **Produto**
- **Memorial**
- **Documentação Ambiental**

## Onde os documentos costumam estar (estrutura observada no Drive)

Os empreendimentos ficam em `00 - Empreendimentos Estruturados`, na pasta mãe da Seazone.
Dentro de cada empreendimento:

```
<Empreendimento>/
  02 - Projetos/                    ← topográfico, EVA, sondagem, estrutural, fundação, EP
    09 - Imagens de Drone/          ← contexto e entorno
  05 - Jurídico/
    01 - Terreno/
      00 - Documentos e certidões/
        Imóvel 1/  Imóvel 2/        ← matrícula, espelho de IPTU, confrontantes
      02 - Proposta de compra e venda/
```

Regras práticas:

- Usar sempre a **última versão em PDF**.
- Ignorar pastas e arquivos marcados como `OLD`, `ANTIGO`, `Demais arquivos`, `REV00`
  quando houver revisão posterior.
- Mais de um imóvel ⇒ mais de uma matrícula ⇒ tratar cada uma e somar
  ([R1](04-regras-de-auditoria.md#r1--consistência-de-áreas)).
- A nomenclatura varia entre empreendimentos: **identifique pelo conteúdo**, não só pelo
  nome da pasta.

## Formatos e identificação automática

Os documentos podem estar em **PDF, DWG, RVT, XLSX, DOCX ou imagens**. Você deve
**identificar automaticamente o tipo de documento** pelo conteúdo:

| Pistas no documento | Tipo provável |
|---|---|
| "Certidão de inteiro teor", "Registro de Imóveis", matrícula nº, averbações (Av-1, R-2) | Matrícula |
| Inscrição imobiliária, IPTU, "espelho", dados cadastrais do imóvel | Espelho cadastral |
| Curvas de nível, cotas, norte, sistema de coordenadas (SIRGAS/UTM), ART de topografia | Levantamento topográfico |
| Furos SP-01..n, NSPT, "nível d'água", perfil de camadas, NBR 6484 | Sondagem (SPT) |
| Tabela de áreas, nº de unidades, pavimentos-tipo, implantação, torre/bloco | Estudo de massa / EP |
| Zoneamento, TO, CA, TP, recuos, "consulta de viabilidade", brasão da prefeitura | Viabilidade construtiva |
| Lançamento estrutural, pilares, modulação, cargas, ART estrutural | Estrutural |
| Estaca, tubulão, sapata, bloco de coroamento, cota de assentamento | Fundação |
| RIP, "Secretaria do Patrimônio da União", aforamento, ocupação, laudêmio | SPU / marinha |
| APP, supressão, DAP/AuC, licenciamento, bioma, restinga, mangue | Documentação ambiental |
| Valor, condições de pagamento, permuta, área considerada, prazo de exclusividade | Proposta de compra e venda |

Formatos **DWG e RVT** normalmente não são lidos diretamente: exigir a exportação em PDF
ou tratar como pendência ([R6](04-regras-de-auditoria.md#r6--completude-documental)) —
não inferir conteúdo a partir do nome do arquivo.

**Documentos escaneados** exigem OCR. Se o texto não for extraível com confiança, marcar
como ilegível e pedir nova via, em vez de ler parcialmente.

## Vocabulário de disciplinas

Para que os achados desta DD alimentem a base histórica, use as **disciplinas** do
vocabulário fixo da base histórica (`engine/schema.py` → `TAXONOMIA`, no repositório
`seazone-tech/base-conhecimento-dd-tecnica`):

`ambiental` · `urbanístico` · `concessionárias` · `incêndio` · `sanitário` ·
`patrimônio` · `jurídico-cartorial` · `topografia` · `arquitetura-projeto` · `engenharia`

E as **categorias**: `referência` · `conhecimento-geral` · `acerto` · `gargalo` ·
`exigência-de-órgão` · `erro`.

Ver [10 — Consulta à base histórica](10-consulta-a-base-historica.md).
