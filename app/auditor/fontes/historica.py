"""
Base histórica — recuperação de precedentes.

Lê a planilha "Base de Conhecimento — DD Técnica (Seazone)" do repo do Vini
(seazone-tech/base-conhecimento-dd-tecnica): abas `aprendizados` (granular, append-only)
e `sintese` (derivada, 1 linha por emp_id × disciplina × categoria).

DECISÃO DE ARQUITETURA (§8.1): NÃO é RAG vetorial ingênuo.

A base já está estruturada e destilada — tem emp_id, disciplina, categoria, cidade, uf,
tema. Recuperar isso por similaridade de cosseno é PERDER informação já paga. E a
pergunta certa raramente é semântica: "sondagem do empreendimento mais próximo" é
geográfica; "exigência do CBMSC em apart-hotel" é um filtro; "o que deu errado" é
categoria ∈ {erro, gargalo}.

Fluxo (§8.2): roteamento por fatos → ranqueamento multi-critério → só então semântica.

⚠️ Escrita: NUNCA. Acesso é somente leitura (push: false no repo do Vini). A
realimentação vai para staging + PR — ver curador.py.
"""
from __future__ import annotations

import math
import os
import unicodedata
from typing import Any

# Pesos por disciplina (§10.2). O que torna um precedente relevante MUDA conforme a
# pergunta: subsolo é do lugar (distância); licenciamento é do órgão (município);
# marinha é do regime dominial; incêndio é norma estadual.
PESOS: dict[str, dict[str, float]] = {
    "engenharia":          {"geo": 5.0, "cidade": 2.0, "uf": 1.0, "regime": 0.5, "produto": 1.0, "porte": 1.0},
    "topografia":          {"geo": 4.0, "cidade": 2.0, "uf": 1.0, "regime": 3.0, "produto": 0.5, "porte": 0.5},
    "ambiental":           {"geo": 2.5, "cidade": 4.0, "uf": 2.0, "regime": 1.5, "produto": 1.0, "porte": 1.0},
    "urbanístico":         {"geo": 1.0, "cidade": 5.0, "uf": 1.5, "regime": 0.5, "produto": 1.5, "porte": 1.0},
    "jurídico-cartorial":  {"geo": 2.0, "cidade": 2.0, "uf": 2.0, "regime": 5.0, "produto": 0.5, "porte": 0.5},
    "incêndio":            {"geo": 0.5, "cidade": 1.0, "uf": 3.0, "regime": 0.0, "produto": 4.0, "porte": 2.0},
    "concessionárias":     {"geo": 2.0, "cidade": 4.5, "uf": 1.0, "regime": 0.0, "produto": 0.5, "porte": 1.0},
    "patrimônio":          {"geo": 2.0, "cidade": 4.0, "uf": 1.5, "regime": 0.5, "produto": 0.5, "porte": 0.5},
    "sanitário":           {"geo": 1.0, "cidade": 4.0, "uf": 1.5, "regime": 0.0, "produto": 1.5, "porte": 1.0},
    "arquitetura-projeto": {"geo": 0.5, "cidade": 2.0, "uf": 1.0, "regime": 0.5, "produto": 4.0, "porte": 2.5},
    "negócio":             {"geo": 0.5, "cidade": 1.5, "uf": 1.0, "regime": 2.0, "produto": 3.0, "porte": 3.0},
}
PESO_PADRAO = {"geo": 2.0, "cidade": 3.0, "uf": 1.5, "regime": 1.5, "produto": 1.5, "porte": 1.0}

# Casos que deram errado são minoria numérica e maioria em valor. Num ranking único eles
# são diluídos por dezenas de linhas de `conhecimento-geral`. Daí o bônus E o canal
# separado de negativos (§8.3). É a formalização do "são os que mais trazem aprendizados".
BONUS_DESFECHO_RUIM = 3.0
CATEGORIAS_NEGATIVAS = {"erro", "gargalo"}
PISTAS_DESFECHO_RUIM = ("perdid", "cancelad", "embarg", "indeferid", "suspens",
                        "negad", "arquivad", "caiu", "declinad")


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode("ascii")
    return s.lower().strip()


def sheet_id() -> str:
    return os.getenv("BASE_SHEET_ID", "").strip()


def disponivel() -> tuple[bool, str]:
    if not sheet_id():
        return False, ("Base histórica indisponível: defina BASE_SHEET_ID com o ID da "
                       "planilha 'Base de Conhecimento — DD Técnica (Seazone)' e "
                       "compartilhe-a (leitura) com o e-mail da service account.")
    return True, ""


# --------------------------------------------------------------------------- #
# Leitura das abas (Sheets API, mesma service account do Drive)
# --------------------------------------------------------------------------- #

_CACHE: dict[str, list[dict]] = {}


def _ler_aba(aba: str) -> list[dict]:
    if aba in _CACHE:
        return _CACHE[aba]
    ok, _ = disponivel()
    if not ok:
        return []
    try:
        from googleapiclient.discovery import build
        from core.drive_client import _credentials  # reaproveita a mesma credencial
        svc = build("sheets", "v4", credentials=_credentials(), cache_discovery=False)
        resp = svc.spreadsheets().values().get(
            spreadsheetId=sheet_id(), range=f"{aba}!A1:Z100000").execute()
        vals = resp.get("values", [])
    except Exception as e:  # noqa: BLE001
        print(f"[auditor] falha ao ler aba {aba}: {e}")
        return []
    if not vals:
        return []
    cab = [c.strip() for c in vals[0]]
    linhas = [dict(zip(cab, r + [""] * (len(cab) - len(r)))) for r in vals[1:]]
    _CACHE[aba] = linhas
    return linhas


def limpar_cache() -> None:
    _CACHE.clear()


def sinteses() -> list[dict]:
    return _ler_aba("sintese")


def aprendizados() -> list[dict]:
    return _ler_aba("aprendizados")


# --------------------------------------------------------------------------- #
# Ranqueamento (§10.2)
# --------------------------------------------------------------------------- #

def _dist_km(a: tuple[float, float] | None, b: tuple[float, float] | None) -> float | None:
    if not a or not b or None in a or None in b:
        return None
    R = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def _desfecho_ruim(txt: str) -> bool:
    t = _norm(txt)
    return any(p in t for p in PISTAS_DESFECHO_RUIM)


def _score(linha: dict, perfil, disciplina: str, coords: dict) -> tuple[float, list[str]]:
    w = PESOS.get(disciplina, PESO_PADRAO)
    s, porque = 0.0, []

    cid_l, uf_l = _norm(linha.get("cidade", "")), _norm(linha.get("uf", ""))
    cid_p, uf_p = _norm(perfil.cidade), _norm(perfil.uf)

    if cid_p and cid_p in cid_l:
        s += w["cidade"]; porque.append("mesma cidade")
    elif uf_p and uf_p == uf_l:
        s += w["uf"]; porque.append("mesmo estado")

    d = _dist_km((perfil.lat, perfil.lon), coords.get(str(linha.get("emp_id", "")).strip()))
    if d is not None:
        s += w["geo"] / (1 + d / 10.0)
        porque.append(f"{d:.0f} km")

    if perfil.regime_dominial:
        alvo = _norm(perfil.regime_dominial)
        if alvo and alvo in _norm(f"{linha.get('tema','')} {linha.get('sintese','')} "
                                 f"{linha.get('resumo','')}"):
            s += w["regime"]; porque.append("mesmo regime dominial")

    if perfil.produto and _norm(perfil.produto).split()[0:1]:
        if _norm(perfil.produto).split()[0] in _norm(linha.get("empreendimento", "")):
            s += w["produto"]; porque.append("mesmo produto")

    if linha.get("categoria") in CATEGORIAS_NEGATIVAS or \
            _desfecho_ruim(f"{linha.get('desfecho','')} {linha.get('empreendimento','')}"):
        s += BONUS_DESFECHO_RUIM; porque.append("desfecho negativo (alto valor)")

    return s, porque


def _coords() -> dict[str, tuple[float, float]]:
    """
    Coordenadas por emp_id.

    ⚠️ A base do Vini hoje NÃO tem coluna de coordenadas (§7, `bc.vizinhos`). Enquanto
    não tiver, isto vem de AUDITOR_COORDS ("emp_id:lat,lon;...") e o critério geográfico
    simplesmente não pontua para quem não estiver lá — nunca inventa distância.
    """
    out: dict[str, tuple[float, float]] = {}
    for par in os.getenv("AUDITOR_COORDS", "").split(";"):
        par = par.strip()
        if not par or ":" not in par:
            continue
        emp, ll = par.split(":", 1)
        try:
            lat, lon = (float(x) for x in ll.split(","))
            out[emp.strip()] = (lat, lon)
        except Exception:  # noqa: BLE001
            continue
    return out


# --------------------------------------------------------------------------- #
# Consulta usada pela ferramenta do agente
# --------------------------------------------------------------------------- #

def buscar(perfil, disciplina: str, tema: str = "", limite_emp: int = 3,
           limite_linhas: int = 12) -> dict[str, Any]:
    ok, msg = disponivel()
    if not ok:
        return {"disponivel": False, "motivo": msg, "precedentes": []}

    sint = [s for s in sinteses() if _norm(s.get("disciplina", "")) == _norm(disciplina)]
    if not sint:
        return {
            "disponivel": True, "encontrado": False, "precedentes": [],
            "empreendimentos_na_base": sorted(
                {s.get("empreendimento", "") for s in sinteses() if s.get("empreendimento")}),
            "declaracao_de_ausencia": (
                f"Não há precedente na base para a disciplina '{disciplina}'. "
                f"Declarar a ausência é informação — silêncio é ambíguo (§10.3)."),
        }

    coords = _coords()
    proprio = _norm(perfil.emp_id)
    marcados = []
    for s in sint:
        if _norm(s.get("emp_id", "")) == proprio:
            continue                       # não é precedente de si mesmo
        sc, porque = _score(s, perfil, disciplina, coords)
        if tema and _norm(tema) in _norm(f"{s.get('sintese','')} {s.get('categoria','')}"):
            sc += 1.5; porque.append("tema compatível")
        marcados.append((sc, porque, s))

    marcados.sort(key=lambda x: -x[0])

    # Top-N empreendimentos distintos — "não leia 50 projetos a cada análise".
    escolhidos, vistos = [], set()
    for sc, porque, s in marcados:
        emp = s.get("emp_id", "")
        if emp in vistos:
            continue
        vistos.add(emp)
        escolhidos.append((sc, porque, s))
        if len(escolhidos) >= limite_emp:
            break

    # Nível 2/3: desce nas granulares dos escolhidos, via linhas_ref.
    granulares = aprendizados()
    por_id = {str(g.get("id", "")).strip(): g for g in granulares}
    precedentes = []
    for sc, porque, s in escolhidos:
        refs = [r.strip() for r in str(s.get("linhas_ref", "")).split(",") if r.strip()]
        linhas = [por_id[r] for r in refs if r in por_id][:limite_linhas]
        if not linhas:
            linhas = [g for g in granulares
                      if str(g.get("emp_id", "")).strip() == str(s.get("emp_id", "")).strip()
                      and _norm(g.get("disciplina", "")) == _norm(disciplina)][:limite_linhas]
        precedentes.append({
            "empreendimento": s.get("empreendimento", ""),
            "emp_id": s.get("emp_id", ""),
            "cidade": s.get("cidade", ""), "uf": s.get("uf", ""),
            "disciplina": s.get("disciplina", ""), "categoria": s.get("categoria", ""),
            "sintese": s.get("sintese", ""),
            "nota_humana": s.get("nota_humana", ""),
            "score": round(sc, 2),
            "por_que_este": ", ".join(porque) or "mesma disciplina",
            "granulares": [{
                "id": g.get("id", ""), "tema": g.get("tema", ""),
                "categoria": g.get("categoria", ""),
                "resumo": g.get("resumo", ""), "desfecho": g.get("desfecho", ""),
                "documento": g.get("documento", ""), "link": g.get("link", ""),
                "data_doc": g.get("data_doc", ""),
            } for g in linhas],
        })

    return {
        "disponivel": True, "encontrado": True,
        "precedentes": precedentes,
        "negativos": negativos(disciplina, perfil),
        "regra": ("Precedente NUNCA vira fato sobre este terreno — entra no Livro como "
                  "tipo='precedente'. O fato vem do documento do terreno."),
    }


def negativos(disciplina: str, perfil, limite: int = 8) -> list[dict]:
    """
    Canal separado de 'o que deu errado' — recuperado sem competir por ranking.

    Motivo (§8.3): é o sinal mais valioso e é minoria numérica; num ranking único ele
    desaparece sob linhas de `conhecimento-geral`.
    """
    out = []
    for g in aprendizados():
        if _norm(g.get("disciplina", "")) != _norm(disciplina):
            continue
        if g.get("categoria") not in CATEGORIAS_NEGATIVAS:
            continue
        if _norm(g.get("emp_id", "")) == _norm(perfil.emp_id):
            continue
        peso = 1.0
        if _norm(perfil.uf) and _norm(perfil.uf) == _norm(g.get("uf", "")):
            peso += 1.0
        if _norm(perfil.cidade) and _norm(perfil.cidade) in _norm(g.get("cidade", "")):
            peso += 1.5
        out.append((peso, {
            "empreendimento": g.get("empreendimento", ""), "emp_id": g.get("emp_id", ""),
            "cidade": g.get("cidade", ""), "uf": g.get("uf", ""),
            "categoria": g.get("categoria", ""), "tema": g.get("tema", ""),
            "resumo": g.get("resumo", ""), "desfecho": g.get("desfecho", ""),
            "link": g.get("link", ""), "id": g.get("id", ""),
        }))
    out.sort(key=lambda x: -x[0])
    return [d for _, d in out[:limite]]


def cobertura_da_base() -> dict[str, Any]:
    """
    O que a base REALMENTE tem — para o Auditor poder declarar ausência com honestidade.

    ⚠️ Estado conhecido em 06/07/2026: 4 empreendimentos (2595 Campeche, 6665 Jurerê,
    0584 Japaratinga, 2811 Jurerê Beach). A fila dos 68 restantes está PAUSADA por decisão
    do Vini — e o PATACHO está entre os 24 com sufixo PERDIDO dessa fila. Ou seja: a
    comparação com o Patacho pedida na revisão de 29/07 depende de o Vini retomar a fila.
    Ver §10.4 e a dependência E1 do roadmap.
    """
    s = sinteses()
    emps = {}
    for r in s:
        k = str(r.get("emp_id", "")).strip()
        if k:
            emps.setdefault(k, {"emp_id": k, "empreendimento": r.get("empreendimento", ""),
                                "cidade": r.get("cidade", ""), "uf": r.get("uf", ""),
                                "disciplinas": set()})
            emps[k]["disciplinas"].add(r.get("disciplina", ""))
    return {
        "empreendimentos": [{**v, "disciplinas": sorted(x for x in v["disciplinas"] if x)}
                            for v in emps.values()],
        "total_sinteses": len(s),
        "total_granulares": len(aprendizados()),
    }
