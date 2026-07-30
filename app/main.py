"""
Auditor de DD Técnica — API (FastAPI).

Esta camada é FINA de propósito: não contém lógica de auditoria. Tudo vive em
`auditor/pipeline.py`, que também é chamável por terminal, cron e skill (§4.3-D1).

O que mudou em relação ao v1:

  · SEMPRE REEXECUTA. Não existe endpoint que devolva parecer antigo. `POST /api/dd`
    dispara uma auditoria nova, que revarre o Drive e reconstrói o Livro do zero.
    Ver §9.1 — a causa do "ele pega o que já fez em algum momento".
  · JOB ASSÍNCRONO + POLLING. Com loop de ferramentas, uma DD leva de 5 a 20 minutos;
    um POST síncrono estoura o timeout do proxy (§4.3-D3).
  · /api/health DIZ O QUE FALTA. O v1 caía em DEMO silenciosamente e o painel exibia
    JSON estático versionado no repo, indistinguível do resultado real. Era a origem
    do problema nº 1.
"""
from __future__ import annotations

import json
import os
import threading
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from auditor import estado, parecer, pipeline, relatorio
from core import docs_writer

ROOT = Path(__file__).resolve().parent.parent
EXEMPLOS = ROOT / "claude.md" / "exemplos"
STATIC = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Auditor de DD Técnica — SZI Lançamentos")

_JOBS: dict[str, dict] = {}
_LOCK = threading.Lock()
_POOL = ThreadPoolExecutor(max_workers=int(os.getenv("DD_WORKERS", "2")))
LOGO_ID = os.getenv("LOGO_FILE_ID", "1QXKWeEZ9w8SVUq0lazUuRnBrnXJFsi9z")

# (id do demo, prefixo do arquivo em claude.md/exemplos, nome exibido)
DEMOS = [
    ("demo-jurere-iii", "jurere-iii", "Jurerê Spot III"),
    ("demo-farol-barra", "farol-barra", "Farol da Barra Spot"),
    ("demo-novo-campeche-iii", "novo-campeche", "Novo Campeche Spot III"),
    ("demo-sao-miguel", "sao-miguel", "São Miguel dos Milagres"),
]


# --------------------------------------------------------------------------- #
# Diagnóstico de capacidades — nada de degradar em silêncio
# --------------------------------------------------------------------------- #

def capacidades() -> dict[str, Any]:
    """
    Diz exatamente o que está ligado e o que falta para ligar o resto.

    Isto existe porque o app rodou semanas em modo demo servindo JSON congelado sem que
    ninguém percebesse. Agora a falta de cada credencial é visível e nomeada.
    """
    from auditor.fontes import diario as fdiario
    from auditor.fontes import historica as fhistorica

    try:
        from core import drive_client
        drive_ok = drive_client.is_configured()
    except Exception:  # noqa: BLE001
        drive_ok = False

    claude_ok = bool(os.getenv("ANTHROPIC_API_KEY"))
    diario_ok, diario_msg = fdiario.disponivel()
    base_ok, base_msg = fhistorica.disponivel()
    disco_ok = estado.disco_disponivel()

    itens = {
        "drive": {
            "ativo": drive_ok, "essencial": True,
            "falta": "" if drive_ok else
                     "GOOGLE_SERVICE_ACCOUNT_JSON (JSON inteiro da service account) e "
                     "EMPREENDIMENTOS_FOLDER_ID; a pasta precisa estar compartilhada "
                     "com o e-mail da service account.",
        },
        "claude": {
            "ativo": claude_ok, "essencial": True,
            "falta": "" if claude_ok else "ANTHROPIC_API_KEY",
        },
        "diario": {
            "ativo": diario_ok, "essencial": False, "falta": diario_msg,
            "beneficio": "riscos e decisões do time que não estão em documento nenhum",
        },
        "base_historica": {
            "ativo": base_ok, "essencial": False, "falta": base_msg,
            "beneficio": "comparação com casos anteriores (Patacho, Japaratinga…)",
        },
        "historico_em_disco": {
            "ativo": disco_ok, "essencial": False,
            "falta": "" if disco_ok else
                     f"volume gravável montado em {estado.raiz()} "
                     f"(ou AUDITOR_DADOS_DIR apontando para um)",
            "beneficio": "changelog entre rodadas e sessão de contestação persistente",
        },
    }
    forcado = os.getenv("DEMO_MODE", "").lower() in {"1", "true", "yes"}
    operante = drive_ok and claude_ok and not forcado
    return {
        "modo": "produção" if operante else "demo",
        "demo_forcado_por_env": forcado,
        "itens": itens,
        "faltando_essencial": [k for k, v in itens.items()
                               if v["essencial"] and not v["ativo"]],
    }


def demo_mode() -> bool:
    return capacidades()["modo"] == "demo"


@app.get("/api/health")
def health():
    c = capacidades()
    aviso = ""
    if c["modo"] == "demo":
        faltam = ", ".join(c["faltando_essencial"]) or "DEMO_MODE=1 está forçando o modo"
        aviso = (f"⚠️ MODO DEMO — os dados exibidos são EXEMPLOS FIXOS versionados no "
                 f"repositório, não o resultado de uma auditoria. Nada é lido do Drive e "
                 f"nenhuma análise roda. Falta: {faltam}.")
    return {"ok": True, "versao": "2.0", **c, "aviso": aviso}


@app.get("/api/logo")
def logo():
    if not demo_mode():
        try:
            from core import drive_client
            data, mime = drive_client.download_file_by_id(LOGO_ID, "image/png")
            return Response(content=data, media_type=mime or "image/png",
                            headers={"Cache-Control": "public, max-age=86400"})
        except Exception:  # noqa: BLE001
            pass
    return RedirectResponse(f"https://drive.google.com/thumbnail?id={LOGO_ID}&sz=w240")


# --------------------------------------------------------------------------- #
# Empreendimentos
# --------------------------------------------------------------------------- #

@app.get("/api/empreendimentos")
def empreendimentos():
    if demo_mode():
        # Lista só os exemplos cujos arquivos existem de fato neste build. Oferecer um
        # demo cujo JSON não está presente produz uma tela vazia que parece bug.
        return {"modo": "demo", "itens": [
            {"id": eid, "name": f"{nome} (EXEMPLO FIXO)"}
            for eid, slug, nome in DEMOS
            if (EXEMPLOS / f"{slug}-achados.json").exists()
        ]}
    from core import drive_client
    try:
        itens = drive_client.list_empreendimentos()
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"Erro ao listar empreendimentos: {e}")
    # Anexa o histórico de auditorias já realizadas
    for it in itens:
        emp_id = pipeline._extrair_emp_id(it["name"], it["id"])
        it["emp_id"] = emp_id
        ult = estado.ultima_rodada(emp_id)
        it["rodadas"] = ult or 0
        lv = estado.ler_livro(emp_id) if ult else None
        it["ultima_auditoria"] = lv.gerado_em if lv else ""
    return {"modo": "produção", "itens": itens}


# --------------------------------------------------------------------------- #
# Auditoria — job assíncrono. SEMPRE reexecuta.
# --------------------------------------------------------------------------- #

class DDRequest(BaseModel):
    id: str
    nome: str
    contraditor: bool = True


def _novo_job(emp_id: str, nome: str) -> str:
    jid = uuid.uuid4().hex[:10]
    with _LOCK:
        _JOBS[jid] = {"id": jid, "emp_id": emp_id, "nome": nome, "estado": "na_fila",
                      "progresso": [], "erro": None, "resultado": None}
    return jid


def _progresso(jid: str):
    def _p(msg: str):
        with _LOCK:
            j = _JOBS.get(jid)
            if j:
                j["progresso"].append(msg)
                j["progresso"] = j["progresso"][-60:]
    return _p


def _rodar(jid: str, folder_id: str, nome: str, contraditor: bool) -> None:
    with _LOCK:
        _JOBS[jid]["estado"] = "rodando"
    try:
        out = pipeline.auditar(folder_id, nome, progresso=_progresso(jid),
                               rodar_contraditor=contraditor)
        livro = out["livro"]
        resumo = out["resumo"]
        resumo["markdown"] = out["markdown"]
        resumo["parecer_md"] = out["parecer_md"]
        resumo["xlsx_url"] = f"/api/dd/{livro.emp_id}/xlsx"
        resumo["docx_url"] = f"/api/dd/{livro.emp_id}/docx"
        with _LOCK:
            _JOBS[jid]["estado"] = "pronto"
            _JOBS[jid]["resultado"] = resumo
    except Exception as e:  # noqa: BLE001
        traceback.print_exc()
        with _LOCK:
            _JOBS[jid]["estado"] = "erro"
            _JOBS[jid]["erro"] = str(e)[:800]


@app.post("/api/dd")
def gerar_dd(req: DDRequest):
    """
    Dispara uma auditoria NOVA. Nunca devolve resultado anterior.

    Em modo demo devolve o exemplo fixo, mas explicitamente rotulado como tal.
    """
    if demo_mode():
        return {"modo": "demo", "job": None, "resultado": _demo(req.id),
                "aviso": health()["aviso"]}
    emp_id = pipeline._extrair_emp_id(req.nome, req.id)
    jid = _novo_job(emp_id, req.nome)
    _POOL.submit(_rodar, jid, req.id, req.nome, req.contraditor)
    return {"modo": "produção", "job": jid, "estado": "na_fila"}


@app.get("/api/dd/job/{jid}")
def job(jid: str):
    j = _JOBS.get(jid)
    if not j:
        raise HTTPException(404, "Job não encontrado.")
    return j


@app.get("/api/dd/{emp_id}/livro")
def livro(emp_id: str, rodada: int | None = None):
    """
    Lê um Livro JÁ GRAVADO. É consulta ao histórico — não substitui rodar de novo.
    """
    lv = estado.ler_livro(emp_id, rodada)
    if not lv:
        raise HTTPException(404, "Nenhuma auditoria gravada para este empreendimento.")
    anterior = estado.ler_livro(emp_id, lv.rodada - 1) if lv.rodada > 1 else None
    from auditor.livro import diff_livros
    return relatorio.resumo_api(lv, diff_livros(anterior, lv))


@app.get("/api/dd/{emp_id}/historico")
def historico(emp_id: str):
    return {"emp_id": emp_id, "rodadas": estado.historico(emp_id)}


# --------------------------------------------------------------------------- #
# Sessão de contestação — o "jogo" (§1.3-I1)
# --------------------------------------------------------------------------- #

class Contestacao(BaseModel):
    afirmacao_id: str
    argumento: str
    autor: str = "humano"


@app.post("/api/dd/{emp_id}/contestar")
def contestar(emp_id: str, body: Contestacao):
    try:
        return pipeline.contestar_afirmacao(
            emp_id, body.afirmacao_id, body.argumento, body.autor)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(400, str(e))


class Aceite(BaseModel):
    ids: list[str]
    autor: str = "humano"


@app.post("/api/dd/{emp_id}/aceitar")
def aceitar(emp_id: str, body: Aceite):
    try:
        return pipeline.aceitar_afirmacoes(emp_id, body.ids, body.autor)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(400, str(e))


@app.get("/api/dd/{emp_id}/base-conhecimento")
def linhas_base(emp_id: str):
    """
    Linhas prontas para a base histórica, no schema de engine/schema.py.

    Só inclui afirmações ACEITAS por uma pessoa (§11.2). Não escreve na base do Vini —
    o acesso é somente leitura; isto é insumo para PR.
    """
    linhas = pipeline.gerar_linhas_para_base(emp_id)
    return {"emp_id": emp_id, "total": len(linhas), "linhas": linhas,
            "nota": ("Somente afirmações aceitas por revisão humana. Entregar ao "
                     "responsável pela base (seazone-tech/base-conhecimento-dd-tecnica) "
                     "— este app não escreve lá.")}


# --------------------------------------------------------------------------- #
# Saídas
# --------------------------------------------------------------------------- #

def _achados_legado(resumo: dict) -> list[dict]:
    """Adapta os achados do Livro ao formato que a planilha de controle espera."""
    out = []
    for a in resumo.get("achados", []):
        ev = (a.get("evidencias") or [{}])[0]
        out.append({
            "etapa": a.get("disciplina", ""),
            "documento": ev.get("ref", ""),
            "status": {"Crítico": "Divergência", "Atenção": "Pendente"}.get(
                a.get("severidade"), "OK"),
            "severidade": a.get("severidade", "OK"),
            "observacao": a.get("texto", ""),
            "acao": a.get("acao", "—"),
            "fonte": ev.get("trecho", "")[:200],
            "link": ev.get("link", ""),
        })
    for l in resumo.get("lacunas", []):
        out.append({
            "etapa": l.get("disciplina", ""), "documento": "—",
            "status": "Pendente", "severidade": l.get("severidade", "Atenção"),
            "observacao": l.get("texto", ""), "acao": l.get("como_obter", "—"),
            "fonte": "lacuna declarada", "link": "",
        })
    return out


def _resumo_de(emp_id: str) -> dict:
    lv = estado.ler_livro(emp_id)
    if not lv:
        raise HTTPException(404, "Nenhuma auditoria gravada para este empreendimento.")
    r = relatorio.resumo_api(lv)
    r["markdown"] = relatorio.render_markdown(lv)      # área de trabalho
    r["parecer_md"] = parecer.render(lv)               # entregável oficial
    return r


@app.get("/api/dd/{emp_id}/xlsx")
def baixar_xlsx(emp_id: str):
    import unicodedata
    r = _resumo_de(emp_id)
    dados = docs_writer.gerar_xlsx_bytes(
        r["nome"], _achados_legado(r), "decisão humana — ver exposição técnica")
    base = (unicodedata.normalize("NFKD", f"controle-dd-{r['nome']}")
            .encode("ascii", "ignore").decode("ascii")).replace(" ", "_") or "controle-dd"
    return Response(
        content=dados,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{base}.xlsx"'})


@app.get("/api/dd/{emp_id}/docx")
def baixar_docx(emp_id: str):
    """Parecer Técnico oficial em .docx — o entregável, não a tela de auditoria."""
    import unicodedata
    r = _resumo_de(emp_id)
    imagens = None
    if not demo_mode():
        try:
            from core import drive_client
            imagens = parecer.imagens_para_doc(estado.ler_livro(emp_id), drive_client)
        except Exception:  # noqa: BLE001
            imagens = None
    dados = docs_writer.gerar_docx_bytes(r["nome"], r["parecer_md"], imagens)
    base = (unicodedata.normalize("NFKD", f"DD_Tecnica_{r['nome']}")
            .encode("ascii", "ignore").decode("ascii")).replace(" ", "_") or "DD_Tecnica"
    return Response(
        content=dados,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{base}.docx"'})


@app.post("/api/dd/{emp_id}/gdoc")
def gerar_gdoc(emp_id: str):
    if demo_mode():
        raise HTTPException(400, "Indisponível em modo demo.")
    r = _resumo_de(emp_id)
    from core import locator
    lv = estado.ler_livro(emp_id)
    folder = (lv.proveniencia or {}).get("folder_id") or ""
    destino = (locator.find_dd_folder(folder) or folder) if folder else ""
    if not destino:
        raise HTTPException(400, "Pasta de destino não identificada nesta rodada.")
    try:
        from core import drive_client
        doc = docs_writer.create_google_doc(
            destino, f"[{r['nome']}] DD Técnica (auto)", r["parecer_md"],
            images=parecer.imagens_para_doc(estado.ler_livro(emp_id), drive_client))
        return {"doc_url": doc.get("url", "")}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"Falha ao criar Google Doc: {e}")


# --------------------------------------------------------------------------- #
# Monitor — reexecução por mudança, não por completude
# --------------------------------------------------------------------------- #

@app.get("/api/monitor")
def monitor_status():
    """
    Varre os empreendimentos e diz quais MUDARAM desde a última auditoria.

    O critério do v1 ("tem todos os documentos e ainda não tem DD") estava errado por
    duas razões: (a) `list_files` não é recursivo, então nada era considerado completo e
    o monitor nunca disparava; (b) no modelo novo, auditoria incompleta é saída VÁLIDA —
    com as lacunas declaradas. O critério passa a ser mudança. Ver §9.4.
    """
    if demo_mode():
        return {"modo": "demo", "itens": []}
    from auditor import cartografo
    from core import drive_client
    out = []
    for emp in drive_client.list_empreendimentos():
        emp_id = pipeline._extrair_emp_id(emp["name"], emp["id"])
        try:
            inv = cartografo.varrer(emp["id"], drive_client)
            delta = cartografo.calcular_delta(emp_id, inv)
        except Exception as e:  # noqa: BLE001
            out.append({"id": emp["id"], "emp_id": emp_id, "nome": emp["name"],
                        "erro": str(e)[:200]})
            continue
        out.append({
            "id": emp["id"], "emp_id": emp_id, "nome": emp["name"],
            "arquivos": inv["total_arquivos"],
            "novos": len(delta["novos"]), "alterados": len(delta["alterados"]),
            "removidos": len(delta["removidos"]),
            "rodadas": estado.ultima_rodada(emp_id) or 0,
            "elegivel": delta["houve_mudanca"] or not estado.ultima_rodada(emp_id),
        })
    return {"modo": "produção", "itens": out}


@app.post("/api/monitor/run")
def monitor_run():
    """Dispara auditoria para todo empreendimento que mudou (chamável por cron)."""
    if demo_mode():
        return {"modo": "demo", "disparados": []}
    st = monitor_status()
    disparados = []
    for emp in st["itens"]:
        if emp.get("elegivel"):
            jid = _novo_job(emp["emp_id"], emp["nome"])
            _POOL.submit(_rodar, jid, emp["id"], emp["nome"], True)
            disparados.append({"nome": emp["nome"], "job": jid})
    return {"modo": "produção", "disparados": disparados, "total": len(disparados)}


# --------------------------------------------------------------------------- #
# Demo — mantido, mas impossível de confundir com produção
# --------------------------------------------------------------------------- #

def _comparativo_ilustrativo(achado: dict) -> list[dict]:
    """
    Mostra o FORMATO do cruzamento no modo demo, sem inventar dado técnico.

    Os exemplos fixos do repositório são texto corrido antigo — não têm os parâmetros
    comparáveis. Em produção o cruzamento é montado pelo agente a partir das granulares
    da base histórica. Aqui a estrutura aparece com os valores marcados como
    ilustrativos, para que dê para avaliar o layout sem que ninguém confunda um número
    de exemplo com número apurado de um empreendimento real.
    """
    texto = f"{achado.get('etapa','')} {achado.get('observacao','')}".lower()
    if not any(p in texto for p in ("sondagem", "fundação", "fundacao", "estrutura")):
        return []
    return [{
        "tema": "sondagem e fundação",
        "disciplina": "engenharia",
        "colunas": ["Patacho (a X km)", "Japaratinga (a Y km)"],
        "linhas": [
            {"parametro": "Sondagem realizada", "este_caso": "❌ não realizada",
             "valores": ["—", "—"],
             "implicacao": "risco geotécnico DESCONHECIDO, não baixo (R6.c)"},
            {"parametro": "Perfil do subsolo", "este_caso": "—",
             "valores": ["—", "—"], "implicacao": "define o tipo de fundação"},
            {"parametro": "Nível d'água", "este_caso": "—",
             "valores": ["—", "—"], "implicacao": "define necessidade de rebaixamento"},
            {"parametro": "Fundação adotada", "este_caso": "verba padrão",
             "valores": ["—", "—"],
             "implicacao": "se os vizinhos exigiram fundação profunda, a verba está baixa"},
            {"parametro": "Custo real da fundação", "este_caso": "previsto no handover",
             "valores": ["—", "—"], "implicacao": "calibra a verba deste caso"},
        ],
        "premissa_de_trabalho": "",
        "confianca_da_analogia": "baixa",
        "ressalva": ("EXEMPLO DE FORMATO — os valores não foram apurados. Em produção "
                     "estas células são preenchidas com os números reais das granulares "
                     "da base histórica (nº de furos, perfil, NA, tipo de fundação, "
                     "custo), e daí sai a premissa de trabalho."),
        "fontes": ["(demo — sem fonte)"],
    }]


def _demo(emp_id: str) -> dict:
    slug, nome = next(((s, n) for eid, s, n in DEMOS if eid == emp_id),
                      ("jurere-iii", "Jurerê Spot III"))
    try:
        achados = json.loads(
            (EXEMPLOS / f"{slug}-achados.json").read_text(encoding="utf-8"))["itens"]
        md = (EXEMPLOS / f"{slug}-parecer.md").read_text(encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        achados = []
        md = (f"**Exemplo indisponível neste build.** O arquivo "
              f"`claude.md/exemplos/{slug}-achados.json` não foi encontrado "
              f"({type(e).__name__}). Isto é uma falha do modo demo, não um "
              f"resultado de auditoria.")
    return {
        "demo": True,
        "nome": f"{nome} (EXEMPLO FIXO — não é uma auditoria)",
        "rodada": 0,
        "markdown": ("> ⚠️ **Este conteúdo é um exemplo estático versionado no "
                     "repositório.** Nenhum documento foi lido do Drive e nenhuma "
                     "análise foi executada.\n\n") + md,
        "achados": [{
            "id": f"DEMO-{i:03d}", "disciplina": a.get("etapa", ""),
            "texto": a.get("observacao", ""), "severidade": a.get("severidade", "OK"),
            "tipo": "fato", "acao": a.get("acao", ""), "confianca": "media",
            "estado": "aberta", "evidencias": [], "contestacoes": [],
            "comparativos": _comparativo_ilustrativo(a),
        } for i, a in enumerate(achados, 1)],
        "lacunas": [], "precedentes": [], "perguntas_ao_humano": [],
        "cobertura": {}, "changelog": {}, "trilha": [], "legislacao": [], "imagens": [],
        "parecer_md": ("> ⚠️ **Exemplo fixo do repositório.** Em produção, esta aba traz o "
                       "Parecer Técnico no formato oficial da Seazone (1. IMÓVEL, "
                       "2. PROPRIETÁRIO, 3. CONCLUSÃO com as seções por disciplina, "
                       "tabelas de área, figuras e o campo de recomendação para "
                       "assinatura).\n\n") + md,
        "contadores": {
            "criticos": sum(1 for a in achados if a.get("severidade") == "Crítico"),
            "atencao": sum(1 for a in achados if a.get("severidade") == "Atenção"),
            "ok": sum(1 for a in achados if a.get("severidade") == "OK"),
            "lacunas": 0, "documentos_lidos": 0, "nao_lidos_criticos": 0,
            "precedentes": 0, "consultas": 0,
        },
        "exposicao": {},
    }


# --------------------------------------------------------------------------- #

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(
        content=(STATIC / "index.html").read_text(encoding="utf-8"),
        headers={"Cache-Control": "no-cache, no-store, must-revalidate",
                 "Pragma": "no-cache", "Expires": "0"})


app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")
