"""
PARECER TÉCNICO — o documento oficial da DD Técnica.

DISTINÇÃO QUE EU TINHA PERDIDO E QUE É O PONTO DE TUDO:

  · `relatorio.py` renderiza a ÁREA DE TRABALHO — achados, cruzamentos, lacunas,
    cobertura, trilha. É o que o painel mostra enquanto se audita.
  · `parecer.py` (este módulo) renderiza o ENTREGÁVEL — o documento no formato oficial
    da Seazone, o mesmo que a Rachel monta à mão, que espelha
    "[Empreendimento] DD Técnica Spot.docx" e segue
    `claude.md/templates/parecer-tecnico.md`.

Na v2 inicial eu substituí o segundo pelo primeiro. O painel passou a mostrar uma tela
de auditoria e o documento oficial sumiu — exatamente a reclamação: "não está claro o que
está refletindo no painel; preciso gerar um documento da DD técnica conforme repassei".

O formato tem seções fixas, três tabelas de área e FIGURAS. Revisão de 29/07, 29:31 —
"ele montou essa DD técnica igual eu faço, então vou colocando imagens e tudo mais".

Uma diferença deliberada em relação ao template original: a linha de RECOMENDAÇÃO sai
marcada como decisão humana, com espaço para assinatura, em vez de o Auditor cravar
GO/NO-GO. Ver docs/ARQUITETURA-AUDITOR-V2.md §12.3 — pendente de validação com a Caroline.
"""
from __future__ import annotations

import datetime as _dt
from typing import Any

from .livro import Afirmacao, Livro

ICONE = {"Crítico": "🔴", "Atenção": "🟡", "OK": "🟢"}

# Ordem canônica das seções de conclusão do parecer oficial. `urbanistico` é acréscimo
# nosso — a legislação precisava de lugar próprio, e antes ficava diluída no ambiental.
SECOES = [
    ("topografia", "TOPOGRAFIA"),
    ("ambiental", "ESTUDO PRÉVIO AMBIENTAL"),
    ("urbanistico", "VIABILIDADE URBANÍSTICA E LEGISLAÇÃO"),
    ("juridico_dominial", "SITUAÇÃO DOMINIAL"),
    ("validacao_ep", "VALIDAÇÃO DO ESTUDO PRELIMINAR SEAZONE"),
    ("sondagem", "SONDAGEM"),
    ("estrutura_fundacao", "ESTRUTURA / FUNDAÇÃO"),
]

# Disciplinas do Livro que alimentam cada seção — é assim que os achados entram no
# parecer sem o Redator precisar reescrevê-los.
DISCIPLINAS_DA_SECAO = {
    "topografia": {"topografia"},
    "ambiental": {"ambiental", "concessionárias", "sanitário"},
    "urbanistico": {"urbanístico", "patrimônio", "incêndio"},
    "juridico_dominial": {"jurídico-cartorial"},
    "validacao_ep": {"arquitetura-projeto"},
    "sondagem": {"engenharia"},
    "estrutura_fundacao": {"engenharia"},
}


def _hoje() -> str:
    return _dt.date.today().strftime("%d/%m/%Y")


def _fig(f: dict) -> str:
    """Figura embutida por thumbnail do Drive — funciona no MD, no HTML e no Word."""
    url = f.get("url") or (f"https://drive.google.com/thumbnail?id={f['id']}&sz=w900"
                           if f.get("id") else "")
    if not url:
        return ""
    legenda = f.get("nome") or f.get("cap") or "Figura"
    return f"\n![{legenda}]({url})\n*{legenda}*\n"


def _figuras_da_secao(livro: Livro, secao: str) -> str:
    imgs = ((livro.cobertura or {}).get("imagens") or [])
    sel = [i for i in imgs if i.get("secao") == secao]
    return "".join(_fig(i) for i in sel[:4])


def _tabela_areas(titulo: str, itens: list[dict], rotulo: str) -> str:
    if not itens:
        return ""
    L = [f"\n**{titulo}**\n", f"| {rotulo} | Área (m²) |", "|---|---|"]
    for it in itens:
        L.append(f"| {it.get('ref','')} | {it.get('area','')} |")
    return "\n".join(L) + "\n"


def _achados_da_secao(livro: Livro, secao: str) -> str:
    """
    Os achados entram no parecer resumidos e com a ação — não como tabela de auditoria.

    O parecer é prosa técnica; a tabela completa vive no painel e na planilha de controle.
    """
    discs = DISCIPLINAS_DA_SECAO.get(secao, set())
    itens = [a for a in livro.afirmacoes
             if a.disciplina in discs and a.severidade in ("Crítico", "Atenção")]
    if not itens:
        return ""
    itens.sort(key=lambda a: 0 if a.severidade == "Crítico" else 1)
    L = ["\n**Pontos de atenção desta seção**\n"]
    for a in itens[:10]:
        L.append(f"- {ICONE.get(a.severidade,'·')} {a.texto}")
        if a.acao:
            L.append(f"  - *Ação:* {a.acao}")
        for c in a.comparativos:
            if c.premissa_de_trabalho:
                L.append(f"  - *Premissa de trabalho (analogia com casos anteriores):* "
                         f"{c.premissa_de_trabalho}")
    return "\n".join(L) + "\n"


def _legislacao_verificada(livro: Livro) -> str:
    """
    Seção nova, e a que estava faltando: o que foi conferido em texto legal, com link e
    data. Sem isto, "foi verificado o plano diretor" é uma frase de template.
    """
    evs = []
    for a in livro.afirmacoes:
        for e in a.evidencias:
            if e.origem == "legislacao":
                evs.append((e, a))
    if not evs:
        return ("\n> ⚠️ **Nenhuma legislação foi verificada em texto primário nesta rodada.** "
                "Os parâmetros urbanísticos citados vêm da Viabilidade Técnica Construtiva; "
                "a norma que os fundamenta não foi conferida. Registrar como pendência.\n")

    vistos, L = set(), ["\n**Legislação verificada nesta análise**\n",
                        "| Norma / dispositivo | O que fundamenta | Fonte | Consultado em |",
                        "|---|---|---|---|"]
    for e, a in evs:
        chave = (e.ref, e.localizacao)
        if chave in vistos:
            continue
        vistos.add(chave)
        fonte = f"[link]({e.link})" if e.link else e.ref
        L.append(f"| {e.localizacao or e.ref} | {a.texto[:110]} | {fonte} | "
                 f"{(e.consultado_em or e.data_do_documento or '—')[:10]} |")
    L.append("\n<sub>Legislação conferida em texto primário na data indicada. "
             "A vigência se reconfere a cada DD.</sub>\n")
    return "\n".join(L)


def _documentos_analisados(livro: Livro) -> str:
    """Tabela de rastreabilidade — a base do parecer inteiro (06-estrutura §3)."""
    cob = livro.cobertura or {}
    lidos = cob.get("lidos") or []
    nao = cob.get("nao_lidos_criticos") or []
    if not lidos and not nao:
        return ""
    L = ["\n| Documento | Disciplina | Situação | Link |", "|---|---|---|---|"]
    for d in lidos[:60]:
        link = f"[abrir]({d['link']})" if d.get("link") else "—"
        L.append(f"| {d['nome']} | {d.get('disciplina') or '—'} | analisado | {link} |")
    for d in nao[:30]:
        link = f"[abrir]({d['link']})" if d.get("link") else "—"
        L.append(f"| {d['nome']} | {d.get('disciplina') or '—'} | **NÃO ANALISADO** | {link} |")
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------- #

def render(livro: Livro, changelog: dict | None = None) -> str:
    """Parecer Técnico no formato oficial SZI, renderizado a partir do Livro."""
    p = livro.proveniencia or {}
    im = p.get("imovel") or {}
    con = p.get("conclusao") or {}
    val = p.get("validacao") or {}
    at = p.get("areas_tabela") or {}
    expo = p.get("exposicao") or {}
    perfil = livro.perfil

    L: list[str] = []
    L.append(f"# PARECER TÉCNICO – DUE DILIGENCE – {livro.nome.upper()}\n")
    L.append("> Elaborado pelo Auditor de DD Técnica a partir dos documentos do "
             "empreendimento, da base histórica da Seazone, do Diário de Lançamentos e da "
             "legislação vigente consultada. **Rascunho técnico — requer revisão humana.**\n")

    # ---- 1. IMÓVEL ----------------------------------------------------------
    L.append("## 1. IMÓVEL\n")
    L.append("| Item | Descrição |\n|---|---|")
    L.append(f"| **Inscrição** | {im.get('inscricoes') or '(pendente)'} |")
    L.append(f"| **Endereço** | {im.get('endereco') or '(pendente)'} |")
    L.append(f"| **Município** | {perfil.cidade or '(pendente)'}"
             f"{'/' + perfil.uf if perfil.uf else ''} |")
    L.append(f"| **Área total** | {im.get('area_matricula_total') or '(pendente)'} |")
    L.append(f"| **Matrícula** | {im.get('matriculas') or '(pendente)'} |")
    if perfil.regime_dominial:
        L.append(f"| **Regime dominial** | {perfil.regime_dominial} |")
    L.append("")

    # ---- 2. PROPRIETÁRIO ----------------------------------------------------
    L.append("## 2. PROPRIETÁRIO(A)\n")
    props = p.get("proprietarios") or []
    L += [f"- {x}" for x in props] if props else ["- (pendente)"]
    L.append(
        "\nTrata-se de parecer técnico acerca das diligências e da análise técnica "
        "realizada pelo Setor de Lançamentos da Seazone Investimentos em relação aos "
        "estudos de viabilidade referentes ao terreno e ao estudo preliminar desenvolvido, "
        "objetivando a aquisição do imóvel e a continuidade no processo de estruturação "
        "do empreendimento.\n")

    L.append("### Documentos analisados")
    L.append(_documentos_analisados(livro))
    L.append("Para realização da due diligence foram verificados, entre outros tópicos, "
             "código de obras, plano diretor e demais legislações vigentes.")
    L.append(_legislacao_verificada(livro))

    # ---- 3. CONCLUSÃO -------------------------------------------------------
    L.append("## 3. CONCLUSÃO\n")

    L.append("### LOCALIZAÇÃO\n")
    L.append("Visão geral de onde o empreendimento (modelo Spot) está inserido:\n")
    figs_loc = _figuras_da_secao(livro, "localizacao")
    L.append(figs_loc or "::FIG:: Localização / entorno do terreno\n")

    for chave, titulo in SECOES:
        texto = (con.get(chave) or "").strip()
        achados = _achados_da_secao(livro, chave)
        figs = _figuras_da_secao(livro, chave)
        if not texto and not achados and not figs:
            # Seção sem conteúdo NÃO é omitida — é declarada (06-estrutura-do-parecer).
            L.append(f"### {titulo}\n")
            L.append("_Sem documentação disponível nesta rodada. Ver seção de pendências._\n")
            continue
        L.append(f"### {titulo}\n")
        L.append(texto or "_Sem análise textual consolidada nesta rodada._")
        if chave == "topografia":
            L.append(_tabela_areas("Área de Matrícula", at.get("matricula") or [],
                                   "Referência (Inscrição Imobiliária)"))
            L.append(_tabela_areas("Área de Cadastro Imobiliário", at.get("cadastro_pmf") or [],
                                   "Referência (Inscrição Imobiliária)"))
            if at.get("topografico"):
                L.append("\n**Área Levantamento Topográfico**\n\n| Referência | Área (m²) |"
                         f"\n|---|---|\n| Área Real | {at['topografico']} |\n")
        if chave == "validacao_ep":
            if val.get("ajustes"):
                L.append("\n**Ajustes exigidos no anteprojeto**\n")
                L += [f"- {x}" for x in val["ajustes"]]
            if val.get("docs_aprovacao"):
                L.append("\n**Documentos para Aprovação do Projeto Arquitetônico**\n")
                L += [f"- {x}" for x in val["docs_aprovacao"]]
            if val.get("docs_alvara"):
                L.append("\n**Documentos para o Alvará de Construção**\n")
                L += [f"- {x}" for x in val["docs_alvara"]]
        L.append(achados)
        L.append(figs)

    # ---- Pendências ---------------------------------------------------------
    lac = livro.lacunas_abertas()
    if lac or livro.perguntas_ao_humano:
        L.append("### PENDÊNCIAS\n")
        L.append("Itens que impedem o fechamento da análise, com o responsável sugerido:\n")
        for a in sorted(lac, key=lambda x: 0 if x.severidade == "Crítico" else 1):
            quem = "**equipe Seazone**" if a.depende_de_humano else "fornecedor / disciplina"
            L.append(f"- {ICONE.get(a.severidade,'·')} **{a.texto}** — {a.o_que_falta or ''} "
                     f"({quem})")
            if a.como_obter:
                L.append(f"  - Como obter: {a.como_obter}")
        for q in livro.perguntas_ao_humano:
            L.append(f"- 👤 **{q.get('o_que_preciso','')}** — {q.get('para_que','')}")
        L.append("")

    # ---- Precedentes --------------------------------------------------------
    if livro.precedentes:
        L.append("### CASOS ANTERIORES COMPARÁVEIS\n")
        for pr in livro.precedentes:
            cab = pr.get("empreendimento", "—")
            if pr.get("distancia_ou_relacao"):
                cab += f" ({pr['distancia_ou_relacao']})"
            L.append(f"**{cab}** — {pr.get('o_que_aconteceu_la','')}")
            if pr.get("por_que_se_aplica_aqui"):
                L.append(f"Aplicação a este caso: {pr['por_que_se_aplica_aqui']}\n")
        L.append("<sub>Precedente embasa recomendação; não é fato sobre este terreno.</sub>\n")

    # ---- Conclusão final ----------------------------------------------------
    L.append("### CONCLUSÃO\n")
    L.append((con.get("final") or "").strip() or
             "_Conclusão não consolidada nesta rodada — ver pendências acima._")

    # ---- Leitura de negócio + decisão humana --------------------------------
    L.append("\n---\n")
    L.append("## LEITURA DE NEGÓCIO\n")
    if expo.get("situacao"):
        L.append(f"**Situação apurada:** {expo['situacao']}\n")
    if expo.get("divergencias"):
        L.append("**Divergências entre documentos**\n")
        L += [f"- {x}" for x in expo["divergencias"]]
        L.append("")
    if expo.get("pontos_de_atencao"):
        L.append("**Pontos de atenção**\n")
        L += [f"- {x}" for x in expo["pontos_de_atencao"]]
        L.append("")
    L.append(f"**Impacto em custo e prazo:** {expo.get('impacto_custo_prazo') or '—'}\n")
    if expo.get("o_que_falta_para_concluir"):
        L.append("**O que ainda falta para concluir**\n")
        L += [f"- {x}" for x in expo["o_que_falta_para_concluir"]]
        L.append("")

    crit = sum(1 for a in livro.achados() if a.severidade == "Crítico")
    aten = sum(1 for a in livro.achados() if a.severidade == "Atenção")
    L.append(f"**Quadro de criticidade:** {crit} achado(s) crítico(s), {aten} de atenção, "
             f"{len(lac)} pendência(s) aberta(s).\n")

    L.append("### RECOMENDAÇÃO\n")
    L.append("> A classificação **GO / GO COM RESSALVAS / NO-GO** é decisão humana. O "
             "Auditor apresenta acima a exposição técnica, as evidências e as pendências; "
             "a recomendação é assinada por quem responde pela análise.\n")
    L.append("| | |\n|---|---|")
    L.append("| **Recomendação** | ( ) GO   ( ) GO COM RESSALVAS   ( ) NO-GO |")
    L.append("| **Responsável** | ______________________________ |")
    L.append("| **Data** | ____ / ____ / ________ |")
    L.append("| **Justificativa** | |")

    cidade = f"{perfil.cidade}/{perfil.uf}" if perfil.cidade else "Florianópolis/SC"
    L.append(f"\n*{cidade}, {_hoje()}.*")
    L.append("*Setor de Projetos — Estruturação — Seazone Investimentos.*")

    # ---- Rodapé de rastreabilidade -----------------------------------------
    cob = livro.cobertura or {}
    L.append(f"\n---\n<sub>Auditor de DD Técnica v2 · rodada {livro.rodada} · "
             f"{p.get('documentos_lidos', 0)} de {cob.get('total', 0)} arquivos lidos · "
             f"{p.get('chamadas_de_ferramenta', 0)} consultas · "
             f"gerado em {livro.gerado_em[:19]}. "
             f"Rascunho técnico para revisão humana.</sub>")

    return "\n".join(x for x in L if x is not None)


def imagens_para_doc(livro: Livro, drive=None) -> dict[str, bytes]:
    """
    Baixa as figuras para embutir no .docx / Google Doc.

    Chaveado pela MESMA URL usada em `_fig()`, que é como `docs_writer` faz a
    substituição do markdown pela imagem real.
    """
    out: dict[str, bytes] = {}
    if drive is None:
        return out
    for i in ((livro.cobertura or {}).get("imagens") or [])[:12]:
        url = f"https://drive.google.com/thumbnail?id={i['id']}&sz=w900"
        try:
            data, _ = drive.download_file_by_id(i["id"], i.get("mime", "image/png"))
            out[url] = data
        except Exception:  # noqa: BLE001
            continue
    return out
