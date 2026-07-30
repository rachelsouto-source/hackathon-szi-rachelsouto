"""
Livro de Evidências — o artefato central do Auditor v2.

O parecer NÃO é a unidade de trabalho: o Livro é. O parecer é uma renderização dele.

Regra inviolável: não existe Afirmação sem Evidência (exceto tipo="lacuna", que é
justamente a declaração de que falta evidência). Isso torna a rastreabilidade
estrutural em vez de cosmética — é impossível o modelo afirmar algo sem dizer de onde
tirou, porque o schema não aceita.

Ver docs/ARQUITETURA-AUDITOR-V2.md §4.1 e §14.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

# --------------------------------------------------------------------------- #
# Vocabulário controlado
# --------------------------------------------------------------------------- #

# Taxonomia fixa — espelha engine/schema.py de seazone-tech/base-conhecimento-dd-tecnica.
# É o que permite realimentar a base histórica sem tradução (ver §11.3).
DISCIPLINAS = [
    "ambiental", "urbanístico", "concessionárias", "incêndio", "sanitário",
    "patrimônio", "jurídico-cartorial", "topografia", "arquitetura-projeto",
    "engenharia", "negócio",
]

TipoAfirmacao = Literal["fato", "inferencia", "precedente", "hipotese", "lacuna"]
Estado = Literal["aberta", "confirmada", "refutada", "indeterminada"]
Severidade = Literal["OK", "Atenção", "Crítico"]
Confianca = Literal["alta", "media", "baixa"]

ORIGENS = [
    "documento_emp",    # documento da pasta do empreendimento
    "base_historica",   # linha granular / síntese da base do Vini
    "diario",           # Diário de Lançamentos (reunião ou Slack)
    "repo_lancamento",  # repositório do lançamento (quando existir)
    "fonte_externa",    # SPU/SPUNET, geoportal, web
    "legislacao",       # texto legal recuperado (nunca de memória)
    "humano",           # inserido/corrigido por pessoa
]

# Teto de confiança por origem. O Diário é fala de reunião e Slack — o material menos
# confiável de todos e o mais fácil de tratar como fato. Ver §13.4.
TETO_CONFIANCA = {
    "documento_emp": "alta",
    "legislacao": "alta",
    "fonte_externa": "alta",
    "humano": "alta",
    "base_historica": "media",
    "repo_lancamento": "media",
    "diario": "media",
}

_ORDEM_CONF = {"baixa": 0, "media": 1, "alta": 2}
_ORDEM_SEV = {"OK": 0, "Atenção": 1, "Crítico": 2}


# --------------------------------------------------------------------------- #
# Estruturas
# --------------------------------------------------------------------------- #

@dataclass
class Evidencia:
    """Uma prova. `trecho` é a citação literal — nome de arquivo não é evidência."""
    origem: str
    ref: str                          # file_id · id da granular · âncora do Diário · URL
    trecho: str                       # a citação literal
    link: str = ""
    localizacao: str = ""             # "p. 4" · "camada MCZ_LPM_TM" · "00:41:27"
    data_do_documento: str = ""
    # None ⇒ o documento de terceiro não declara sua própria fonte ⇒ dispara R10 (§1.3-I2)
    fonte_declarada_pelo_doc: str | None = None
    consultado_em: str = ""           # timestamp — importa para fonte externa

    def valida(self) -> list[str]:
        erros = []
        if self.origem not in ORIGENS:
            erros.append(f"origem inválida: {self.origem!r}")
        if not str(self.ref).strip():
            erros.append("evidência sem ref")
        if not str(self.trecho).strip():
            erros.append("evidência sem trecho literal (nome de arquivo não é evidência)")
        return erros


@dataclass
class Contestacao:
    """Um ataque à afirmação — do Contraditor ou de um humano."""
    autor: str                        # "contraditor" | "humano:rachel" | ...
    argumento: str
    veredito: str                     # "procede" | "improcede" | "inconclusivo"
    em: str = ""


@dataclass
class LinhaComparativa:
    """Uma linha do cruzamento: o mesmo parâmetro, neste caso e nos precedentes."""
    parametro: str                      # "Sondagem realizada", "Perfil", "NA", "Fundação"
    este_caso: str                      # "❌ não realizada" · "R$ 790 mil (verba padrão)"
    casos: dict[str, str] = field(default_factory=dict)   # {"Patacho (38 km)": "areia..."}
    implicacao: str = ""                # o que a diferença significa AQUI


@dataclass
class Comparativo:
    """
    Cruzamento de um tema deste empreendimento contra os casos anteriores.

    É a resposta ao vazio do formato anterior: precedente numa aba e achado em outra
    obrigava o leitor a fazer o join de cabeça. O valor está no join.
    """
    tema: str                           # "sondagem e fundação", "área de marinha"
    disciplina: str
    linhas: list[LinhaComparativa] = field(default_factory=list)
    premissa_de_trabalho: str = ""      # o que assumir enquanto o dado real não chega
    confianca_da_analogia: Confianca = "media"
    ressalva: str = ""                  # por que a analogia NÃO substitui o dado real
    fontes: list[str] = field(default_factory=list)   # ids de granulares / links


@dataclass
class Afirmacao:
    id: str
    disciplina: str
    texto: str
    tipo: TipoAfirmacao = "fato"
    confianca: Confianca = "media"
    evidencias: list[Evidencia] = field(default_factory=list)
    # Precedentes ANEXADOS a este achado — renderizados junto, não numa aba distante.
    comparativos: list[Comparativo] = field(default_factory=list)
    regra: str | None = None                    # "R1" ... "R10"
    premissa_normativa: str | None = None       # "DL 9.760/1946 art. 2º (preamar 1831)"
    depende_de: list[str] = field(default_factory=list)   # define o subgrafo a reabrir
    contestacoes: list[Contestacao] = field(default_factory=list)
    estado: Estado = "aberta"
    severidade: Severidade | None = None
    acao: str = ""                              # o que fazer a respeito
    # Só para tipo="lacuna":
    o_que_falta: str = ""
    como_obter: str = ""
    depende_de_humano: bool = False

    # -- validação ---------------------------------------------------------- #
    def valida(self) -> list[str]:
        erros = []
        if self.disciplina not in DISCIPLINAS:
            erros.append(f"{self.id}: disciplina inválida {self.disciplina!r}")
        if not self.texto.strip():
            erros.append(f"{self.id}: texto vazio")
        if self.tipo != "lacuna" and not self.evidencias:
            erros.append(f"{self.id}: afirmação sem evidência (proibido — §4.1)")
        for i, e in enumerate(self.evidencias):
            erros += [f"{self.id}.ev{i}: {m}" for m in e.valida()]
        return erros

    # -- regras derivadas --------------------------------------------------- #
    def confianca_efetiva(self) -> Confianca:
        """Nenhuma afirmação pode ser mais confiável que a melhor evidência que a sustenta."""
        if not self.evidencias:
            return "baixa"
        teto = max(
            (_ORDEM_CONF[TETO_CONFIANCA.get(e.origem, "media")] for e in self.evidencias),
            default=0,
        )
        return ["baixa", "media", "alta"][min(_ORDEM_CONF[self.confianca], teto)]

    def sem_fonte_declarada(self) -> bool:
        """R10: evidência de documento de terceiro que não declara a própria fonte."""
        return any(
            e.origem == "documento_emp" and e.fonte_declarada_pelo_doc is None
            for e in self.evidencias
        )

    def e_critica(self) -> bool:
        return self.severidade == "Crítico" or self.tipo == "lacuna"

    def chave(self) -> str:
        """Identidade semântica, estável entre rodadas — é o que permite o diff."""
        base = f"{self.disciplina}|{self.regra or ''}|{self.texto.strip().lower()[:160]}"
        return hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]


@dataclass
class PerfilCaso:
    """O enquadramento do caso — dirige a recuperação de precedentes (§10)."""
    emp_id: str = ""
    nome: str = ""
    cidade: str = ""
    uf: str = ""
    lat: float | None = None
    lon: float | None = None
    produto: str = ""                 # Spot / apart-hotel / retrofit
    regime_dominial: str = ""         # alodial / marinha / ocupação / aforamento
    instrumento_aquisicao: str = ""   # compra direta / incorporação prévia / permuta
    flags: list[str] = field(default_factory=list)  # marinha, APP, tombado, demolição, MP...

    def resumo(self) -> str:
        p = [f"{self.nome} ({self.emp_id})" if self.emp_id else self.nome]
        if self.cidade:
            p.append(f"{self.cidade}/{self.uf}" if self.uf else self.cidade)
        if self.produto:
            p.append(self.produto)
        if self.regime_dominial:
            p.append(f"regime: {self.regime_dominial}")
        if self.flags:
            p.append("flags: " + ", ".join(self.flags))
        return " · ".join(p)


@dataclass
class Livro:
    """Estado completo de uma auditoria, versionado."""
    emp_id: str
    nome: str
    rodada: int = 1
    gerado_em: str = ""
    perfil: PerfilCaso = field(default_factory=PerfilCaso)
    afirmacoes: list[Afirmacao] = field(default_factory=list)
    cobertura: dict[str, Any] = field(default_factory=dict)   # do Cartógrafo
    precedentes: list[dict] = field(default_factory=list)     # blocos citáveis
    perguntas_ao_humano: list[dict] = field(default_factory=list)
    ferramentas_usadas: list[dict] = field(default_factory=list)
    # Reprodutibilidade (§14.4)
    proveniencia: dict[str, Any] = field(default_factory=dict)

    # -- acesso ------------------------------------------------------------- #
    def por_id(self, aid: str) -> Afirmacao | None:
        return next((a for a in self.afirmacoes if a.id == aid), None)

    def criticas(self) -> list[Afirmacao]:
        return [a for a in self.afirmacoes if a.e_critica()]

    def lacunas(self) -> list[Afirmacao]:
        return [a for a in self.afirmacoes if a.tipo == "lacuna"]

    def lacunas_abertas(self) -> list[Afirmacao]:
        return [a for a in self.lacunas() if a.estado == "aberta"]

    def achados(self) -> list[Afirmacao]:
        """Afirmações que viram linha do parecer, ordenadas por severidade."""
        ach = [a for a in self.afirmacoes if a.tipo != "lacuna" and a.severidade]
        return sorted(ach, key=lambda a: -_ORDEM_SEV.get(a.severidade or "OK", 0))

    def dependentes_de(self, aid: str) -> list[str]:
        """Fecho transitivo — o subgrafo a reabrir quando alguém contesta (§4.1)."""
        alvo, fila = set(), [aid]
        while fila:
            cur = fila.pop()
            for a in self.afirmacoes:
                if cur in a.depende_de and a.id not in alvo:
                    alvo.add(a.id)
                    fila.append(a.id)
        return sorted(alvo)

    # -- validação e higiene ------------------------------------------------ #
    def valida(self) -> list[str]:
        erros, vistos = [], set()
        for a in self.afirmacoes:
            if a.id in vistos:
                erros.append(f"id duplicado: {a.id}")
            vistos.add(a.id)
            erros += a.valida()
        for a in self.afirmacoes:
            for d in a.depende_de:
                if d not in vistos:
                    erros.append(f"{a.id}: depende_de aponta para id inexistente {d!r}")
        return erros

    def aplicar_tetos(self) -> None:
        """Rebaixa confiança acima do teto da origem (§13.4) e marca R10."""
        for a in self.afirmacoes:
            a.confianca = a.confianca_efetiva()
            # Hipótese de baixa confiança não vira achado — vira lacuna. Ver §1.2-P6:
            # o problema não é só omitir, é preencher o vazio com palpite.
            if a.tipo == "hipotese" and a.confianca == "baixa" and a.severidade == "Crítico":
                a.severidade = "Atenção"

    # -- serialização ------------------------------------------------------- #
    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int | None = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @staticmethod
    def from_dict(d: dict) -> "Livro":
        def ev(x):
            return Evidencia(**{k: v for k, v in x.items() if k in Evidencia.__annotations__})

        def ct(x):
            return Contestacao(**{k: v for k, v in x.items() if k in Contestacao.__annotations__})

        def cp(x):
            campos = {k: v for k, v in x.items() if k in Comparativo.__annotations__}
            campos["linhas"] = [
                LinhaComparativa(**{k: v for k, v in l.items()
                                    if k in LinhaComparativa.__annotations__})
                for l in x.get("linhas", [])]
            return Comparativo(**campos)

        def af(x):
            campos = {k: v for k, v in x.items() if k in Afirmacao.__annotations__}
            campos["evidencias"] = [ev(e) for e in x.get("evidencias", [])]
            campos["contestacoes"] = [ct(c) for c in x.get("contestacoes", [])]
            campos["comparativos"] = [cp(c) for c in x.get("comparativos", [])]
            return Afirmacao(**campos)

        perfil = PerfilCaso(**{k: v for k, v in (d.get("perfil") or {}).items()
                               if k in PerfilCaso.__annotations__})
        base = {k: v for k, v in d.items()
                if k in Livro.__annotations__ and k not in {"afirmacoes", "perfil"}}
        return Livro(perfil=perfil, afirmacoes=[af(a) for a in d.get("afirmacoes", [])], **base)


# --------------------------------------------------------------------------- #
# Diff entre rodadas — o changelog é entrega, não efeito colateral (§9.3)
# --------------------------------------------------------------------------- #

def diff_livros(anterior: Livro | None, atual: Livro) -> dict[str, Any]:
    """
    Compara duas rodadas por `chave()` (identidade semântica, não por id).

    Devolve novos / fechados / agravados / aliviados / lacunas_novas / lacunas_fechadas.
    """
    if anterior is None:
        return {
            "primeira_rodada": True,
            "novos": [_res(a) for a in atual.achados()],
            "fechados": [], "agravados": [], "aliviados": [],
            "lacunas_novas": [_res(a) for a in atual.lacunas_abertas()],
            "lacunas_fechadas": [],
        }

    ant = {a.chave(): a for a in anterior.afirmacoes}
    cur = {a.chave(): a for a in atual.afirmacoes}

    novos, agravados, aliviados = [], [], []
    for k, a in cur.items():
        if a.tipo == "lacuna":
            continue
        if k not in ant:
            if a.severidade:
                novos.append(_res(a))
            continue
        b = ant[k]
        sa, sb = _ORDEM_SEV.get(a.severidade or "OK", 0), _ORDEM_SEV.get(b.severidade or "OK", 0)
        if sa > sb:
            agravados.append(_res(a) | {"de": b.severidade, "para": a.severidade})
        elif sa < sb:
            aliviados.append(_res(a) | {"de": b.severidade, "para": a.severidade})

    fechados = [_res(a) for k, a in ant.items()
                if k not in cur and a.tipo != "lacuna" and a.severidade in {"Crítico", "Atenção"}]

    lac_ant = {a.chave() for a in anterior.lacunas_abertas()}
    lac_cur = {a.chave(): a for a in atual.lacunas_abertas()}
    lacunas_novas = [_res(a) for k, a in lac_cur.items() if k not in lac_ant]
    lacunas_fechadas = [_res(a) for a in anterior.lacunas_abertas() if a.chave() not in lac_cur]

    return {
        "primeira_rodada": False,
        "rodada_anterior": anterior.rodada,
        "gerado_em_anterior": anterior.gerado_em,
        "novos": novos, "fechados": fechados,
        "agravados": agravados, "aliviados": aliviados,
        "lacunas_novas": lacunas_novas, "lacunas_fechadas": lacunas_fechadas,
    }


def _res(a: Afirmacao) -> dict:
    return {
        "id": a.id, "disciplina": a.disciplina, "severidade": a.severidade,
        "texto": a.texto, "regra": a.regra, "tipo": a.tipo,
    }


def diff_vazio_ou_com_mudanca(d: dict) -> bool:
    return any(d.get(k) for k in
               ("novos", "fechados", "agravados", "aliviados",
                "lacunas_novas", "lacunas_fechadas"))
