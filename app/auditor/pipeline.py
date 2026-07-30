"""
Pipeline — orquestra uma auditoria completa.

Ponto de entrada único do núcleo. API, CLI, painel, cron e skill chamam `auditar()`.
Nenhuma interface contém lógica de auditoria (§4.3-D1).

A REGRA DE OURO (§9.1): nenhuma conclusão é reutilizada, nunca. Toda execução reconstrói
o Livro do zero a partir das fontes. O que se reutiliza é apenas extração de texto de
documento inalterado — que é caro e imutável. É isto que resolve o "ele não roda de novo,
pega o que já fez em algum momento" (revisão de 29/07, 22:44).
"""
from __future__ import annotations

import datetime as _dt
import re
from typing import Any, Callable

from . import (agente, cartografo, estado, ferramentas, parecer, regras,
               relatorio)
from .livro import Livro, PerfilCaso, diff_livros

RE_EMP_ID = re.compile(r"\[(\d{3,6})\]")


def _extrair_emp_id(nome: str, fallback: str) -> str:
    """'1.43 - [6468] Jurerê Spot III' -> '6468'. Sem match, usa o folder_id."""
    m = RE_EMP_ID.search(nome or "")
    return m.group(1) if m else fallback


def _perfil_inicial(emp_id: str, nome: str) -> PerfilCaso:
    """
    Enquadramento mínimo antes de ler qualquer documento.

    Deliberadamente pobre: cidade/UF/regime saem dos DOCUMENTOS, não de heurística sobre
    o nome da pasta. Inferir cidade pelo nome do empreendimento seria exatamente o tipo
    de palpite que o sistema deve evitar.
    """
    return PerfilCaso(emp_id=emp_id, nome=nome)


def auditar(folder_id: str, nome: str, drive=None,
            progresso: Callable[[str], None] | None = None,
            rodar_contraditor: bool = True) -> dict[str, Any]:
    """
    Executa uma auditoria completa e devolve {livro, markdown, changelog, resumo}.

    `progresso` recebe mensagens curtas para a barra do painel.
    """
    aviso = progresso or (lambda _m: None)

    if drive is None:
        from core import drive_client as drive  # import tardio: só em produção

    emp_id = _extrair_emp_id(nome, folder_id)

    # --- FASE 1 · Cartógrafo: árvore inteira, sem whitelist ------------------
    aviso("varrendo a pasta do empreendimento…")
    inventario = cartografo.varrer(folder_id, drive)
    if not inventario["arquivos"]:
        raise RuntimeError(
            f"Nenhum arquivo encontrado em '{nome}'. Confirme se a pasta foi "
            f"compartilhada com o e-mail da service account.")

    delta = cartografo.calcular_delta(emp_id, inventario)
    aviso(f"{inventario['total_arquivos']} arquivos em {inventario['total_pastas']} pastas · "
          f"{len(delta['novos'])} novos, {len(delta['alterados'])} alterados")

    ctx = ferramentas.Contexto(
        emp_id=emp_id, nome=nome, inventario=inventario,
        perfil=_perfil_inicial(emp_id, nome), drive=drive)

    # --- FASE 2-5 · investigação com ferramentas -----------------------------
    aviso("investigando: lendo documentos, consultando Diário, base histórica e SPU…")
    mensagens = agente.investigar(ctx, delta, progresso=aviso)

    # --- FASE 6 · consolidação no Livro --------------------------------------
    aviso("consolidando o Livro de Evidências…")
    bruto = agente.consolidar(mensagens, ctx)
    rodada = estado.proxima_rodada(emp_id)
    livro = agente.montar_livro(bruto, ctx, rodada)

    # --- regras determinísticas ----------------------------------------------
    disparos = regras.aplicar(livro, ctx)
    if disparos:
        aviso("regras: " + "; ".join(disparos))
    livro.proveniencia["regras_disparadas"] = disparos

    erros = livro.valida()
    if erros:
        livro.proveniencia["avisos_de_validacao"] = erros[:40]

    # --- FASE 7 · Contraditor -------------------------------------------------
    if rodar_contraditor and any(a.severidade == "Crítico" for a in livro.achados()):
        aviso("contestando as afirmações críticas…")
        try:
            agente.contestar(livro, progresso=aviso)
        except Exception as e:  # noqa: BLE001
            livro.proveniencia["contraditor_falhou"] = str(e)[:300]

    # --- changelog + persistência --------------------------------------------
    anterior = estado.ler_livro(emp_id, rodada - 1) if rodada > 1 else None
    changelog = diff_livros(anterior, livro)
    changelog["documentos"] = {
        "novos": delta["novos"], "alterados": delta["alterados"],
        "removidos": delta["removidos"], "inalterados": delta["inalterados"],
    }

    estado.gravar_livro(livro)
    estado.gravar_manifest(emp_id, cartografo.manifest_de(inventario))

    # DOIS documentos, com propósitos diferentes (ver parecer.py):
    #   markdown → área de trabalho (painel): achados, cruzamentos, lacunas, cobertura
    #   parecer  → entregável oficial no template da Seazone, com figuras
    md = relatorio.render_markdown(livro, changelog)
    parecer_md = parecer.render(livro, changelog)
    aviso("parecer técnico pronto")

    resumo = relatorio.resumo_api(livro, changelog)
    resumo["parecer_md"] = parecer_md
    return {
        "livro": livro,
        "markdown": md,
        "parecer_md": parecer_md,
        "changelog": changelog,
        "resumo": resumo,
    }


# --------------------------------------------------------------------------- #
# Sessão de contestação — o "jogo" (§1.3-I1)
# --------------------------------------------------------------------------- #

def contestar_afirmacao(emp_id: str, afirmacao_id: str, argumento: str,
                        autor: str = "humano") -> dict[str, Any]:
    """
    Registra a contestação de uma pessoa e marca o subgrafo afetado para reabertura.

    Isto é o que o Vinícius descreveu em 42:01 — "eu analiso a resposta e falo 'não é bem
    isso', jogo de volta" — e o que torna a reabertura barata: só o que DEPENDE da
    afirmação contestada volta a ficar em aberto, não a auditoria inteira.
    """
    livro = estado.ler_livro(emp_id)
    if not livro:
        raise RuntimeError("Não há auditoria para este empreendimento.")
    alvo = livro.por_id(afirmacao_id)
    if not alvo:
        raise RuntimeError(f"Afirmação {afirmacao_id} não encontrada.")

    from .livro import Contestacao
    alvo.contestacoes.append(Contestacao(
        autor=autor, argumento=argumento, veredito="procede",
        em=_dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")))
    alvo.estado = "indeterminada"

    afetados = livro.dependentes_de(afirmacao_id)
    for aid in afetados:
        a = livro.por_id(aid)
        if a:
            a.estado = "aberta"

    estado.gravar_livro(livro)

    sessao = estado.ler_sessao(emp_id)
    sessao.setdefault("contestacoes", []).append({
        "afirmacao": afirmacao_id, "argumento": argumento, "autor": autor,
        "rodada": livro.rodada, "afetados": afetados,
        "em": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
    })
    estado.gravar_sessao(emp_id, sessao)

    return {
        "afirmacao": afirmacao_id,
        "afetados": afetados,
        "mensagem": (f"Contestação registrada. {len(afetados)} afirmação(ões) "
                     f"dependente(s) voltaram a ficar em aberto. Rode a auditoria "
                     f"novamente para reprocessá-las com o seu argumento em conta."),
    }


def aceitar_afirmacoes(emp_id: str, ids: list[str], autor: str = "humano") -> dict:
    """
    Marca afirmações como aceitas por uma pessoa.

    Gatilho do aprendizado contínuo (§11.2): NADA entra na base histórica porque o
    Auditor concluiu — entra porque um humano aceitou. Um sistema que aprende com as
    próprias saídas não validadas amplifica os próprios erros.
    """
    livro = estado.ler_livro(emp_id)
    if not livro:
        raise RuntimeError("Não há auditoria para este empreendimento.")
    aceitos = []
    for aid in ids:
        a = livro.por_id(aid)
        if a:
            a.estado = "confirmada"
            aceitos.append(aid)
    estado.gravar_livro(livro)

    sessao = estado.ler_sessao(emp_id)
    sessao.setdefault("aceites", []).append({
        "ids": aceitos, "autor": autor, "rodada": livro.rodada,
        "em": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
    })
    estado.gravar_sessao(emp_id, sessao)
    return {"aceitos": aceitos, "total": len(aceitos)}


# --------------------------------------------------------------------------- #
# Curador — realimentação da base histórica (§11.3)
# --------------------------------------------------------------------------- #

def gerar_linhas_para_base(emp_id: str) -> list[dict]:
    """
    Converte as afirmações ACEITAS em linhas no schema de `engine/schema.py`
    (seazone-tech/base-conhecimento-dd-tecnica).

    ⚠️ NÃO escreve na base: o acesso é somente leitura. A saída vai para staging e é
    entregue ao Vini por PR. `desfecho` sai vazio de propósito — ele só existe meses
    depois, e é a coluna mais valiosa do schema (§11.5).
    """
    livro = estado.ler_livro(emp_id)
    if not livro:
        return []

    mapa_categoria = {
        "Crítico": "gargalo",
        "Atenção": "exigência-de-órgão",
        "OK": "conhecimento-geral",
    }
    linhas = []
    for a in livro.afirmacoes:
        if a.estado != "confirmada" or a.tipo == "precedente":
            continue
        ev = a.evidencias[0] if a.evidencias else None
        linhas.append({
            "empreendimento": livro.nome,
            "emp_id": livro.emp_id,
            "cidade": f"{livro.perfil.cidade}, {livro.perfil.uf}"
                      if livro.perfil.cidade and livro.perfil.uf else "",
            "uf": livro.perfil.uf,
            "disciplina": a.disciplina,
            "categoria": mapa_categoria.get(a.severidade or "OK", "conhecimento-geral"),
            "tema": a.regra or a.disciplina,
            "resumo": a.texto,
            "desfecho": "",                     # preenchido depois — ver §11.5
            "documento": ev.ref if ev else "",
            "data_doc": ev.data_do_documento if ev else "",
            "fonte_extracao": f"auditor-dd v2 · rodada {livro.rodada}",
            "data_extracao": livro.gerado_em[:10],
            "link": ev.link if ev else "",
        })
    return linhas
