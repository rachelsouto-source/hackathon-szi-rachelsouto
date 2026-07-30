"""
Redator — renderiza o parecer A PARTIR do Livro.

Regra dura (§12.1): o Redator não escreve, ele renderiza. Se não há Afirmação, não há
frase. Isso elimina a categoria de erro em que o modelo produz prosa fluente e plausível
sobre algo que não verificou.

Consequência esperada e desejada: o parecer fica mais curto e mais desigual — denso onde
há evidência, explicitamente vazio onde não há.
"""
from __future__ import annotations

from typing import Any

from .livro import Afirmacao, Livro

ICONE = {"Crítico": "🔴", "Atenção": "🟡", "OK": "🟢"}
ICONE_ESTADO = {"confirmada": "✔ confirmada", "refutada": "✘ refutada",
                "indeterminada": "⚠ indeterminada", "aberta": "○ aberta"}


def _fmt_evidencia(e) -> str:
    partes = [f"**{e.origem}**"]
    if e.localizacao:
        partes.append(e.localizacao)
    if e.data_do_documento:
        partes.append(e.data_do_documento)
    cab = " · ".join(partes)
    trecho = (e.trecho or "").strip().replace("\n", " ")
    if len(trecho) > 400:
        trecho = trecho[:400] + "…"
    linha = f"  - {cab}: “{trecho}”"
    if e.link:
        linha += f" — [documento]({e.link})"
    if e.origem == "documento_emp" and e.fonte_declarada_pelo_doc is None:
        linha += "  ⚠️ *o documento não declara a própria fonte (R10)*"
    return linha


def _fmt_comparativo(c) -> str:
    """
    Renderiza o cruzamento como TABELA, dentro do achado.

    Precedente em aba separada obriga o leitor a fazer o join de cabeça — e o valor está
    justamente no join. Aqui o mesmo parâmetro aparece lado a lado: este caso × cada
    precedente, com a implicação da diferença.
    """
    if not c.linhas:
        return ""
    colunas = []
    for l in c.linhas:
        for k in l.casos:
            if k not in colunas:
                colunas.append(k)

    L = [f"\n  **⇄ Cruzamento — {c.tema}**\n"]
    L.append("  | Parâmetro | Este caso | " + " | ".join(colunas) + " | O que significa aqui |")
    L.append("  |---|---|" + "---|" * len(colunas) + "---|")
    for l in c.linhas:
        vals = " | ".join(l.casos.get(k, "—") for k in colunas)
        L.append(f"  | {l.parametro} | **{l.este_caso}** | {vals} | {l.implicacao} |")

    if c.premissa_de_trabalho:
        L.append(f"\n  → **Premissa de trabalho:** {c.premissa_de_trabalho} "
                 f"<sub>(analogia · confiança {c.confianca_da_analogia})</sub>")
    if c.ressalva:
        L.append(f"\n  ⚠️ {c.ressalva}")
    if c.fontes:
        L.append(f"\n  <sub>Fontes: {' · '.join(c.fontes[:6])}</sub>")
    return "\n".join(L)


def _fmt_afirmacao(a: Afirmacao, detalhado: bool = True) -> str:
    ic = ICONE.get(a.severidade or "", "·")
    cab = f"**{ic} [{a.id}] {a.texto}**"
    meta = [a.disciplina, a.tipo, f"confiança {a.confianca}"]
    if a.regra:
        meta.append(f"regra {a.regra}")
    if a.contestacoes:
        meta.append(ICONE_ESTADO.get(a.estado, a.estado))
    linhas = [cab, f"  <sub>{' · '.join(meta)}</sub>"]
    if a.premissa_normativa:
        linhas.append(f"  - Premissa normativa: {a.premissa_normativa}")
    if a.acao:
        linhas.append(f"  - **Ação:** {a.acao}")
    if detalhado:
        for e in a.evidencias:
            linhas.append(_fmt_evidencia(e))
        for comp in a.comparativos:
            linhas.append(_fmt_comparativo(comp))
        for c in a.contestacoes:
            if c.veredito != "improcede":
                linhas.append(f"  - *Contraditor ({c.veredito}):* {c.argumento}")
    return "\n".join(linhas)


def render_markdown(livro: Livro, changelog: dict | None = None) -> str:
    p = livro.proveniencia or {}
    imovel = p.get("imovel") or {}
    concl = p.get("conclusao") or {}
    expo = p.get("exposicao") or {}
    val = p.get("validacao") or {}
    areas = p.get("areas_tabela") or {}

    L: list[str] = []
    L.append(f"# DD Técnica — {livro.nome}")
    L.append(f"*Rodada {livro.rodada} · gerada em {livro.gerado_em} · "
             f"{p.get('documentos_lidos', 0)} documentos lidos · "
             f"{p.get('chamadas_de_ferramenta', 0)} consultas*\n")

    # ---- Exposição técnica (substitui a recomendação automática — §12.3) -----
    L.append("## Exposição técnica")
    if expo.get("situacao"):
        L.append(f"{expo['situacao']}\n")
    if expo.get("divergencias"):
        L.append("**Divergências encontradas**\n")
        L += [f"- {x}" for x in expo["divergencias"]]
        L.append("")
    if expo.get("pontos_de_atencao"):
        L.append("**Pontos de atenção**\n")
        L += [f"- {x}" for x in expo["pontos_de_atencao"]]
        L.append("")
    if expo.get("impacto_custo_prazo"):
        L.append(f"**Impacto de custo e prazo:** {expo['impacto_custo_prazo']}\n")
    if expo.get("o_que_falta_para_concluir"):
        L.append("**O que ainda falta para concluir**\n")
        L += [f"- {x}" for x in expo["o_que_falta_para_concluir"]]
        L.append("")
    L.append("> **A recomendação de GO / GO COM RESSALVAS / NO-GO é decisão humana.** "
             "O Auditor apresenta a exposição técnica e a evidência; quem assina a "
             "recomendação é a pessoa responsável pela análise.\n")

    # ---- Lacunas e perguntas (§12.2) ----------------------------------------
    lac = livro.lacunas_abertas()
    if lac or livro.perguntas_ao_humano:
        L.append("## ⚠️ Lacunas e o que falta")
        for a in sorted(lac, key=lambda x: 0 if x.severidade == "Crítico" else 1):
            ic = ICONE.get(a.severidade or "", "·")
            L.append(f"- {ic} **[{a.id}] {a.texto}**")
            if a.o_que_falta:
                L.append(f"  - Falta: {a.o_que_falta}")
            if a.como_obter:
                L.append(f"  - Como obter: {a.como_obter}")
            if a.depende_de_humano:
                L.append("  - 👤 **Depende de uma pessoa** (credencial, acesso ou decisão)")
            # Lacuna com caso comparável não para em "pendente": mostra o quadro e a
            # premissa de trabalho. É o que torna a pendência acionável.
            for comp in a.comparativos:
                L.append(_fmt_comparativo(comp))
        if livro.perguntas_ao_humano:
            L.append("\n### Perguntas ao humano")
            for q in livro.perguntas_ao_humano:
                L.append(f"- **{q.get('o_que_preciso','')}**")
                if q.get("para_que"):
                    L.append(f"  - Para: {q['para_que']}")
                if q.get("como_obter") or q.get("onde"):
                    L.append(f"  - Onde: {q.get('como_obter') or q.get('onde')}")
                if q.get("por_que_nao_automatico"):
                    L.append(f"  - Por que não é automático: {q['por_que_nao_automatico']}")
                if q.get("bloqueia"):
                    L.append(f"  - Bloqueia: {q['bloqueia']}")
        L.append("")

    # ---- Changelog (§9.3) ----------------------------------------------------
    if changelog and not changelog.get("primeira_rodada"):
        L.append(f"## Mudanças desde a rodada {changelog.get('rodada_anterior','anterior')}")
        docs = changelog.get("documentos") or {}
        if docs.get("novos") or docs.get("alterados") or docs.get("removidos"):
            L.append("\n**Documentos**\n")
            L += [f"- ➕ `{d['caminho']}/{d['nome']}` ({d['modificado'][:10]})"
                  for d in docs.get("novos", [])[:20]]
            L += [f"- 🔄 `{d['caminho']}/{d['nome']}` ({d['modificado'][:10]})"
                  for d in docs.get("alterados", [])[:20]]
            if docs.get("removidos"):
                L.append(f"- ➖ {len(docs['removidos'])} arquivo(s) removido(s)")
        blocos = [("🆕 Novos achados", "novos"), ("✅ Fechados", "fechados"),
                  ("⬆️ Agravados", "agravados"), ("⬇️ Aliviados", "aliviados"),
                  ("🆕 Lacunas novas", "lacunas_novas"),
                  ("✅ Lacunas fechadas", "lacunas_fechadas")]
        for titulo, chave in blocos:
            itens = changelog.get(chave) or []
            if itens:
                L.append(f"\n**{titulo}**\n")
                for i in itens[:15]:
                    extra = (f" ({i['de']} → {i['para']})" if i.get("de") else "")
                    L.append(f"- {ICONE.get(i.get('severidade') or '', '·')} "
                             f"[{i['id']}] {i['texto']}{extra}")
        if not any(changelog.get(c) for _, c in blocos):
            L.append("\nNenhuma mudança material nos achados.")
        L.append("")

    # ---- Identificação -------------------------------------------------------
    if imovel or p.get("proprietarios"):
        L.append("## 1. Imóvel")
        for rot, chave in (("Endereço", "endereco"), ("Inscrições", "inscricoes"),
                           ("Matrículas", "matriculas"),
                           ("Área total de matrícula", "area_matricula_total")):
            if imovel.get(chave):
                L.append(f"- **{rot}:** {imovel[chave]}")
        if p.get("proprietarios"):
            L.append("\n## 2. Proprietários")
            L += [f"- {x}" for x in p["proprietarios"]]
        L.append("")

    if areas:
        L.append("### Áreas confrontadas")
        L.append("\n| Fonte | Referência | Área |\n|---|---|---|")
        for it in areas.get("matricula", []) or []:
            L.append(f"| Matrícula | {it.get('ref','')} | {it.get('area','')} |")
        for it in areas.get("cadastro_pmf", []) or []:
            L.append(f"| Cadastro PMF | {it.get('ref','')} | {it.get('area','')} |")
        if areas.get("topografico"):
            L.append(f"| Levantamento topográfico | georreferenciado | {areas['topografico']} |")
        L.append("")

    # ---- Achados por severidade ---------------------------------------------
    achados = livro.achados()
    if achados:
        L.append("## 3. Achados de auditoria")
        for sev in ("Crítico", "Atenção", "OK"):
            grupo = [a for a in achados if a.severidade == sev]
            if not grupo:
                continue
            L.append(f"\n### {ICONE[sev]} {sev} ({len(grupo)})\n")
            for a in grupo:
                L.append(_fmt_afirmacao(a))
                L.append("")

    # ---- Precedentes (§8.4) --------------------------------------------------
    L.append("## 4. Precedentes consultados")
    if livro.precedentes:
        for pr in livro.precedentes:
            cab = pr.get("empreendimento", "—")
            if pr.get("emp_id"):
                cab += f" [{pr['emp_id']}]"
            if pr.get("distancia_ou_relacao"):
                cab += f" · {pr['distancia_ou_relacao']}"
            L.append(f"\n> **Precedente — {cab}**\n>")
            if pr.get("o_que_aconteceu_la"):
                L.append(f"> {pr['o_que_aconteceu_la']}\n>")
            if pr.get("por_que_se_aplica_aqui"):
                L.append(f"> **Aplicação a este caso:** {pr['por_que_se_aplica_aqui']}\n>")
            fonte = pr.get("fonte", "")
            if pr.get("link"):
                fonte += f" · [documento]({pr['link']})"
            if fonte:
                L.append(f"> <sub>Fonte: {fonte}</sub>")
        L.append("\n*Precedente não é prova: embasa recomendação, nunca fato sobre este "
                 "terreno.*")
    else:
        L.append("\n**Nenhum precedente foi recuperado para este caso.** Declarar a "
                 "ausência é informação — pode significar que a base ainda não cobre "
                 "casos comparáveis, e não que não existam.")
    L.append("")

    # ---- Conclusão por disciplina -------------------------------------------
    secoes = [("Topografia", "topografia"), ("Estudo prévio ambiental", "ambiental"),
              ("Viabilidade urbanística", "urbanistico"),
              ("Validação do estudo preliminar", "validacao_ep"),
              ("Sondagem", "sondagem"), ("Estrutura e fundação", "estrutura_fundacao"),
              ("Situação dominial", "juridico_dominial")]
    if any(concl.get(k) for _, k in secoes) or concl.get("final"):
        L.append("## 5. Conclusão")
        for titulo, chave in secoes:
            if concl.get(chave):
                L.append(f"\n### {titulo}\n\n{concl[chave]}")
        if concl.get("final"):
            L.append(f"\n### Conclusão final\n\n{concl['final']}")
        L.append("")

    if val.get("ajustes") or val.get("docs_aprovacao") or val.get("docs_alvara"):
        L.append("## 6. Ajustes e documentação")
        for titulo, chave in (("Ajustes exigidos no anteprojeto", "ajustes"),
                              ("Documentos para aprovação", "docs_aprovacao"),
                              ("Documentos para o alvará", "docs_alvara")):
            if val.get(chave):
                L.append(f"\n**{titulo}**\n")
                L += [f"- {x}" for x in val[chave]]
        L.append("")

    # ---- Cobertura documental (§14.3) ---------------------------------------
    L.append(render_cobertura(livro))

    # ---- Trilha (§14.4) ------------------------------------------------------
    if livro.ferramentas_usadas:
        L.append("\n## 8. Trilha de investigação\n")
        L.append("<details><summary>"
                 f"{len(livro.ferramentas_usadas)} consultas realizadas</summary>\n")
        for c in livro.ferramentas_usadas:
            L.append(f"- `{c['em'][:19]}` **{c['ferramenta']}** — {c['resumo']}")
        L.append("\n</details>")

    L.append(f"\n---\n<sub>Auditor de DD Técnica v2 · modelo {p.get('modelo','—')} · "
             f"rodada {livro.rodada}. Documento é rascunho técnico para revisão humana.</sub>")
    return "\n".join(L)


def render_cobertura(livro: Livro) -> str:
    c = livro.cobertura or {}
    if not c:
        return ""
    L = ["## 7. Cobertura documental",
         f"\nVarridos **{c.get('total', 0)} arquivos** em "
         f"{c.get('total_pastas', 0)} pastas.\n"]
    L.append(f"- ✅ **Lidos:** {len(c.get('lidos', []))}")
    L.append(f"- ⏭️ **Não aplicáveis:** {c.get('nao_aplicaveis', 0)} "
             f"(imagens, mídia, temporários)")
    req = c.get("requer_ferramenta") or []
    if req:
        L.append(f"- 🛠️ **Requerem ferramenta específica:** {len(req)} "
                 f"(CAD/geoespacial)")
        L += [f"    - `{x['caminho']}/{x['nome']}` — {x['motivo']}" for x in req[:8]]
    nl = c.get("nao_lidos") or []
    if nl:
        L.append(f"- ❌ **NÃO LIDOS:** {len(nl)}")
        crit = c.get("nao_lidos_criticos") or []
        if crit:
            L.append(f"    - ⚠️ **{len(crit)} de disciplina relevante** — "
                     f"“existe e não foi lido” tem a mesma severidade de "
                     f"“não existe” (R6.b):")
            for x in crit[:12]:
                link = f" ([abrir]({x['link']}))" if x.get("link") else ""
                L.append(f"        - `{x['caminho']}/{x['nome']}` "
                         f"({x.get('disciplina') or '—'}){link}")
    vaz = c.get("pastas_vazias") or []
    if vaz:
        L.append(f"- 📂 **Pastas vazias:** {len(vaz)} — pasta vazia é documento "
                 f"AUSENTE, não “disponível” (R6.a)")
        L += [f"    - `{v}`" for v in vaz[:10]]
    erros = c.get("erros_de_leitura") or []
    if erros:
        L.append(f"- 🚫 **Pastas que não puderam ser listadas:** {len(erros)} "
                 f"— cobertura incompleta")
    if c.get("truncado"):
        L.append("- ⚠️ **Varredura truncada pelo limite de arquivos** — a cobertura "
                 "acima não é completa.")
    return "\n".join(L)


def _comp_api(c) -> dict:
    """Comparativo em formato de tabela pronta para o painel."""
    colunas: list[str] = []
    for l in c.linhas:
        for k in l.casos:
            if k not in colunas:
                colunas.append(k)
    return {
        "tema": c.tema, "disciplina": c.disciplina,
        "colunas": colunas,
        "linhas": [{"parametro": l.parametro, "este_caso": l.este_caso,
                    "valores": [l.casos.get(k, "—") for k in colunas],
                    "implicacao": l.implicacao} for l in c.linhas],
        "premissa_de_trabalho": c.premissa_de_trabalho,
        "confianca_da_analogia": c.confianca_da_analogia,
        "ressalva": c.ressalva, "fontes": c.fontes,
    }


def resumo_api(livro: Livro, changelog: dict | None = None) -> dict[str, Any]:
    """Payload enxuto para o painel."""
    p = livro.proveniencia or {}
    return {
        "emp_id": livro.emp_id,
        "nome": livro.nome,
        "rodada": livro.rodada,
        "gerado_em": livro.gerado_em,
        "perfil": {
            "cidade": livro.perfil.cidade, "uf": livro.perfil.uf,
            "produto": livro.perfil.produto,
            "regime_dominial": livro.perfil.regime_dominial,
            "flags": livro.perfil.flags,
        },
        "exposicao": p.get("exposicao", {}),
        "contadores": {
            "criticos": sum(1 for a in livro.achados() if a.severidade == "Crítico"),
            "atencao": sum(1 for a in livro.achados() if a.severidade == "Atenção"),
            "ok": sum(1 for a in livro.achados() if a.severidade == "OK"),
            "lacunas": len(livro.lacunas_abertas()),
            "documentos_lidos": p.get("documentos_lidos", 0),
            "nao_lidos_criticos": len((livro.cobertura or {}).get("nao_lidos_criticos", [])),
            "precedentes": len(livro.precedentes),
            "consultas": p.get("chamadas_de_ferramenta", 0),
        },
        "achados": [{
            "id": a.id, "disciplina": a.disciplina, "texto": a.texto,
            "tipo": a.tipo, "severidade": a.severidade, "regra": a.regra,
            "acao": a.acao, "confianca": a.confianca, "estado": a.estado,
            "premissa_normativa": a.premissa_normativa,
            "depende_de": a.depende_de,
            "evidencias": [{
                "origem": e.origem, "trecho": e.trecho, "link": e.link,
                "localizacao": e.localizacao, "ref": e.ref,
                "sem_fonte_declarada": e.fonte_declarada_pelo_doc is None
                and e.origem == "documento_emp",
            } for e in a.evidencias],
            "contestacoes": [{"autor": c.autor, "veredito": c.veredito,
                              "argumento": c.argumento} for c in a.contestacoes],
            "comparativos": [_comp_api(c) for c in a.comparativos],
        } for a in livro.achados()],
        "lacunas": [{
            "id": a.id, "disciplina": a.disciplina, "texto": a.texto,
            "severidade": a.severidade, "o_que_falta": a.o_que_falta,
            "como_obter": a.como_obter, "depende_de_humano": a.depende_de_humano,
            "comparativos": [_comp_api(c) for c in a.comparativos],
        } for a in livro.lacunas_abertas()],
        "perguntas_ao_humano": livro.perguntas_ao_humano,
        "precedentes": livro.precedentes,
        "cobertura": livro.cobertura,
        "changelog": changelog or {},
        "trilha": livro.ferramentas_usadas,
    }
