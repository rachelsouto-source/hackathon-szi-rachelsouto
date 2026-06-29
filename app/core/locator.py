"""
Localizador de documentos da DD na estrutura real de pastas do empreendimento.

Estrutura (confirmada no Drive da SZI):
  <Empreendimento>/
    02 - Projetos/
      02 - Viabilidade Técnica de Construção/
      03 - Levantamento Topográfico/            (+ subpasta "Certidão de confrontante")
      04 - Estudo Ambiental/
      05 - Projeto Arquitetônico/02 - Validação do estudo preliminar/
      07 - DD Técnica/                          (saída do parecer)
      08 - Sondagem/
      10 - Estrutura e Fundação/
    05 - Jurídico/                              (matrícula)
    04 - Comercial/ | 05 - Jurídico/            (proposta de compra e venda)

Para cada tipo de documento, navega o caminho (por nome, tolerante a variações), ignora
pastas OLD/Demais arquivos, e escolhe a ÚLTIMA VERSÃO em PDF (heurística de Rev/V + data).
Retorna nome + link + fileId + mime, para rastreabilidade no parecer.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any

from . import drive_client

IGNORAR_PASTAS = {"old", "00 - old", "demais arquivos", "antigos", "lixeira"}


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return s.lower().strip()


def _is_pdf(f: dict) -> bool:
    return f.get("mimeType") == "application/pdf" or f.get("name", "").lower().endswith(".pdf")


def _version_key(name: str) -> tuple:
    """Maior Rev/V e sufixo de letra => versão mais nova. Ex.: 'Rev06 B' > 'Rev06 A' > 'Rev05'."""
    n = name.lower()
    rev = re.search(r"\brev\.?\s*(\d+)\s*([a-z])?", n)
    ver = re.search(r"\bv\.?\s*(\d+)", n)
    num = int(rev.group(1)) if rev else (int(ver.group(1)) if ver else -1)
    letra = (rev.group(2) or "") if rev else ""
    return (num, letra)


def _pick_latest(files: list[dict], name_aliases: list[str] | None = None) -> dict | None:
    """Entre os arquivos, escolhe a última versão em PDF (preferindo nomes que casam aliases)."""
    cands = [f for f in files if f.get("mimeType") != "application/vnd.google-apps.folder"]
    if name_aliases:
        filt = [f for f in cands if any(a in _norm(f["name"]) for a in name_aliases)]
        cands = filt or cands
    pdfs = [f for f in cands if _is_pdf(f)]
    pool = pdfs or cands
    if not pool:
        return None
    pool.sort(key=lambda f: (_version_key(f["name"]), f.get("modifiedTime", "")), reverse=True)
    return pool[0]


def _children(folder_id: str) -> list[dict]:
    try:
        return drive_client.list_files(folder_id)
    except Exception:  # noqa: BLE001
        return []


def _find_subfolder(parent_id: str, aliases: list[str]) -> str | None:
    for f in _children(parent_id):
        if f["mimeType"] != "application/vnd.google-apps.folder":
            continue
        nn = _norm(f["name"])
        if nn in IGNORAR_PASTAS:
            continue
        if any(a in nn for a in aliases):
            return f["id"]
    return None


def _walk_path(root_id: str, path_aliases: list[list[str]]) -> str | None:
    """Desce por uma sequência de subpastas (cada nível = lista de aliases)."""
    cur = root_id
    for level in path_aliases:
        nxt = _find_subfolder(cur, level)
        if not nxt:
            return None
        cur = nxt
    return cur


def _all_files_recursive(folder_id: str, depth: int = 1) -> list[dict]:
    files = []
    for f in _children(folder_id):
        if f["mimeType"] == "application/vnd.google-apps.folder":
            if _norm(f["name"]) in IGNORAR_PASTAS or depth <= 0:
                continue
            files += _all_files_recursive(f["id"], depth - 1)
        else:
            files.append(f)
    return files


# tipo -> (caminho a partir da RAIZ do empreendimento, aliases de nome de arquivo, múltiplos?)
SOURCES: dict[str, dict[str, Any]] = {
    "viabilidade": {"path": [["02 - projetos", "projetos"], ["viabilidade"]],
                    "aliases": ["viabilidade"], "multi": False},
    "topografico": {"path": [["02 - projetos", "projetos"], ["topograf"]],
                    "aliases": ["prancha", "laudo", "topograf"], "multi": False},
    "confrontantes": {"path": [["02 - projetos", "projetos"], ["topograf"], ["confrontante"]],
                      "aliases": ["confrontante"], "multi": True},
    "ambiental": {"path": [["02 - projetos", "projetos"], ["ambiental"]],
                  "aliases": ["eva", "ambiental"], "multi": False},
    "validacao_ep": {"path": [["02 - projetos", "projetos"], ["arquitetonico", "arquitetônico"],
                              ["validacao", "validação"]],
                     "aliases": ["validac", "dd", "ep"], "multi": False},
    "sondagem": {"path": [["02 - projetos", "projetos"], ["sondagem"]],
                 "aliases": ["sondagem", "spt"], "multi": False},
    "estrutura": {"path": [["02 - projetos", "projetos"], ["estrutura"]],
                  "aliases": ["quantitativo", "carga", "estrutura"], "multi": False},
    "fundacao": {"path": [["02 - projetos", "projetos"], ["estrutura"]],
                 "aliases": ["fundac", "premissas de fundac"], "multi": False},
    "matricula": {"path": [["05 - juridico", "juridico", "jurídico"], ["terreno"],
                           ["documentos e certidoes", "documentos", "certidoes", "certidões"]],
                  "aliases": ["matricula", "matrícula", "inteiro teor", "certidao", "certidão"],
                  "multi": True, "depth": 2, "limit": 6},
    "proposta": {"path": [["05 - juridico", "juridico", "jurídico"], ["terreno"],
                          ["proposta de compra", "proposta"]],
                 "aliases": ["proposta", "compra e venda", "ccv", "compromisso"], "multi": False},
    "imagens": {"path": [["02 - projetos", "projetos"], ["imagens de drone", "imagens", "drone"]],
                "aliases": ["localiza", "panoram", "drone", "vista", "aerea", "aérea"],
                "multi": True, "depth": 0, "only_images": True, "limit": 4},
}


def find_dd_folder(empreendimento_root_id: str) -> str | None:
    """Pasta de saída do parecer: 02 - Projetos / 07 - DD Técnica."""
    return _walk_path(empreendimento_root_id, [["02 - projetos", "projetos"], ["dd tecnica", "dd", "07 - dd"]])


# tipo de documento -> palavras que aparecem na 'etapa' dos achados (para casar o link)
TIPO_PARA_ETAPA = {
    "matricula": ["matrícula", "matricula"],
    "cadastral": ["cadastral", "iptu"],
    "confrontantes": ["confrontante"],
    "viabilidade": ["viabilidade"],
    "topografico": ["topográfico", "topografico", "topografia"],
    "ambiental": ["ambiental", "eva"],
    "sondagem": ["sondagem"],
    "estrutura": ["estrutura"],
    "fundacao": ["fundação", "fundacao"],
    "validacao_ep": ["validação", "validacao", "ep"],
    "proposta": ["proposta", "compra e venda"],
}


def anexar_links(achados: list[dict], fontes: dict) -> None:
    """Anexa link/link2 E o NOME REAL do arquivo localizado a cada achado (rastreabilidade)."""
    for ach in achados:
        et = _norm(ach.get("etapa", ""))
        for tipo, palavras in TIPO_PARA_ETAPA.items():
            if any(_norm(p) in et for p in palavras):
                f = fontes.get(tipo)
                if isinstance(f, list) and f:
                    ach["link"] = f[0].get("link", "")
                    ach["fonte"] = " · ".join(x.get("nome", "") for x in f[:2]) or ach.get("fonte", "")
                    if len(f) > 1:
                        ach["link2"] = f[1].get("link", "")
                elif isinstance(f, dict) and f:
                    ach["link"] = f.get("link", "")
                    ach["fonte"] = f.get("nome", "") or ach.get("fonte", "")
                break


def _link(f: dict) -> dict:
    return {"nome": f["name"], "link": f.get("webViewLink", ""), "id": f["id"],
            "mime": f.get("mimeType", "")}


def localizar(empreendimento_root_id: str) -> dict[str, Any]:
    """Retorna {tipo: {nome, link, id, mime} | [..] | None} para cada documento da DD."""
    out: dict[str, Any] = {}
    for tipo, spec in SOURCES.items():
        # resolve a pasta (suporta caminhos alternativos via path_alts)
        folder_id = None
        for path in spec.get("path_alts", [spec.get("path", [])]):
            folder_id = _walk_path(empreendimento_root_id, path)
            if folder_id:
                break
        if not folder_id:
            out[tipo] = [] if spec.get("multi") else None
            continue
        files = _all_files_recursive(folder_id, depth=spec.get("depth", 1))
        files = [f for f in files if f["mimeType"] != "application/vnd.google-apps.folder"]
        if spec.get("only_images"):
            files = [f for f in files if (f.get("mimeType", "").startswith("image/")
                     or f["name"].lower().endswith((".png", ".jpg", ".jpeg")))]
        if spec.get("multi"):
            al = spec["aliases"]
            sel = [f for f in files if any(a in _norm(f["name"]) for a in al)] or files
            out[tipo] = [_link(f) for f in sel[:spec.get("limit", 6)]]
        else:
            best = _pick_latest(files, spec["aliases"])
            out[tipo] = _link(best) if best else None
    return out
