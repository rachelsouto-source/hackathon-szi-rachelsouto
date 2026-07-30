"""
Regras determinísticas sobre o Livro.

Motivo de existir (§4.3-D4): comparar áreas e aplicar um gatilho de 3% é aritmética —
tem de ser código testável e reprodutível, não inferência de modelo. No v1, R1 era feita
pelo modelo: caro, não determinístico e impossível de testar.

Estas regras rodam DEPOIS da consolidação e são de dois tipos:
  · verificações que o modelo pode ter pulado (e que não dependem de julgamento);
  · higiene do Livro — garantir que o que chegou respeita os invariantes.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any

from .livro import Afirmacao, Evidencia, Livro

LIMITE_RETIFICACAO_PCT = 3.0

RE_AREA = re.compile(r"([\d]{1,3}(?:[.\s]\d{3})*(?:,\d+)?)\s*m²", re.I)
RE_RIP = re.compile(r"\b\d{4}[.\s-]?\d{7}[-.\s]?\d{2}\b")

PISTAS_MARINHA = ("marinha", "spu", "rip", "aforamento", "ocupacao da uniao",
                  "patrimonio da uniao", "preamar", "lpm", "acrescido")


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode("ascii")
    return s.lower()


def _num(txt: str) -> float | None:
    try:
        return float(txt.replace(".", "").replace(" ", "").replace(",", "."))
    except Exception:  # noqa: BLE001
        return None


def _proximo_id(livro: Livro, prefixo: str = "AR") -> str:
    n = sum(1 for a in livro.afirmacoes if a.id.startswith(prefixo)) + 1
    return f"{prefixo}-{n:03d}"


# --------------------------------------------------------------------------- #
# Aplicação
# --------------------------------------------------------------------------- #

def aplicar(livro: Livro, ctx=None) -> list[str]:
    """Muta o Livro, devolve a lista de regras que dispararam."""
    disparos: list[str] = []
    for regra in (_r_higiene, _r10_fonte_declarada, _r6b_nao_lidos,
                  _r_marinha_sem_spu, _r1_areas, _r_precedente_nao_e_fato,
                  _r_pastas_vazias, _r_cruzamento_faltando):
        try:
            msg = regra(livro, ctx)
            if msg:
                disparos.append(msg)
        except Exception as e:  # noqa: BLE001
            disparos.append(f"{regra.__name__}: erro ao aplicar ({e})")
    livro.aplicar_tetos()
    return disparos


# --------------------------------------------------------------------------- #

def _r_higiene(livro: Livro, ctx) -> str | None:
    """
    Invariante do §4.1: afirmação sem evidência não existe.

    Em vez de descartar (perderia informação), rebaixa para lacuna — que é o que ela
    realmente é: uma alegação sem prova.
    """
    convertidas = 0
    for a in livro.afirmacoes:
        if a.tipo != "lacuna" and not a.evidencias:
            a.tipo = "lacuna"
            a.o_que_falta = a.o_que_falta or f"Evidência que sustente: {a.texto[:180]}"
            a.como_obter = a.como_obter or "Localizar o documento-fonte e citar o trecho."
            a.severidade = a.severidade or "Atenção"
            convertidas += 1
    return (f"higiene: {convertidas} afirmação(ões) sem evidência rebaixada(s) a lacuna"
            if convertidas else None)


def _r10_fonte_declarada(livro: Livro, ctx) -> str | None:
    """
    R10 — documento de terceiro sem fonte declarada é achado.

    É a regra que nasceu da revisão de 29/07: a primeira pergunta feita ao material não
    foi sobre o terreno, foi "de onde ele tira essa linha?". Resposta: nem a planta nem o
    relatório citavam. O levantamento era metricamente ótimo e a premissa estava errada.
    """
    alvos = [a for a in livro.afirmacoes
             if a.tipo in ("fato", "inferencia")
             and a.severidade in ("Crítico", "Atenção")
             and a.sem_fonte_declarada()]
    if not alvos:
        return None

    for a in alvos:
        docs = sorted({e.ref for e in a.evidencias
                       if e.origem == "documento_emp" and e.fonte_declarada_pelo_doc is None})
        livro.afirmacoes.append(Afirmacao(
            id=_proximo_id(livro, "R10"),
            disciplina=a.disciplina,
            texto=(f"O documento que sustenta \"{a.texto[:120]}\" não declara a própria "
                   f"fonte nem a premissa normativa adotada."),
            tipo="inferencia",
            confianca="alta",
            severidade="Atenção" if a.severidade == "Atenção" else "Crítico",
            regra="R10",
            acao=("Exigir do fornecedor a fonte e a premissa normativa do dado. "
                  "Medição correta sobre premissa errada é o modo de falha mais caro "
                  "da DD — conferir especialmente premissas de data-base (ex.: terreno "
                  "de marinha se define pela preamar-média de 1831, DL 9.760/1946 "
                  "art. 2º, e não pela maré atual)."),
            depende_de=[a.id],
            evidencias=[e for e in a.evidencias if e.origem == "documento_emp"][:2],
        ))
    return f"R10: {len(alvos)} afirmação(ões) apoiada(s) em documento sem fonte declarada"


def _r6b_nao_lidos(livro: Livro, ctx) -> str | None:
    """
    R6.b — "existe e não foi lido" tem a mesma severidade de "não existe".

    Sem isto, a cobertura fica bonita no relatório e não produz consequência.
    """
    cob = livro.cobertura or {}
    criticos = cob.get("nao_lidos_criticos") or []
    if not criticos:
        return None
    por_disc: dict[str, list[dict]] = {}
    for a in criticos:
        por_disc.setdefault(a.get("disciplina") or "arquitetura-projeto", []).append(a)

    for disc, itens in por_disc.items():
        nomes = ", ".join(i["nome"] for i in itens[:6])
        livro.afirmacoes.append(Afirmacao(
            id=_proximo_id(livro, "R6B"),
            disciplina=disc,
            texto=(f"{len(itens)} documento(s) de {disc} existem na pasta e NÃO foram "
                   f"lidos nesta auditoria: {nomes}"
                   + (" …" if len(itens) > 6 else "")),
            tipo="lacuna",
            confianca="alta",
            severidade="Crítico",
            regra="R6.b",
            o_que_falta=f"Leitura dos documentos de {disc} listados.",
            como_obter=("Rodar nova auditoria priorizando esses arquivos, ou extrair o "
                        "texto manualmente se o formato exigir OCR/ferramenta."),
            evidencias=[Evidencia(
                origem="documento_emp", ref=i.get("link") or i["nome"],
                trecho=f"{i['caminho']}/{i['nome']}", link=i.get("link", ""),
                localizacao="não lido") for i in itens[:3]],
        ))
    return f"R6.b: {len(criticos)} documento(s) relevante(s) não lido(s)"


def _r_marinha_sem_spu(livro: Livro, ctx) -> str | None:
    """
    Se há indício de marinha, a consulta à SPU é obrigatória (R6 + R-MARINHA).

    Registra lacuna quando o agente não chamou `consultar_spu`.
    """
    corpus = _norm(
        " ".join(a.texto for a in livro.afirmacoes)
        + " " + " ".join(e.trecho for a in livro.afirmacoes for e in a.evidencias)
        + " " + " ".join(str(f) for f in (livro.perfil.flags or []))
        + " " + _norm(livro.perfil.regime_dominial))
    if not any(p in corpus for p in PISTAS_MARINHA):
        return None
    chamou = any(c.get("ferramenta") == "consultar_spu" for c in livro.ferramentas_usadas)
    if chamou:
        return None

    rips = RE_RIP.findall(" ".join(
        a.texto + " " + " ".join(e.trecho for e in a.evidencias) for a in livro.afirmacoes))
    livro.afirmacoes.append(Afirmacao(
        id=_proximo_id(livro, "SPU"),
        disciplina="jurídico-cartorial",
        texto=("Há indício de terreno de marinha e a situação junto à SPU não foi "
               "consultada nesta auditoria."
               + (f" RIP identificado: {rips[0]}." if rips else "")),
        tipo="lacuna",
        confianca="alta",
        severidade="Crítico",
        regra="R4/R6",
        depende_de_humano=True,
        o_que_falta=("Área da União no cadastro SPU, natureza do terreno, situação de "
                     "ocupação e taxa de ocupação (para VDP e laudêmio); e a situação de "
                     "homologação da demarcação NO TRECHO do imóvel."),
        como_obter=("Camadas e atributo de homologação: GeoPortal SPUNET (automatizável). "
                    "Área cadastral e histórico financeiro: portal SPU "
                    "(sistema.patrimoniodetodos.gov.br) — exige login gov.br Bronze+ e "
                    "captcha, portanto depende de uma pessoa do time."),
        evidencias=[Evidencia(
            origem="documento_emp", ref="indício textual",
            trecho="menção a marinha/RIP/aforamento nos documentos auditados",
            localizacao="conjunto do Livro")],
    ))
    return "marinha: indício presente sem consulta à SPU"


def _r1_areas(livro: Livro, ctx) -> str | None:
    """
    R1 — divergência de área entre matrícula e topográfico acima de 3% exige retificação.

    Aritmética pura: não depende do modelo. Só dispara quando os dois números foram
    efetivamente extraídos — nunca infere área ausente.
    """
    tabela = (livro.proveniencia or {}).get("areas_tabela") or {}
    topo = _num((RE_AREA.search(str(tabela.get("topografico", ""))) or [None]) and
                RE_AREA.search(str(tabela.get("topografico", ""))).group(1)) \
        if RE_AREA.search(str(tabela.get("topografico", ""))) else None

    mats = []
    for it in tabela.get("matricula", []) or []:
        m = RE_AREA.search(str(it.get("area", "")))
        if m:
            v = _num(m.group(1))
            if v:
                mats.append(v)
    if not topo or not mats:
        return None

    total = sum(mats)
    dif = abs(topo - total) / total * 100 if total else 0.0
    if dif <= LIMITE_RETIFICACAO_PCT:
        return None

    livro.afirmacoes.append(Afirmacao(
        id=_proximo_id(livro, "R1"),
        disciplina="topografia",
        texto=(f"Divergência de {dif:.2f}% entre a área do levantamento topográfico "
               f"({topo:,.2f} m²) e a soma das matrículas ({total:,.2f} m²), acima do "
               f"limite de {LIMITE_RETIFICACAO_PCT}%."
               .replace(",", "X").replace(".", ",").replace("X", ".")),
        tipo="inferencia",
        confianca="alta",
        severidade="Crítico",
        regra="R1",
        acao=("Exigir RETIFICAÇÃO DE ÁREA da matrícula antes do pedido de aprovação. "
              "Havendo mais de uma matrícula, avaliar amembramento."),
        evidencias=[Evidencia(
            origem="documento_emp", ref="areas_tabela",
            trecho=f"topográfico {topo:.2f} m² × matrícula(s) {total:.2f} m²",
            localizacao="tabela de áreas consolidada")],
    ))
    return f"R1: divergência de área de {dif:.2f}%"


def _r_precedente_nao_e_fato(livro: Livro, ctx) -> str | None:
    """Precedente nunca sustenta afirmação de fato sobre ESTE terreno (§8.3)."""
    corrigidas = 0
    for a in livro.afirmacoes:
        if a.tipo != "fato":
            continue
        origens = {e.origem for e in a.evidencias}
        if origens and origens <= {"base_historica", "diario", "repo_lancamento"}:
            a.tipo = "precedente" if "base_historica" in origens else "hipotese"
            a.confianca = "media" if a.confianca == "alta" else a.confianca
            corrigidas += 1
    return (f"{corrigidas} afirmação(ões) reclassificada(s): precedente/fala de reunião "
            f"não é fato sobre o terreno" if corrigidas else None)


def _r_pastas_vazias(livro: Livro, ctx) -> str | None:
    """R6.a — subpasta de template vazia é documento AUSENTE, não 'disponível'."""
    vazias = (livro.cobertura or {}).get("pastas_vazias") or []
    if len(vazias) < 3:
        return None
    livro.afirmacoes.append(Afirmacao(
        id=_proximo_id(livro, "R6A"),
        disciplina="arquitetura-projeto",
        texto=(f"{len(vazias)} subpasta(s) da estrutura do empreendimento estão VAZIAS — "
               f"são estrutura de template, não entrega. Ex.: "
               + "; ".join(vazias[:5]) + ("…" if len(vazias) > 5 else "")),
        tipo="lacuna",
        confianca="alta",
        severidade="Atenção",
        regra="R6.a",
        o_que_falta="Os documentos que deveriam ocupar essas pastas.",
        como_obter="Cobrar dos fornecedores/disciplinas responsáveis.",
        evidencias=[Evidencia(
            origem="documento_emp", ref="varredura",
            trecho="; ".join(vazias[:8]), localizacao="árvore de pastas")],
    ))
    return f"R6.a: {len(vazias)} pasta(s) vazia(s)"


def _r_cruzamento_faltando(livro: Livro, ctx) -> str | None:
    """
    Lacuna ou achado crítico SEM cruzamento, havendo precedente disponível na disciplina,
    é falha do próprio Auditor — não do terreno.

    Nasceu de uma crítica direta ao formato anterior: o achado dizia "verba de fundação
    em valor padrão, a confirmar após sondagem" e parava aí, quando havia sondagem feita
    em empreendimento próximo. O valor está no cruzamento; sem ele o parecer é uma lista
    de pendências, não uma análise.
    """
    if not livro.precedentes:
        return None      # sem precedente recuperado, não há o que cruzar

    orfas = [a for a in livro.afirmacoes
             if (a.tipo == "lacuna" or a.severidade == "Crítico")
             and not a.comparativos
             and not a.id.startswith(("R6B", "R6A", "R10"))]
    if not orfas:
        return None

    ids = ", ".join(a.id for a in orfas[:8])
    livro.afirmacoes.append(Afirmacao(
        id=_proximo_id(livro, "XRF"),
        disciplina="arquitetura-projeto",
        texto=(f"{len(orfas)} achado(s)/lacuna(s) crítica(s) ficaram SEM cruzamento com "
               f"os casos anteriores, embora haja precedente recuperado nesta auditoria "
               f"({ids}). O parecer perde a comparação justamente onde ela mais vale."),
        tipo="lacuna",
        confianca="alta",
        severidade="Atenção",
        regra="R-CRUZAMENTO",
        o_que_falta=("Quadro comparativo — mesmo parâmetro, este caso × casos anteriores "
                     "— e a premissa de trabalho decorrente."),
        como_obter=("Rodar a auditoria novamente; se persistir, verificar se a base "
                    "histórica cobre a disciplina em questão."),
        evidencias=[Evidencia(
            origem="base_historica", ref="auto-verificação",
            trecho=f"{len(livro.precedentes)} precedente(s) recuperado(s), "
                   f"{len(orfas)} achado(s) crítico(s) sem cruzamento",
            localizacao="Livro de Evidências")],
    ))
    return f"R-CRUZAMENTO: {len(orfas)} achado(s) crítico(s) sem comparativo"
