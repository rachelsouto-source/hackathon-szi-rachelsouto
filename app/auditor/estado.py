"""
Persistência do Auditor.

Motivo de existir: no v1 o resultado vivia num dict em memória (`_RESULTS`), perdido a
cada restart do container. Sem estado em disco não há changelog entre rodadas, não há
sessão de contestação e não há reprodutibilidade. Ver §4.3-D2.

Layout (raiz configurável por AUDITOR_DADOS_DIR; no Coolify, montar um volume):

    <dados>/
      <emp_id>/
        manifest.json           file_id -> modifiedTime da última varredura
        textos/<file_id>.txt    cache de EXTRAÇÃO (nunca de conclusão — §9.1)
        livros/<rodada>.json    Livro de cada rodada, imutável
        sessao.json             contestações e aceites do humano

Se o diretório não for gravável (ex.: container sem volume), tudo degrada para memória:
a auditoria continua funcionando, apenas sem histórico entre reinícios.
"""
from __future__ import annotations

import json
import os
import re
import threading
from pathlib import Path
from typing import Any

from .livro import Livro

_LOCK = threading.Lock()
_MEMORIA: dict[str, Any] = {}          # fallback quando não há disco
_AVISO_DISCO_EMITIDO = False


def raiz() -> Path:
    return Path(os.getenv("AUDITOR_DADOS_DIR", "/data/auditor")).expanduser()


def disco_disponivel() -> bool:
    global _AVISO_DISCO_EMITIDO
    try:
        raiz().mkdir(parents=True, exist_ok=True)
        p = raiz() / ".escrita"
        p.write_text("ok", encoding="utf-8")
        p.unlink(missing_ok=True)
        return True
    except Exception:  # noqa: BLE001
        if not _AVISO_DISCO_EMITIDO:
            print(f"[auditor] AVISO: {raiz()} não é gravável — histórico só em memória. "
                  f"Monte um volume e aponte AUDITOR_DADOS_DIR para ele.")
            _AVISO_DISCO_EMITIDO = True
        return False


def _slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s)[:120] or "sem-id"


def _dir_emp(emp_id: str) -> Path:
    d = raiz() / _slug(emp_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


# --------------------------------------------------------------------------- #
# Manifest — base da detecção de delta (§9.2)
# --------------------------------------------------------------------------- #

def ler_manifest(emp_id: str) -> dict[str, str]:
    if not disco_disponivel():
        return _MEMORIA.get(f"manifest:{emp_id}", {})
    p = _dir_emp(emp_id) / "manifest.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def gravar_manifest(emp_id: str, manifest: dict[str, str]) -> None:
    if not disco_disponivel():
        _MEMORIA[f"manifest:{emp_id}"] = manifest
        return
    (_dir_emp(emp_id) / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")


# --------------------------------------------------------------------------- #
# Cache de EXTRAÇÃO — texto de documento inalterado.
# Nunca cacheia conclusão: reutilizar conclusão é exatamente o bug P1. Ver §4.3-D6.
# --------------------------------------------------------------------------- #

def texto_cache(emp_id: str, file_id: str, modified: str) -> str | None:
    chave = f"texto:{emp_id}:{file_id}:{modified}"
    if not disco_disponivel():
        return _MEMORIA.get(chave)
    p = _dir_emp(emp_id) / "textos" / f"{_slug(file_id)}.json"
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return d.get("texto") if d.get("modified") == modified else None
    except Exception:  # noqa: BLE001
        return None


def gravar_texto_cache(emp_id: str, file_id: str, modified: str, texto: str) -> None:
    chave = f"texto:{emp_id}:{file_id}:{modified}"
    if not disco_disponivel():
        _MEMORIA[chave] = texto
        return
    d = _dir_emp(emp_id) / "textos"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{_slug(file_id)}.json").write_text(
        json.dumps({"modified": modified, "texto": texto}, ensure_ascii=False),
        encoding="utf-8")


# --------------------------------------------------------------------------- #
# Livros — um por rodada, imutáveis (§9.2, passo 5)
# --------------------------------------------------------------------------- #

def proxima_rodada(emp_id: str) -> int:
    return (ultima_rodada(emp_id) or 0) + 1


def ultima_rodada(emp_id: str) -> int | None:
    if not disco_disponivel():
        ls = _MEMORIA.get(f"livros:{emp_id}", {})
        return max(ls) if ls else None
    d = _dir_emp(emp_id) / "livros"
    if not d.exists():
        return None
    ns = [int(p.stem) for p in d.glob("*.json") if p.stem.isdigit()]
    return max(ns) if ns else None


def ler_livro(emp_id: str, rodada: int | None = None) -> Livro | None:
    r = rodada or ultima_rodada(emp_id)
    if r is None:
        return None
    if not disco_disponivel():
        d = _MEMORIA.get(f"livros:{emp_id}", {}).get(r)
        return Livro.from_dict(d) if d else None
    p = _dir_emp(emp_id) / "livros" / f"{r}.json"
    if not p.exists():
        return None
    try:
        return Livro.from_dict(json.loads(p.read_text(encoding="utf-8")))
    except Exception:  # noqa: BLE001
        return None


def gravar_livro(livro: Livro) -> None:
    with _LOCK:
        if not disco_disponivel():
            _MEMORIA.setdefault(f"livros:{livro.emp_id}", {})[livro.rodada] = livro.to_dict()
            return
        d = _dir_emp(livro.emp_id) / "livros"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{livro.rodada}.json").write_text(livro.to_json(), encoding="utf-8")


def historico(emp_id: str) -> list[dict]:
    """Lista as rodadas já gravadas — alimenta o seletor de histórico no painel."""
    out = []
    ult = ultima_rodada(emp_id)
    for r in range(1, (ult or 0) + 1):
        lv = ler_livro(emp_id, r)
        if lv:
            out.append({
                "rodada": r, "gerado_em": lv.gerado_em,
                "criticos": sum(1 for a in lv.achados() if a.severidade == "Crítico"),
                "lacunas": len(lv.lacunas_abertas()),
            })
    return out


# --------------------------------------------------------------------------- #
# Sessão — contestações e aceites do humano (o "jogo", §1.3-I1)
# --------------------------------------------------------------------------- #

def ler_sessao(emp_id: str) -> dict:
    if not disco_disponivel():
        return _MEMORIA.get(f"sessao:{emp_id}", {"contestacoes": [], "aceites": []})
    p = _dir_emp(emp_id) / "sessao.json"
    if not p.exists():
        return {"contestacoes": [], "aceites": []}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {"contestacoes": [], "aceites": []}


def gravar_sessao(emp_id: str, sessao: dict) -> None:
    with _LOCK:
        if not disco_disponivel():
            _MEMORIA[f"sessao:{emp_id}"] = sessao
            return
        (_dir_emp(emp_id) / "sessao.json").write_text(
            json.dumps(sessao, ensure_ascii=False, indent=1), encoding="utf-8")
