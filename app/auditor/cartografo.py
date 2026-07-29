"""
Cartógrafo — varredura EXAUSTIVA da pasta do empreendimento.

Substitui `core/locator.py`, cuja whitelist de 11 tipos de documento com caminhos fixos
tornava invisível tudo que não estivesse nela. No São Miguel isso significou não enxergar
`02 Projetos/03 Levantamento Topográfico/06 Confronto SPU` — a pasta onde estava a
resposta do caso. Ver docs/ARQUITETURA-AUDITOR-V2.md §1.4-B.

Aqui não há whitelist: varre a árvore inteira, classifica cada arquivo, e entrega o
inventário ao agente, que decide o que ler. Isso é o que torna R6.b ("varredura exaustiva
antes de concluir") executável — no v1 a regra estava no prompt e o código a impedia.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any

from . import estado

# Pastas historicamente ignoráveis. Note que uma pasta "OLD" VAZIA não é sinal de nada:
# R6.a — pasta não é documento.
IGNORAR_PASTAS = {"old", "00 - old", "demais arquivos", "antigos", "lixeira", ".tmp"}

PROFUNDIDADE_MAX = 8
MAX_ARQUIVOS = 4000

# Extensões que não carregam informação de auditoria (renders, fontes, binários de CAD
# que precisam de ferramenta própria). Continuam no inventário como "não aplicável" —
# ficam VISÍVEIS, apenas não entram na fila de leitura.
EXT_NAO_TEXTUAL = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff", ".webp", ".heic",
    ".mp4", ".mov", ".avi", ".zip", ".rar", ".7z", ".exe", ".ttf", ".otf",
    ".skp", ".3ds", ".max", ".blend", ".rvt", ".ifc",
}
EXT_CAD = {".dwg", ".dxf", ".dwl", ".dwl2", ".kmz", ".kml", ".shp", ".dbf", ".shx", ".prj"}


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode("ascii")
    return s.lower().strip()


def _ext(nome: str) -> str:
    m = re.search(r"(\.[A-Za-z0-9]{1,6})$", nome or "")
    return m.group(1).lower() if m else ""


# --------------------------------------------------------------------------- #
# Classificação por disciplina — heurística por caminho + nome.
# Não decide o que ler; só ajuda o agente a priorizar e alimenta a cobertura.
# --------------------------------------------------------------------------- #

PISTAS_DISCIPLINA: list[tuple[str, list[str]]] = [
    ("jurídico-cartorial", ["matricula", "matrícula", "inteiro teor", "onus", "ônus",
                            "certidao", "certidão", "escritura", "iptu", "cadastral",
                            "spu", "rip", "marinha", "aforamento", "juridic", "cnd",
                            "clicksign", "proposta", "compra e venda", "ccv", "contrato"]),
    ("topografia", ["topograf", "planialtim", "poligonal", "memorial", "georreferenc",
                    "confrontante", "curvas_nivel", "curvas de nivel", "confronto",
                    "prancha", "lpm", "ltm", "demarcac"]),
    ("ambiental", ["ambiental", "eva", "app", "supressao", "supressão", "vegetac",
                   "floram", "licenc", "ima", "auc", "danc", "manguezal", "mangue",
                   "fauna", "arboreo", "arbóreo", "compensac"]),
    ("urbanístico", ["viabilidade", "zoneamento", "plano diretor", "pdm", "pddu",
                     "consulta", "alvara", "alvará", "prefeitura", "pmf", "eiv",
                     "outorga", "tdc", "uso do solo", "habite-se"]),
    ("engenharia", ["sondagem", "spt", "fundac", "fundaç", "estrutura", "carga",
                    "geotecn", "laudo", "art", "rrt", "eletric", "hidro", "spda"]),
    ("incêndio", ["bombeiro", "cbmsc", "ppci", "incendio", "incêndio", "escada",
                  "brigada", "hidrante"]),
    ("arquitetura-projeto", ["arquitet", "estudo preliminar", "ep-", "ep_", "anteprojeto",
                             "estudo de massa", "premissas", "layout", "planta",
                             "pavimento", "implantac", "quadro de areas", "área"]),
    ("concessionárias", ["casan", "celesc", "comcap", "esgoto", "agua", "água",
                         "energia", "concession"]),
    ("negócio", ["viabilidade economica", "vgv", "financeir", "orcamento", "orçamento",
                 "custo", "handover"]),
    ("patrimônio", ["iphan", "sephan", "tombad", "arqueolog"]),
    ("sanitário", ["visa", "vigilancia sanitaria", "sanitari"]),
]


def classificar_disciplina(caminho: str, nome: str) -> str | None:
    alvo = _norm(f"{caminho} {nome}")
    for disc, pistas in PISTAS_DISCIPLINA:
        if any(p in alvo for p in pistas):
            return disc
    return None


def _relevancia(caminho: str, nome: str, mime: str) -> tuple[str, str]:
    """
    Devolve (situacao, motivo). situacao ∈ {"a_ler", "nao_aplicavel", "requer_ferramenta"}.

    Importante: "não aplicável" NUNCA some do inventário. R6.b — "existe e não foi lido"
    tem a mesma severidade de "não existe"; a diferença tem de ficar visível.
    """
    ext = _ext(nome)
    n = _norm(nome)
    if ext in EXT_CAD:
        return "requer_ferramenta", "arquivo CAD/geoespacial — exige ferramenta de geoprocessamento"
    if ext in EXT_NAO_TEXTUAL:
        return "nao_aplicavel", "imagem/mídia/binário sem texto auditável"
    if n.startswith("~$") or n.endswith(".tmp"):
        return "nao_aplicavel", "arquivo temporário"
    if "vnd.google-apps.form" in (mime or ""):
        return "nao_aplicavel", "formulário"
    return "a_ler", ""


# --------------------------------------------------------------------------- #
# Varredura
# --------------------------------------------------------------------------- #

def varrer(root_id: str, drive) -> dict[str, Any]:
    """
    Percorre a árvore inteira a partir da raiz do empreendimento.

    `drive` é o módulo/objeto com list_files(folder_id) -> [{id,name,mimeType,webViewLink,
    modifiedTime,size}]. Injetado para permitir teste sem rede.
    """
    arquivos: list[dict] = []
    pastas: list[dict] = []
    vistos: set[str] = set()

    def desce(fid: str, caminho: str, prof: int) -> None:
        if prof > PROFUNDIDADE_MAX or len(arquivos) >= MAX_ARQUIVOS or fid in vistos:
            return
        vistos.add(fid)
        try:
            filhos = drive.list_files(fid)
        except Exception as e:  # noqa: BLE001
            pastas.append({"caminho": caminho, "erro": str(e)[:200]})
            return
        for f in filhos:
            nome = f.get("name", "")
            if f.get("mimeType") == "application/vnd.google-apps.folder":
                sub = f"{caminho}/{nome}"
                pastas.append({"id": f["id"], "caminho": sub, "vazia": None})
                if _norm(nome) in IGNORAR_PASTAS:
                    continue
                desce(f["id"], sub, prof + 1)
            else:
                sit, motivo = _relevancia(caminho, nome, f.get("mimeType", ""))
                arquivos.append({
                    "id": f["id"],
                    "nome": nome,
                    "caminho": caminho,
                    "mime": f.get("mimeType", ""),
                    "link": f.get("webViewLink", ""),
                    "modificado": f.get("modifiedTime", ""),
                    "tamanho": int(f.get("size") or 0),
                    "disciplina": classificar_disciplina(caminho, nome),
                    "situacao": sit,
                    "motivo": motivo,
                    "lido": False,
                })

    desce(root_id, "", 0)

    # R6.a — pasta não é documento. Marcar as vazias explicitamente: subpasta de template
    # vazia é documento AUSENTE, não "disponível".
    com_conteudo = {a["caminho"] for a in arquivos}
    for p in pastas:
        if "erro" in p:
            continue
        cam = p["caminho"]
        p["vazia"] = not any(c == cam or c.startswith(cam + "/") for c in com_conteudo)

    return {
        "raiz": root_id,
        "arquivos": arquivos,
        "pastas": pastas,
        "total_arquivos": len(arquivos),
        "total_pastas": len([p for p in pastas if "erro" not in p]),
        "pastas_vazias": [p["caminho"] for p in pastas if p.get("vazia")],
        "erros_de_leitura": [p for p in pastas if "erro" in p],
        "truncado": len(arquivos) >= MAX_ARQUIVOS,
    }


# --------------------------------------------------------------------------- #
# Delta entre rodadas (§9.2)
# --------------------------------------------------------------------------- #

def manifest_de(inventario: dict) -> dict[str, str]:
    return {a["id"]: a.get("modificado", "") for a in inventario["arquivos"]}


def calcular_delta(emp_id: str, inventario: dict) -> dict[str, Any]:
    """
    Compara com a varredura anterior.

    Documento REMOVIDO é tão significativo quanto documento novo: as evidências que o
    citavam ficam órfãs e as afirmações apoiadas nelas voltam a "aberta" (§9.2, passo 2).
    """
    anterior = estado.ler_manifest(emp_id)
    atual = manifest_de(inventario)
    por_id = {a["id"]: a for a in inventario["arquivos"]}

    novos = [por_id[i] for i in atual if i not in anterior]
    alterados = [por_id[i] for i in atual
                 if i in anterior and anterior[i] != atual[i]]
    removidos = [i for i in anterior if i not in atual]

    return {
        "primeira_varredura": not anterior,
        "novos": [{"id": a["id"], "nome": a["nome"], "caminho": a["caminho"],
                   "modificado": a["modificado"]} for a in novos],
        "alterados": [{"id": a["id"], "nome": a["nome"], "caminho": a["caminho"],
                       "modificado": a["modificado"]} for a in alterados],
        "removidos": removidos,
        "inalterados": len(atual) - len(novos) - len(alterados),
        "houve_mudanca": bool(novos or alterados or removidos),
    }


# --------------------------------------------------------------------------- #
# Cobertura documental — a seção do parecer que torna R6.b auditável (§14.3)
# --------------------------------------------------------------------------- #

def cobertura(inventario: dict, lidos: set[str]) -> dict[str, Any]:
    arq = inventario["arquivos"]
    for a in arq:
        a["lido"] = a["id"] in lidos

    nao_lidos = [a for a in arq if a["situacao"] == "a_ler" and not a["lido"]]
    # Um não-lido cuja disciplina é conhecida é mais grave: significa que uma regra
    # daquela disciplina rodou sem uma fonte que existia.
    criticos = [a for a in nao_lidos if a["disciplina"] in
                {"jurídico-cartorial", "topografia", "ambiental", "urbanístico", "engenharia"}]

    return {
        "total": len(arq),
        "total_pastas": inventario["total_pastas"],
        "lidos": sorted(
            [{"nome": a["nome"], "caminho": a["caminho"], "disciplina": a["disciplina"],
              "link": a["link"]} for a in arq if a["lido"]],
            key=lambda x: x["caminho"]),
        "nao_lidos": sorted(
            [{"nome": a["nome"], "caminho": a["caminho"], "disciplina": a["disciplina"],
              "link": a["link"]} for a in nao_lidos],
            key=lambda x: x["caminho"]),
        "nao_lidos_criticos": [
            {"nome": a["nome"], "caminho": a["caminho"], "disciplina": a["disciplina"],
             "link": a["link"]} for a in criticos],
        "requer_ferramenta": [
            {"nome": a["nome"], "caminho": a["caminho"], "motivo": a["motivo"],
             "link": a["link"]} for a in arq if a["situacao"] == "requer_ferramenta"],
        "nao_aplicaveis": len([a for a in arq if a["situacao"] == "nao_aplicavel"]),
        "pastas_vazias": inventario["pastas_vazias"],
        "erros_de_leitura": inventario["erros_de_leitura"],
        "truncado": inventario.get("truncado", False),
    }


def resumo_para_prompt(inventario: dict, limite: int = 320) -> str:
    """
    Inventário em texto para o agente escolher o que ler.

    É deliberado entregar a árvore INTEIRA (e não uma seleção): a decisão do que é
    relevante passa a ser do agente, com justificativa registrada, em vez de uma
    whitelist de código que ninguém revisa.
    """
    arq = inventario["arquivos"]
    ordem = {"a_ler": 0, "requer_ferramenta": 1, "nao_aplicavel": 2}
    arq = sorted(arq, key=lambda a: (ordem.get(a["situacao"], 3), a["caminho"], a["nome"]))

    linhas = [f"ÁRVORE COMPLETA — {inventario['total_arquivos']} arquivos "
              f"em {inventario['total_pastas']} pastas"]
    if inventario["pastas_vazias"]:
        linhas.append(
            f"\nPASTAS VAZIAS ({len(inventario['pastas_vazias'])}) — R6.a: pasta vazia é "
            f"documento AUSENTE, não 'disponível':")
        linhas += [f"  (vazia) {c}" for c in inventario["pastas_vazias"][:60]]

    linhas.append(f"\nARQUIVOS (id · situação · disciplina · caminho/nome · modificado):")
    for a in arq[:limite]:
        d = a["disciplina"] or "—"
        tam = f" · {a['tamanho']//1024} KB" if a["tamanho"] else ""
        linhas.append(f"  {a['id']} · {a['situacao']} · {d} · "
                      f"{a['caminho']}/{a['nome']} · {a['modificado'][:10]}{tam}")
    if len(arq) > limite:
        linhas.append(f"  … e mais {len(arq)-limite} arquivos "
                      f"(use listar_arvore com filtro para vê-los)")
    if inventario["erros_de_leitura"]:
        linhas.append("\n⚠️ PASTAS QUE NÃO CONSEGUI LISTAR (trate como cobertura incompleta):")
        linhas += [f"  {p['caminho']}: {p['erro']}" for p in inventario["erros_de_leitura"][:20]]
    return "\n".join(linhas)
