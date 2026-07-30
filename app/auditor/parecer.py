"""
DD TÉCNICA — o documento entregável, no formato real da Seazone.

FORMATO EXTRAÍDO DOS DOCUMENTOS REAIS, não de um template idealizado:
  · DD TÉCNICA_SEAZONE_ID - 12235_R00.pdf        (São Miguel dos Milagres, 23 pp.)
  · DD TÉCNICA_SEAZONE_ID 5966 PATACHO SPOT_R03  (Patacho, 20 pp.)
  · [Jurerê Spot III] DD Técnica Spot.docx

A DD Técnica NÃO é um parecer em prosa corrida — é uma **ANÁLISE TÉCNICA em quadros**,
com cabeçalho de ID em toda seção. A primeira versão deste módulo renderizava o parecer
jurídico-formal do template antigo; os documentos reais mostram outra coisa:

    ANÁLISE TÉCNICA (capa: projeto, município, área, proprietário)
    IMPLANTAÇÃO GERAL [+ trechos]
    CONSULTA DE VIABILIDADE E ÍNDICES URBANÍSTICOS
        RESUMO GERAL          — área total menos as deduções → ÁREA FINAL
        NORMATIVAS E LEGISLAÇÃO — RESTRIÇÕES × FONTE DE PESQUISA
        PREFEITURA × OBSERVAÇÕES — parâmetro, valor, observação ("NÃO INFORMADO" quando falta)
    QUADRO DE ÁREAS           — Item × Valor × Unidade
    ANÁLISE DE PROJETO        — relação projeto × topografia, afastamentos
    ANÁLISE DE PROJETO – SUGESTÕES
    CORTE ESQUEMÁTICO
    LICENCIAMENTO             — licença prévia, de instalação, alvará
    PROJETO DE REFERÊNCIA
    ATA DE APROVAÇÃO – ETAPA VALIDAÇÃO

Duas coisas que o documento real ensina e que valem como regra:

1. **"NÃO INFORMADO" é uma resposta legítima e frequente.** No 12235, TO, TP, vagas e
   muro lateral estão todos assim. O documento registra a ausência em vez de estimar —
   exatamente o princípio do Livro de Evidências.
2. **A coluna "FONTE DE PESQUISA" existe desde sempre.** A rastreabilidade da legislação
   não é invenção nossa; é o formato da casa.
"""
from __future__ import annotations

import datetime as _dt
from typing import Any

from .livro import Livro

ICONE = {"Crítico": "🔴", "Atenção": "🟡", "OK": "🟢"}
NAO_INFORMADO = "NÃO INFORMADO"

# Parâmetros do quadro PREFEITURA × OBSERVAÇÕES, na ordem do documento real.
PARAMETROS = [
    ("recuos", "RECUOS GERAIS"),
    ("altura_maxima", "ALTURA MÁXIMA"),
    ("taxa_ocupacao", "TAXA DE OCUPAÇÃO"),
    ("taxa_permeabilidade", "TAXA DE PERMEABILIDADE"),
    ("coeficiente_aproveitamento", "COEFICIENTE DE APROVEITAMENTO"),
    ("vagas_garagem", "VAGAS DE GARAGEM"),
    ("muro_lateral", "MURO LATERAL"),
    ("outorga", "OUTORGA ONEROSA"),
    ("eiv", "EIV — ESTUDO DE IMPACTO DE VIZINHANÇA"),
]

# Seções de análise de projeto e as disciplinas que as alimentam.
ANALISES = [
    ("topografia", "RELAÇÃO PROJETO × TOPOGRAFIA", {"topografia"}),
    ("implantacao", "IMPLANTAÇÃO E AFASTAMENTOS", {"arquitetura-projeto", "urbanístico"}),
    ("ambiental", "RESTRIÇÕES AMBIENTAIS", {"ambiental"}),
    ("dominial", "SITUAÇÃO DOMINIAL", {"jurídico-cartorial"}),
    ("geotecnico", "SONDAGEM, ESTRUTURA E FUNDAÇÃO", {"engenharia"}),
    ("incendio", "SEGURANÇA CONTRA INCÊNDIO", {"incêndio"}),
    ("infraestrutura", "INFRAESTRUTURA E CONCESSIONÁRIAS",
     {"concessionárias", "sanitário"}),
]

LICENCAS = [("licenca_previa", "LICENÇA PRÉVIA"),
            ("licenca_instalacao", "LICENÇA DE INSTALAÇÃO"),
            ("alvara_construcao", "ALVARÁ DE CONSTRUÇÃO")]


def _hoje() -> str:
    return _dt.date.today().strftime("%d/%m/%Y")


def _cab(livro: Livro) -> str:
    """`ID – 12235 | MILAGRES SPOT - SÃO MIGUEL DOS MILAGRES/AL` — em toda seção."""
    p = livro.perfil
    local = f" - {p.cidade.upper()}/{p.uf}" if p.cidade else ""
    return f"<sub>ID – {p.emp_id} | {livro.nome.upper()}{local}</sub>"


def _fig(f: dict) -> str:
    url = f.get("url") or (f"https://drive.google.com/thumbnail?id={f['id']}&sz=w1000"
                           if f.get("id") else "")
    if not url:
        return ""
    return f"\n![{f.get('nome','Figura')}]({url})\n*{f.get('nome','')}*\n"


def _figuras(livro: Livro, secao: str, limite: int = 3) -> str:
    imgs = ((livro.cobertura or {}).get("imagens") or [])
    return "".join(_fig(i) for i in [x for x in imgs if x.get("secao") == secao][:limite])


def _bullets(livro: Livro, discs: set[str], severidades: tuple[str, ...]) -> list[str]:
    itens = [a for a in livro.afirmacoes
             if a.disciplina in discs and a.severidade in severidades
             and a.tipo != "lacuna"]
    itens.sort(key=lambda a: 0 if a.severidade == "Crítico" else 1)
    return [f"- {ICONE.get(a.severidade,'·')} **{a.texto}**"
            + (f"\n  - *Ação:* {a.acao}" if a.acao else "") for a in itens]


# --------------------------------------------------------------------------- #
# Quadros
# --------------------------------------------------------------------------- #

def _resumo_geral(p: dict) -> str:
    """
    Área total menos as deduções → ÁREA FINAL.

    No 12235: 8.573,00 m² − 1.331,65 (marinha) − 109,45 (estrada vicinal) = 7.131,90 m².
    É o número que importa para o produto, e ele não aparece em nenhuma certidão.
    """
    rg = p.get("resumo_geral") or {}
    total = rg.get("area_total")
    deducoes = rg.get("deducoes") or []
    final = rg.get("area_final")
    if not (total or deducoes or final):
        return ""
    L = ["\n**RESUMO GERAL**\n", "| Terreno | Área |", "|---|---|"]
    if total:
        L.append(f"| ÁREA TOTAL | {total} |")
    for d in deducoes:
        L.append(f"| {str(d.get('item','')).upper()} | −{d.get('area','')} |")
    if final:
        L.append(f"| **ÁREA FINAL** | **{final}** |")
    if rg.get("observacao"):
        L.append(f"\n<sub>{rg['observacao']}</sub>")
    return "\n".join(L) + "\n"


def _normativas(livro: Livro) -> str:
    """
    NORMATIVAS E LEGISLAÇÃO — RESTRIÇÕES × FONTE DE PESQUISA.

    A coluna de fonte é do formato original da casa. Aqui ela é preenchida com o link
    do texto primário e a data da consulta.
    """
    L = ["\n**NORMATIVAS E LEGISLAÇÃO**\n",
         "| Restrições | Fonte de pesquisa | Consultado em |", "|---|---|---|"]
    vistos, n = set(), 0
    for a in livro.afirmacoes:
        for e in a.evidencias:
            if e.origem != "legislacao":
                continue
            chave = (e.localizacao or e.ref)
            if chave in vistos:
                continue
            vistos.add(chave)
            n += 1
            fonte = f"[{e.link[:60]}…]({e.link})" if e.link else (e.ref or "—")
            L.append(f"| {chave} | {fonte} | {(e.consultado_em or '')[:10] or '—'} |")
    if not n:
        return ("\n**NORMATIVAS E LEGISLAÇÃO**\n\n"
                "> ⚠️ Nenhuma norma foi conferida em texto primário nesta rodada. Os "
                "parâmetros abaixo, quando presentes, vêm da consulta de viabilidade — "
                "a lei que os fundamenta **não** foi verificada.\n")
    return "\n".join(L) + "\n"


def _prefeitura(p: dict) -> str:
    """
    PREFEITURA × OBSERVAÇÕES.

    Parâmetro ausente sai como NÃO INFORMADO — é o que o documento real faz, e é a
    diferença entre registrar a lacuna e inventar um número.
    """
    par = p.get("parametros_urbanisticos") or {}
    L = ["\n**PREFEITURA**\n", "| Parâmetro | Valor | Observações |", "|---|---|---|"]
    for chave, rotulo in PARAMETROS:
        v = par.get(chave)
        if isinstance(v, dict):
            valor, obs = v.get("valor") or NAO_INFORMADO, v.get("observacao") or "-"
        elif v:
            valor, obs = str(v), "-"
        else:
            valor, obs = NAO_INFORMADO, "-"
        destaque = "**" if valor == NAO_INFORMADO else ""
        L.append(f"| {rotulo} | {destaque}{valor}{destaque} | {obs} |")
    for extra in (par.get("outros") or []):
        L.append(f"| {str(extra.get('parametro','')).upper()} | "
                 f"{extra.get('valor') or NAO_INFORMADO} | {extra.get('observacao') or '-'} |")
    faltando = sum(1 for c, _ in PARAMETROS
                   if not (par.get(c) if not isinstance(par.get(c), dict)
                           else par[c].get("valor")))
    if faltando:
        L.append(f"\n<sub>{faltando} parâmetro(s) como NÃO INFORMADO — a prefeitura não "
                 f"publica, ou não foi possível confirmar em texto legal. Não estimados "
                 f"de propósito.</sub>")
    return "\n".join(L) + "\n"


def _quadro_areas(p: dict) -> str:
    """QUADRO DE ÁREAS — Item × Valor × Unidade."""
    q = p.get("quadro_areas") or []
    if not q:
        at = p.get("areas_tabela") or {}
        if at.get("topografico"):
            q = [{"item": "Área do terreno (levantamento)",
                  "valor": at["topografico"], "unidade": "m²"}]
    if not q:
        return ""
    L = ["\n## QUADRO DE ÁREAS\n", "| Item | Valor | Unidade |", "|---|---|---|"]
    for it in q:
        L.append(f"| {it.get('item','')} | {it.get('valor','')} | {it.get('unidade','')} |")
    return "\n".join(L) + "\n"


def _comparativos(livro: Livro) -> str:
    """Cruzamento com casos anteriores — a seção que o documento manual não tinha."""
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
            B = [f"\n**{c.tema.upper()}**\n",
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
    if not blocos:
        return ""
    return ("\n## CRUZAMENTO COM CASOS ANTERIORES\n"
            + "\n".join(blocos)
            + "\n\n<sub>Precedente embasa recomendação; não é fato sobre este "
              "terreno.</sub>\n")


# --------------------------------------------------------------------------- #

def render(livro: Livro, changelog: dict | None = None) -> str:
    p = livro.proveniencia or {}
    perfil = livro.perfil
    cab = _cab(livro)
    rev = f"R{max(0, livro.rodada - 1):02d}"

    L: list[str] = []

    # ---- CAPA ---------------------------------------------------------------
    L.append(f"# ANÁLISE TÉCNICA\n")
    L.append(f"## DD TÉCNICA_SEAZONE_ID {perfil.emp_id} {livro.nome.upper()}_{rev}\n")
    L.append("| | |\n|---|---|")
    L.append(f"| **PROJETO** | {livro.nome} |")
    L.append(f"| **MUNICÍPIO** | {perfil.cidade or '(pendente)'}"
             f"{'/' + perfil.uf if perfil.uf else ''} |")
    im = p.get("imovel") or {}
    L.append(f"| **ÁREA** | {im.get('area_matricula_total') or '(pendente)'} |")
    L.append(f"| **MATRÍCULA** | {im.get('matriculas') or '(pendente)'} |")
    L.append(f"| **INSCRIÇÃO** | {im.get('inscricoes') or '(pendente)'} |")
    props = p.get("proprietarios") or []
    L.append(f"| **PROPRIETÁRIO DO IMÓVEL** | {'; '.join(props) if props else '(pendente)'} |")
    if perfil.regime_dominial:
        L.append(f"| **REGIME DOMINIAL** | {perfil.regime_dominial} |")
    L.append(f"| **DATA** | {_hoje()} |")
    L.append("")

    # ---- IMPLANTAÇÃO GERAL --------------------------------------------------
    L.append("## IMPLANTAÇÃO GERAL")
    L.append(cab)
    L.append(_figuras(livro, "localizacao") or "\n::FIG:: Implantação geral / entorno\n")

    # ---- CONSULTA DE VIABILIDADE E ÍNDICES URBANÍSTICOS ---------------------
    L.append("## CONSULTA DE VIABILIDADE E ÍNDICES URBANÍSTICOS")
    L.append(cab)
    L.append(_resumo_geral(p))
    L.append(_normativas(livro))
    L.append(_prefeitura(p))
    L.append(_figuras(livro, "topografia"))

    # ---- QUADRO DE ÁREAS ----------------------------------------------------
    qa = _quadro_areas(p)
    if qa:
        L.append(qa)
        L.append(cab)
    at = p.get("areas_tabela") or {}
    if at.get("matricula") or at.get("cadastro_pmf"):
        L.append("\n**Confronto de áreas entre fontes**\n")
        L.append("| Fonte | Referência | Área |\n|---|---|---|")
        for it in at.get("matricula") or []:
            L.append(f"| Matrícula | {it.get('ref','')} | {it.get('area','')} |")
        for it in at.get("cadastro_pmf") or []:
            L.append(f"| Cadastro municipal | {it.get('ref','')} | {it.get('area','')} |")
        if at.get("topografico"):
            L.append(f"| Levantamento topográfico | georreferenciado | {at['topografico']} |")
        L.append("")

    # ---- ANÁLISE DE PROJETO -------------------------------------------------
    L.append("## ANÁLISE DE PROJETO")
    L.append(cab)
    houve = False
    for chave, titulo, discs in ANALISES:
        bl = _bullets(livro, discs, ("Crítico", "Atenção"))
        figs = _figuras(livro, chave, 2)
        if not bl and not figs:
            continue
        houve = True
        L.append(f"\n### {titulo}\n")
        L += bl
        if figs:
            L.append(figs)
    if not houve:
        L.append("\n_Sem achados consolidados nesta rodada._\n")

    # ---- SUGESTÕES ----------------------------------------------------------
    sug = (p.get("validacao") or {}).get("ajustes") or []
    if sug:
        L.append("\n## ANÁLISE DE PROJETO – SUGESTÕES")
        L.append(cab + "\n")
        L += [f"- {x}" for x in sug]
        L.append("")
        L.append(_figuras(livro, "validacao_ep", 2))

    # ---- CRUZAMENTO ---------------------------------------------------------
    L.append(_comparativos(livro))

    # ---- LICENCIAMENTO ------------------------------------------------------
    lic = p.get("licenciamento") or {}
    val = p.get("validacao") or {}
    if lic or val.get("docs_aprovacao") or val.get("docs_alvara"):
        L.append("## LICENCIAMENTO")
        L.append(cab + "\n")
        for chave, rotulo in LICENCAS:
            v = lic.get(chave)
            if v:
                L.append(f"**{rotulo}** — {v}\n")
        if val.get("docs_aprovacao"):
            L.append("**Documentos para aprovação do projeto arquitetônico**\n")
            L += [f"- {x}" for x in val["docs_aprovacao"]]
            L.append("")
        if val.get("docs_alvara"):
            L.append("**Documentos para o alvará de construção**\n")
            L += [f"- {x}" for x in val["docs_alvara"]]
            L.append("")

    # ---- PENDÊNCIAS ---------------------------------------------------------
    lac = livro.lacunas_abertas()
    if lac or livro.perguntas_ao_humano:
        L.append("## PENDÊNCIAS")
        L.append(cab + "\n")
        L.append("| Pendência | O que falta | Responsável |\n|---|---|---|")
        for a in sorted(lac, key=lambda x: 0 if x.severidade == "Crítico" else 1):
            quem = "Equipe Seazone" if a.depende_de_humano else "Fornecedor / disciplina"
            L.append(f"| {ICONE.get(a.severidade,'·')} {a.texto} | "
                     f"{a.o_que_falta or '—'} | {quem} |")
        for q in livro.perguntas_ao_humano:
            L.append(f"| 👤 {q.get('o_que_preciso','')} | {q.get('para_que','')} | "
                     f"Equipe Seazone |")
        L.append("")

    # ---- CONCLUSÃO ----------------------------------------------------------
    con = p.get("conclusao") or {}
    expo = p.get("exposicao") or {}
    L.append("## CONCLUSÃO")
    L.append(cab + "\n")
    if expo.get("situacao"):
        L.append(f"{expo['situacao']}\n")
    if con.get("final"):
        L.append(f"{con['final']}\n")
    if expo.get("divergencias"):
        L.append("**Divergências entre documentos**\n")
        L += [f"- {x}" for x in expo["divergencias"]]
        L.append("")
    if expo.get("impacto_custo_prazo"):
        L.append(f"**Impacto em custo e prazo:** {expo['impacto_custo_prazo']}\n")
    crit = sum(1 for a in livro.achados() if a.severidade == "Crítico")
    aten = sum(1 for a in livro.achados() if a.severidade == "Atenção")
    L.append(f"**Quadro de criticidade:** {crit} crítico(s), {aten} de atenção, "
             f"{len(lac)} pendência(s) aberta(s).\n")

    # ---- ATA DE APROVAÇÃO ---------------------------------------------------
    L.append("## ATA DE APROVAÇÃO – ETAPA VALIDAÇÃO")
    L.append(cab + "\n")
    L.append("> A classificação **GO / GO COM RESSALVAS / NO-GO** é decisão humana. "
             "A Análise Técnica apresenta a exposição, as evidências e as pendências; "
             "a recomendação é assinada por quem responde pela análise.\n")
    L.append("| | |\n|---|---|")
    L.append("| **RECOMENDAÇÃO** | ( ) GO  ( ) GO COM RESSALVAS  ( ) NO-GO |")
    L.append("| **JUSTIFICATIVA** | |")
    L.append("| **CONTRATANTE** | Seazone Investimentos — Setor de Lançamentos |")
    L.append("| **RESPONSÁVEL** | ______________________________ |")
    L.append("| **DATA** | ____ / ____ / ________ |")

    cidade = f"{perfil.cidade}/{perfil.uf}" if perfil.cidade else "Florianópolis/SC"
    L.append(f"\n*{cidade}, {_hoje()}.*")
    L.append("*Setor de Projetos — Estruturação — Seazone Investimentos.*")

    cob = livro.cobertura or {}
    L.append(f"\n---\n<sub>Auditor de DD Técnica v2 · {rev} · rodada {livro.rodada} · "
             f"{p.get('documentos_lidos', 0)} de {cob.get('total', 0)} arquivos lidos · "
             f"{p.get('chamadas_de_ferramenta', 0)} consultas · {livro.gerado_em[:19]}. "
             f"Rascunho técnico para revisão humana.</sub>")

    return "\n".join(x for x in L if x is not None)


def nome_arquivo(livro: Livro) -> str:
    """Padrão de nome dos documentos reais: `DD TÉCNICA_SEAZONE_ID 12235 NOME_R00`."""
    rev = f"R{max(0, livro.rodada - 1):02d}"
    return f"DD TÉCNICA_SEAZONE_ID {livro.perfil.emp_id} {livro.nome.upper()}_{rev}"


def imagens_para_doc(livro: Livro, drive=None) -> dict[str, bytes]:
    """Baixa as figuras para embutir no .docx / Google Doc."""
    out: dict[str, bytes] = {}
    if drive is None:
        return out
    for i in ((livro.cobertura or {}).get("imagens") or [])[:14]:
        url = f"https://drive.google.com/thumbnail?id={i['id']}&sz=w1000"
        try:
            data, _ = drive.download_file_by_id(i["id"], i.get("mime", "image/png"))
            out[url] = data
        except Exception:  # noqa: BLE001
            continue
    return out
