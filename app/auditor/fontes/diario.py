"""
Conector do Diário de Lançamentos (seazone-tech/diario-lancamentos).

Por que é o melhor investimento do projeto: é ler markdown de um repositório Git — sem
API paga, sem custo de LLM — e o conteúdo é justamente o que falta ao Auditor: o que o
time SABE E TEME, e que não está em documento nenhum.

No 12235, o Diário já registrava (com link para a fonte) a suspensão de alvarás no SOUS
da Praia do Toque, a recomendação do MPF ao IMA/AL e ao cartório, e o risco de embargo.
Nada disso está em matrícula, EVA ou sondagem. Tudo é material de DD.

⚠️ Teto de confiança: o Diário é fala de reunião e mensagem de Slack — o material menos
confiável de todas as fontes. Ele GERA PERGUNTA, corrobora ou contradiz. Não conclui.
Ver docs/ARQUITETURA-AUDITOR-V2.md §13.4. O teto é aplicado em livro.TETO_CONFIANCA.
"""
from __future__ import annotations

import os
import re
import unicodedata
from pathlib import Path
from typing import Any

# Cada bullet do Diário carrega uma âncora estável — é o que permite citar a FRASE EXATA
# da reunião/Slack como evidência rastreável (§13.2).
RE_ANCORA = re.compile(r"<!--anc:([^:]+):([^:]+):([^>]+)-->")
RE_CABECALHO = re.compile(
    r"^###\s+(?P<icone>[^\w\s]*)\s*(?P<fonte>.+?)\s+·\s+`(?P<data>[^`]+)`"
    r"(?:\s+·\s+\[(?P<rotulo>[^\]]+)\]\((?P<link>[^)]+)\))?",
)
SECOES = {
    "riscos": ("riscos", "pontos de atenção", "pontos de atencao"),
    "decisoes": ("decisões", "decisoes"),
    "timeline": ("timeline", "linha do tempo", "histórico", "historico"),
}


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode("ascii")
    return s.lower().strip()


def repo_dir() -> Path | None:
    """Diretório local do repo do Diário (clonado/montado). Ver DIARIO_REPO_DIR."""
    d = os.getenv("DIARIO_REPO_DIR", "").strip()
    if d and Path(d).is_dir():
        return Path(d)
    # Convenção de fallback: repo irmão, útil em desenvolvimento local.
    for cand in (Path.cwd() / "diario-lancamentos",
                 Path.cwd().parent / "diario-lancamentos",
                 Path("/data/diario-lancamentos")):
        if (cand / "diarios").is_dir():
            return cand
    return None


def disponivel() -> tuple[bool, str]:
    if repo_dir():
        return True, ""
    if os.getenv("GITHUB_TOKEN"):
        return True, ""
    return False, (
        "Diário indisponível: defina DIARIO_REPO_DIR apontando para um clone de "
        "seazone-tech/diario-lancamentos, ou GITHUB_TOKEN com acesso de leitura ao repo."
    )


# --------------------------------------------------------------------------- #
# Leitura
# --------------------------------------------------------------------------- #

def _ler_via_github(emp_id: str) -> str | None:
    tok = os.getenv("GITHUB_TOKEN", "").strip()
    if not tok:
        return None
    try:
        import urllib.request
        base = "https://api.github.com/repos/seazone-tech/diario-lancamentos/contents/diarios"
        req = urllib.request.Request(
            base, headers={"Authorization": f"Bearer {tok}",
                           "Accept": "application/vnd.github.raw+json",
                           "User-Agent": "auditor-dd"})
        import json as _json
        with urllib.request.urlopen(req, timeout=20) as r:
            itens = _json.loads(r.read().decode("utf-8"))
        alvo = next((i for i in itens if str(i.get("name", "")).startswith(f"{emp_id}-")), None)
        if not alvo:
            return None
        req2 = urllib.request.Request(
            alvo["download_url"], headers={"Authorization": f"Bearer {tok}",
                                           "User-Agent": "auditor-dd"})
        with urllib.request.urlopen(req2, timeout=20) as r:
            return r.read().decode("utf-8")
    except Exception:  # noqa: BLE001
        return None


def texto_bruto(emp_id: str) -> str | None:
    d = repo_dir()
    if d:
        for p in (d / "diarios").glob(f"{emp_id}-*.md"):
            return p.read_text(encoding="utf-8")
        # emp_id pode vir com zeros à esquerda diferentes (0584 vs 584)
        for p in (d / "diarios").glob("*.md"):
            if p.stem.split("-")[0].lstrip("0") == str(emp_id).lstrip("0"):
                return p.read_text(encoding="utf-8")
    return _ler_via_github(emp_id)


def listar_empreendimentos() -> list[str]:
    d = repo_dir()
    if not d:
        return []
    return sorted(p.stem for p in (d / "diarios").glob("*.md"))


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #

def _secao_de(titulo: str) -> str | None:
    t = _norm(titulo)
    for chave, pistas in SECOES.items():
        if any(p in t for p in pistas):
            return chave
    return None


def parse(md: str) -> dict[str, Any]:
    """
    Extrai eventos do markdown do Diário.

    Cada evento: {secao, fonte, data, link, texto, ancora}. A âncora é o identificador
    estável do bullet — sobrevive a reordenações e é o `ref` da Evidência.
    """
    eventos: list[dict] = []
    secao_atual: str | None = None
    ctx: dict[str, str] = {}
    painel: dict[str, str] = {}

    for linha in md.splitlines():
        s = linha.strip()
        if s.startswith("## "):
            secao_atual = _secao_de(s[3:])
            ctx = {}
            continue
        if s.startswith("### "):
            m = RE_CABECALHO.match(s)
            ctx = {
                "fonte": (m.group("fonte").strip() if m else s[4:].strip()),
                "data": (m.group("data") if m else ""),
                "link": (m.group("link") or "" if m else ""),
            }
            continue
        if s.startswith("- ") and secao_atual:
            corpo = s[2:]
            anc = ""
            ma = RE_ANCORA.search(corpo)
            if ma:
                anc = f"anc:{ma.group(1)}:{ma.group(2)}:{ma.group(3)}"
                corpo = RE_ANCORA.sub("", corpo).strip()
            if corpo:
                eventos.append({
                    "secao": secao_atual,
                    "fonte": ctx.get("fonte", ""),
                    "data": ctx.get("data", ""),
                    "link": ctx.get("link", ""),
                    "texto": corpo,
                    "ancora": anc,
                })
        elif s.startswith("- **") and not secao_atual:
            m = re.match(r"- \*\*(.+?):\*\*\s*(.+)", s)
            if m:
                painel[m.group(1).strip()] = re.sub(r"\*+", "", m.group(2)).strip()

    return {"painel": painel, "eventos": eventos}


# --------------------------------------------------------------------------- #
# Consulta usada pela ferramenta do agente
# --------------------------------------------------------------------------- #

def consultar(emp_id: str, termo: str = "", secao: str = "", limite: int = 40) -> dict[str, Any]:
    ok, msg = disponivel()
    if not ok:
        return {"disponivel": False, "motivo": msg, "eventos": []}

    md = texto_bruto(emp_id)
    if md is None:
        return {"disponivel": True, "encontrado": False, "eventos": [],
                "motivo": f"Não há diário para o empreendimento {emp_id}."}

    d = parse(md)
    evs = d["eventos"]
    if secao:
        evs = [e for e in evs if e["secao"] == secao]
    if termo:
        t = _norm(termo)
        palavras = [p for p in t.split() if len(p) > 3]
        evs = [e for e in evs
               if t in _norm(e["texto"]) or any(p in _norm(e["texto"]) for p in palavras)]

    # Mais recentes primeiro (datas em dd/mm/aaaa).
    def _chave(e):
        try:
            d_, m_, a_ = e["data"].split("/")
            return (a_, m_, d_)
        except Exception:  # noqa: BLE001
            return ("0000", "00", "00")

    evs = sorted(evs, key=_chave, reverse=True)[:limite]

    return {
        "disponivel": True,
        "encontrado": True,
        "painel": d["painel"],
        "total_eventos": len(d["eventos"]),
        "eventos": evs,
        "nota": ("Diário é fala de reunião e Slack: teto de confiança MÉDIA. Use como "
                 "gerador de pergunta, corroboração ou contradição — nunca como fato "
                 "isolado sobre o terreno."),
    }
