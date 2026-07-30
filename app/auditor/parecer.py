"""
DD TÉCNICA — o documento entregável, no formato `[Empreendimento] DD Técnica Spot`.

DUAS FAMÍLIAS DE DOCUMENTO, E EU JÁ TROQUEI UMA PELA OUTRA:

  · `[Empreendimento] DD Técnica Spot.docx` — **este aqui**. É a DD Técnica que a
    Seazone monta: PARECER TÉCNICO – DUE DILIGENCE, prosa técnica por disciplina,
    com FIGURAS NUMERADAS. Confirmado em `[Jurerê Spot III] DD Técnica Spot.docx`
    (196 parágrafos, 21 imagens) e em `[Foz Spot] DD Técnica Spot`, na pasta
    `02 - Projetos / 07 - DD Técnica` do Drive.
  · `DD TÉCNICA_SEAZONE_ID <id> <NOME>_R<rev>.pdf` — a ANÁLISE TÉCNICA da arquiteta
    contratada (Yaucha), em quadros. Documento diferente, de outro autor.

Numa iteração anterior eu li o segundo e reescrevi o módulo inteiro no formato dele.
Errado: o entregável da Seazone é o primeiro. Aqui ele está restaurado — mas os quadros
que valiam a pena no documento da Yaucha foram incorporados nas seções onde pertencem:

  · RESUMO GERAL (área total − deduções = área final) → dentro de TOPOGRAFIA
  · QUADRO DE ÁREAS (Item × Valor × Unidade)          → dentro de TOPOGRAFIA
  · NORMATIVAS E LEGISLAÇÃO (restrição × fonte)       → VIABILIDADE URBANÍSTICA
  · PREFEITURA × OBSERVAÇÕES, com "NÃO INFORMADO"     → VIABILIDADE URBANÍSTICA

ESTRUTURA REAL (ordem do Jurerê):
    PARECER TÉCNICO – DUE DILIGENCE – <NOME>
    parágrafo de abertura
    Documentos analisados — por bloco, com o nome do arquivo, por imóvel
    ESTUDOS: / VALIDAÇÃO:
    "Para realização da due diligence, foi verificado ... código de obras, plano
     diretor e demais legislações vigentes."
    TOPOGRAFIA · ESTUDO PRÉVIO AMBIENTAL · VIABILIDADE URBANÍSTICA ·
    VALIDAÇÃO DO ESTUDO PRELIMINAR SEAZONE · SONDAGEM · ESTRUTURA/FUNDAÇÃO · CONCLUSÃO

As figuras são numeradas em sequência ao longo do documento — "Figura 01 - Estudo do
levantamento topográfico"; "Figura 07 - Área de estudo e as áreas de terrenos de marinha
(GeoPortal)". A numeração é global, não por seção.
"""
from __future__ import annotations

import datetime as _dt
from typing import Any

from .livro import Livro

ICONE = {"Crítico": "🔴", "Atenção": "🟡", "OK": "🟢"}
NAO_INFORMADO = "NÃO INFORMADO"

ABERTURA = (
    "Trata-se de parecer técnico acerca das diligências e da análise técnica realizada "
    "pelo Setor de Lançamentos da Seazone Investimentos em relação aos estudos de "
    "viabilidade referentes ao terreno e ao estudo preliminar desenvolvido, objetivando "
    "a aquisição do imóvel e a continuidade no processo de estruturação do "
    "empreendimento.")

# Blocos da lista de documentos analisados, na ordem do documento real.
BLOCOS_DOC = [
    ("Certidão de inteiro teor da matrícula com ônus e ações", {"jurídico-cartorial"},
     ("matricula", "matrícula", "inteiro teor", "onus", "ônus")),
    ("Certidão Cadastral", {"jurídico-cartorial"}, ("cadastral", "iptu", "espelho")),
    ("Certidão de Confrontantes", {"jurídico-cartorial"}, ("confrontante",)),
    ("Viabilidade Construtiva", {"urbanístico"}, ("viabilidade", "consulta")),
    ("Documentação SPU / terreno de marinha", {"jurídico-cartorial"},
     ("spu", "rip", "marinha", "cnd")),
]
BLOCOS_ESTUDO = [
    ("Levantamento Topográfico", {"topografia"}, ("topograf", "prancha", "planialt")),
    ("Estudo de Viabilidade Ambiental", {"ambiental"}, ("eva", "ambiental")),
    ("Sondagem", {"engenharia"}, ("sondagem", "spt")),
    ("Estrutura", {"engenharia"}, ("estrutura", "quantitativo", "carga")),
    ("Fundação", {"engenharia"}, ("fundac", "fundaç", "premissas de fund")),
]
BLOCO_VALIDACAO = ("Validação do estudo preliminar pelo arquiteto responsável",
                   {"arquitetura-projeto"}, ("validac", "validaç", "dd_", "ep"))

# Seções de conclusão, na ordem do documento, e as disciplinas que as alimentam.
SECOES = [
    ("topografia", "TOPOGRAFIA", {"topografia"}),
    ("ambiental", "ESTUDO PRÉVIO AMBIENTAL", {"ambiental", "concessionárias", "sanitário"}),
    ("urbanistico", "VIABILIDADE URBANÍSTICA", {"urbanístico", "patrimônio"}),
    ("juridico_dominial", "SITUAÇÃO DOMINIAL", {"jurídico-cartorial"}),
    ("validacao_ep", "VALIDAÇÃO DO ESTUDO PRELIMINAR SEAZONE",
     {"arquitetura-projeto", "incêndio"}),
    ("sondagem", "SONDAGEM", {"engenharia"}),
    ("estrutura_fundacao", "ESTRUTURA / FUNDAÇÃO", {"engenharia"}),
]

PARAMETROS = [
    ("recuos", "RECUOS GERAIS"), ("altura_maxima", "ALTURA MÁXIMA"),
    ("taxa_ocupacao", "TAXA DE OCUPAÇÃO"), ("taxa_permeabilidade", "TAXA DE PERMEABILIDADE"),
    ("coeficiente_aproveitamento", "COEFICIENTE DE APROVEITAMENTO"),
    ("vagas_garagem", "VAGAS DE GARAGEM"), ("muro_lateral", "MURO LATERAL"),
    ("outorga", "OUTORGA ONEROSA"), ("eiv", "EIV"),
]


def _hoje() -> str:
    return _dt.date.today().strftime("%d/%m/%Y")


class Figuras:
    """
    Numerador global de figuras.

    No documento real a numeração corre ao longo do texto inteiro — "Figura 01" na
    topografia, "Figura 07" no ambiental. Não é por seção.
    """

    def __init__(self, livro: Livro):
        self.imgs = list((livro.cobertura or {}).get("imagens") or [])
        self.n = 0

    def da_secao(self, secao: str, limite: int = 4) -> str:
        sel = [i for i in self.imgs if i.get("secao") == secao][:limite]
        partes = []
        for i in sel:
            self.n += 1
            url = f"https://drive.google.com/thumbnail?id={i['id']}&sz=w1000"
            legenda = f"Figura {self.n:02d} - {i.get('nome','')}"
            partes.append(f"\n![{legenda}]({url})\n*{legenda};*\n")
            self.imgs.remove(i)
        return "".join(partes)

    def restantes(self) -> str:
        return self.da_secao(None, 0) if False else ""


def _docs_do_bloco(livro: Livro, discs: set[str], pistas: tuple) -> list[dict]:
    lidos = (livro.cobertura or {}).get("lidos") or []
    out = []
    for d in lidos:
        alvo = f"{d.get('caminho','')} {d.get('nome','')}".lower()
        if any(p in alvo for p in pistas) or d.get("disciplina") in discs:
            if any(p in alvo for p in pistas):
                out.append(d)
    return out


def _lista_documentos(livro: Livro) -> str:
    """
    Documentos analisados, por bloco, com o NOME DO ARQUIVO — como no documento real.

    Não é tabela: é lista, na ordem dos 12 blocos documentais do método.
    """
    L = []

    def bloco(rotulo, discs, pistas):
        docs = _docs_do_bloco(livro, discs, pistas)
        if docs:
            L.append(f"\n**{rotulo};**")
            for d in docs[:6]:
                link = f"[{d['nome']}]({d['link']})" if d.get("link") else d["nome"]
                L.append(f"- {link}")
        else:
            L.append(f"\n**{rotulo};** _(não analisado nesta rodada)_")

    for rot, discs, pistas in BLOCOS_DOC:
        bloco(rot, discs, pistas)
    L.append("\n**ESTUDOS:**")
    for rot, discs, pistas in BLOCOS_ESTUDO:
        bloco(rot, discs, pistas)
    L.append("\n**VALIDAÇÃO:**")
    bloco(*BLOCO_VALIDACAO)

    nao = (livro.cobertura or {}).get("nao_lidos_criticos") or []
    if nao:
        L.append(f"\n> ⚠️ **{len(nao)} documento(s) relevante(s) existem na pasta e NÃO "
                 f"foram analisados** nesta rodada — ver Pendências. \"Existe e não foi "
                 f"lido\" tem a mesma severidade de \"não existe\".")
    return "\n".join(L) + "\n"


def _tabelas_area(p: dict) -> str:
    """Área de Matrícula / Cadastro / Levantamento — as três do documento real."""
    at = p.get("areas_tabela") or {}
    L = []
    if at.get("matricula"):
        L.append("\n**Área de Matrícula**\n\n| Referência | Área |\n|---|---|")
        L += [f"| {i.get('ref','')} | {i.get('area','')} |" for i in at["matricula"]]
    if at.get("cadastro_pmf"):
        L.append("\n**Área de Cadastro Imobiliário**\n\n| Referência | Área |\n|---|---|")
        L += [f"| {i.get('ref','')} | {i.get('area','')} |" for i in at["cadastro_pmf"]]
    if at.get("topografico"):
        L.append(f"\n**Área Levantamento Topográfico**\n\n| Referência | Área |\n|---|---|"
                 f"\n| Área Real | {at['topografico']} |")
    return "\n".join(L) + "\n" if L else ""


def _resumo_geral(p: dict) -> str:
    """
    Área total menos as deduções → ÁREA FINAL.

    Emprestado da Análise Técnica da Yaucha, onde é o quadro mais útil: no 12235,
    8.573,00 − 1.331,65 (marinha) − 109,45 (estrada vicinal) = 7.131,90 m². É o número
    que decide o produto e não aparece em certidão nenhuma.
    """
    rg = p.get("resumo_geral") or {}
    if not (rg.get("area_total") or rg.get("deducoes") or rg.get("area_final")):
        return ""
    L = ["\n**Resumo geral da área aproveitável**\n", "| Terreno | Área |", "|---|---|"]
    if rg.get("area_total"):
        L.append(f"| Área total | {rg['area_total']} |")
    for d in rg.get("deducoes") or []:
        L.append(f"| ({d.get('item','')}) | −{d.get('area','')} |")
    if rg.get("area_final"):
        L.append(f"| **Área final aproveitável** | **{rg['area_final']}** |")
    if rg.get("observacao"):
        L.append(f"\n<sub>{rg['observacao']}</sub>")
    return "\n".join(L) + "\n"


def _quadro_areas(p: dict) -> str:
    q = p.get("quadro_areas") or []
    if not q:
        return ""
    L = ["\n**Quadro de áreas do projeto**\n", "| Item | Valor | Unidade |", "|---|---|---|"]
    for it in q:
        L.append(f"| {it.get('item','')} | {it.get('valor','')} | {it.get('unidade','')} |")
    return "\n".join(L) + "\n"


def _normativas(livro: Livro) -> str:
    """NORMATIVAS E LEGISLAÇÃO — restrição × fonte de pesquisa × data."""
    L = ["\n**Normativas e legislação verificadas**\n",
         "| Restrição / dispositivo | Fonte de pesquisa | Consultado em |", "|---|---|---|"]
    vistos = set()
    for a in livro.afirmacoes:
        for e in a.evidencias:
            if e.origem != "legislacao":
                continue
            chave = e.localizacao or e.ref
            if chave in vistos:
                continue
            vistos.add(chave)
            fonte = f"[texto primário]({e.link})" if e.link else (e.ref or "—")
            L.append(f"| {chave} | {fonte} | {(e.consultado_em or '')[:10] or '—'} |")
    if not vistos:
        return ("\n> ⚠️ **Nenhuma norma foi conferida em texto primário nesta rodada.** Os "
                "parâmetros abaixo, quando presentes, vêm da consulta de viabilidade; a lei "
                "que os fundamenta não foi verificada.\n")
    return "\n".join(L) + "\n"


def _prefeitura(p: dict) -> str:
    """Parâmetros urbanísticos × observações. Ausente sai como NÃO INFORMADO."""
    par = p.get("parametros_urbanisticos") or {}
    if not par:
        return ""
    L = ["\n**Parâmetros urbanísticos**\n", "| Parâmetro | Valor | Observações |",
         "|---|---|---|"]
    faltando = 0
    for chave, rotulo in PARAMETROS:
        v = par.get(chave)
        if isinstance(v, dict):
            valor, obs = v.get("valor") or NAO_INFORMADO, v.get("observacao") or "-"
        elif v:
            valor, obs = str(v), "-"
        else:
            valor, obs = NAO_INFORMADO, "-"
        if valor == NAO_INFORMADO:
            faltando += 1
            valor = f"**{valor}**"
        L.append(f"| {rotulo} | {valor} | {obs} |")
    for x in par.get("outros") or []:
        L.append(f"| {x.get('parametro','')} | {x.get('valor') or NAO_INFORMADO} | "
                 f"{x.get('observacao') or '-'} |")
    if faltando:
        L.append(f"\n<sub>{faltando} parâmetro(s) como NÃO INFORMADO — o município não "
                 f"publica, ou não foi possível confirmar em texto legal. Não estimados.</sub>")
    return "\n".join(L) + "\n"


def _achados(livro: Livro, discs: set[str]) -> str:
    itens = [a for a in livro.afirmacoes
             if a.disciplina in discs and a.severidade in ("Crítico", "Atenção")
             and a.tipo != "lacuna"]
    if not itens:
        return ""
    itens.sort(key=lambda a: 0 if a.severidade == "Crítico" else 1)
    L = ["\n**Pontos de atenção**\n"]
    for a in itens[:10]:
        L.append(f"- {ICONE.get(a.severidade,'·')} {a.texto}")
        if a.acao:
            L.append(f"  - *Ação:* {a.acao}")
        for c in a.comparativos:
            if c.premissa_de_trabalho:
                L.append(f"  - *Premissa de trabalho (analogia com caso anterior):* "
                         f"{c.premissa_de_trabalho}")
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------- #

def render(livro: Livro, changelog: dict | None = None) -> str:
    p = livro.proveniencia or {}
    im = p.get("imovel") or {}
    con = p.get("conclusao") or {}
    val = p.get("validacao") or {}
    expo = p.get("exposicao") or {}
    perfil = livro.perfil
    fig = Figuras(livro)

    L: list[str] = []
    L.append(f"# PARECER TÉCNICO – DUE DILIGENCE – {livro.nome.upper()}\n")
    L.append(ABERTURA + "\n")

    # ---- Identificação ------------------------------------------------------
    L.append("| | |\n|---|---|")
    L.append(f"| **Inscrição** | {im.get('inscricoes') or '(pendente)'} |")
    L.append(f"| **Endereço** | {im.get('endereco') or '(pendente)'} |")
    L.append(f"| **Município** | {perfil.cidade or '(pendente)'}"
             f"{'/' + perfil.uf if perfil.uf else ''} |")
    L.append(f"| **Área total de matrícula** | {im.get('area_matricula_total') or '(pendente)'} |")
    L.append(f"| **Matrícula** | {im.get('matriculas') or '(pendente)'} |")
    props = p.get("proprietarios") or []
    L.append(f"| **Proprietário(a)** | {'; '.join(props) if props else '(pendente)'} |")
    if perfil.regime_dominial:
        L.append(f"| **Regime dominial** | {perfil.regime_dominial} |")
    L.append("")

    # ---- Documentos analisados ---------------------------------------------
    L.append("## DOCUMENTOS ANALISADOS")
    L.append(_lista_documentos(livro))
    L.append("Para realização da due diligence, foi verificado, entre outros tópicos, "
             "código de obras, plano diretor e demais legislações vigentes.\n")

    # ---- Seções por disciplina ----------------------------------------------
    for chave, titulo, discs in SECOES:
        texto = (con.get(chave) or "").strip()
        ach = _achados(livro, discs)
        extras = ""
        if chave == "topografia":
            extras = _tabelas_area(p) + _resumo_geral(p) + _quadro_areas(p)
        elif chave == "urbanistico":
            extras = _normativas(livro) + _prefeitura(p)
        elif chave == "validacao_ep":
            bl = []
            if val.get("ajustes"):
                bl.append("\n**Ajustes exigidos no anteprojeto**\n")
                bl += [f"- {x}" for x in val["ajustes"]]
            if val.get("docs_aprovacao"):
                bl.append("\n**Documentos para Aprovação do Projeto Arquitetônico**\n")
                bl += [f"- {x}" for x in val["docs_aprovacao"]]
            if val.get("docs_alvara"):
                bl.append("\n**Documentos para o Alvará de Construção**\n")
                bl += [f"- {x}" for x in val["docs_alvara"]]
            extras = "\n".join(bl) + "\n" if bl else ""

        figs = fig.da_secao(chave)
        if not (texto or ach or extras.strip() or figs):
            L.append(f"## {titulo}\n")
            L.append("_Sem documentação disponível nesta rodada — ver Pendências._\n")
            continue
        L.append(f"## {titulo}\n")
        if texto:
            L.append(texto + "\n")
        if extras:
            L.append(extras)
        if ach:
            L.append(ach)
        if figs:
            L.append(figs)

    # ---- Cruzamento com casos anteriores ------------------------------------
    blocos = []
    for a in livro.afirmacoes:
        for c in a.comparativos:
            if not c.linhas:
                continue
            cols = []
            for l in c.linhas:
                for k in l.casos:
                    if k not in cols:
                        cols.append(k)
            B = [f"\n**{c.tema}**\n",
                 "| Parâmetro | Este caso | " + " | ".join(cols) + " | Significado |",
                 "|---|---|" + "---|" * len(cols) + "---|"]
            for l in c.linhas:
                B.append(f"| {l.parametro} | **{l.este_caso}** | "
                         + " | ".join(l.casos.get(k, "—") for k in cols)
                         + f" | {l.implicacao} |")
            if c.premissa_de_trabalho:
                B.append(f"\n→ **Premissa de trabalho:** {c.premissa_de_trabalho} "
                         f"<sub>(analogia · confiança {c.confianca_da_analogia})</sub>")
            if c.ressalva:
                B.append(f"\n⚠️ {c.ressalva}")
            blocos.append("\n".join(B))
    if blocos:
        L.append("## CASOS ANTERIORES COMPARÁVEIS\n")
        L += blocos
        L.append("\n<sub>Precedente embasa recomendação; não é fato sobre este terreno.</sub>\n")

    # ---- Pendências ---------------------------------------------------------
    lac = livro.lacunas_abertas()
    if lac or livro.perguntas_ao_humano:
        L.append("## PENDÊNCIAS\n")
        L.append("| Pendência | O que falta | Responsável |\n|---|---|---|")
        for a in sorted(lac, key=lambda x: 0 if x.severidade == "Crítico" else 1):
            quem = "Equipe Seazone" if a.depende_de_humano else "Fornecedor / disciplina"
            L.append(f"| {ICONE.get(a.severidade,'·')} {a.texto} | "
                     f"{a.o_que_falta or '—'} | {quem} |")
        for q in livro.perguntas_ao_humano:
            L.append(f"| 👤 {q.get('o_que_preciso','')} | {q.get('para_que','')} | "
                     f"Equipe Seazone |")
        L.append("")

    # ---- Conclusão ----------------------------------------------------------
    L.append("## CONCLUSÃO\n")
    if con.get("final"):
        L.append(con["final"] + "\n")
    elif expo.get("situacao"):
        L.append(expo["situacao"] + "\n")
    else:
        L.append("_Conclusão não consolidada nesta rodada — ver Pendências._\n")
    if expo.get("divergencias"):
        L.append("**Divergências entre documentos**\n")
        L += [f"- {x}" for x in expo["divergencias"]]
        L.append("")
    if expo.get("impacto_custo_prazo"):
        L.append(f"**Impacto em custo e prazo:** {expo['impacto_custo_prazo']}\n")
    crit = sum(1 for a in livro.achados() if a.severidade == "Crítico")
    aten = sum(1 for a in livro.achados() if a.severidade == "Atenção")
    L.append(f"**Quadro de criticidade:** {crit} achado(s) crítico(s), {aten} de atenção, "
             f"{len(lac)} pendência(s) aberta(s).\n")

    # ---- Recomendação: decisão humana ---------------------------------------
    L.append("### RECOMENDAÇÃO\n")
    L.append("> A classificação **GO / GO COM RESSALVAS / NO-GO** é decisão humana. O "
             "Auditor apresenta acima a análise, as evidências e as pendências; a "
             "recomendação é assinada por quem responde pela DD.\n")
    L.append("| | |\n|---|---|")
    L.append("| **Recomendação** | ( ) GO   ( ) GO COM RESSALVAS   ( ) NO-GO |")
    L.append("| **Justificativa** | |")
    L.append("| **Responsável** | ______________________________ |")
    L.append("| **Data** | ____ / ____ / ________ |")

    cidade = f"{perfil.cidade}/{perfil.uf}" if perfil.cidade else "Florianópolis/SC"
    L.append(f"\n*{cidade}, {_hoje()}.*")
    L.append("*Setor de Projetos — Estruturação — Seazone Investimentos.*")

    cob = livro.cobertura or {}
    L.append(f"\n---\n<sub>Auditor de DD Técnica v2 · rodada {livro.rodada} · "
             f"{p.get('documentos_lidos', 0)} de {cob.get('total', 0)} arquivos lidos · "
             f"{fig.n} figura(s) · {p.get('chamadas_de_ferramenta', 0)} consultas · "
             f"{livro.gerado_em[:19]}. Rascunho técnico para revisão humana.</sub>")

    return "\n".join(x for x in L if x is not None)


def nome_arquivo(livro: Livro) -> str:
    """Padrão da casa: `[Foz Spot] DD Técnica Spot`."""
    return nome_arquivo_de(livro.nome)


def nome_arquivo_de(nome: str) -> str:
    """Mesmo padrão, a partir do nome do empreendimento (o painel só tem o nome)."""
    return f"[{nome}] DD Técnica Spot"


def imagens_para_doc(livro: Livro, drive=None) -> dict[str, bytes]:
    """Baixa as figuras para embutir no .docx / Google Doc."""
    out: dict[str, bytes] = {}
    if drive is None:
        return out
    for i in ((livro.cobertura or {}).get("imagens") or [])[:24]:
        url = f"https://drive.google.com/thumbnail?id={i['id']}&sz=w1000"
        try:
            data, _ = drive.download_file_by_id(i["id"], i.get("mime", "image/png"))
            out[url] = data
        except Exception:  # noqa: BLE001
            continue
    return out
