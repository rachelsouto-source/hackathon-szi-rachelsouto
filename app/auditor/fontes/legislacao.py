"""
Legislação e portais de prefeitura.

Duas coisas que a revisão de 29/07 deixou em aberto e a Rachel cobrou depois:

1. **A base de legislação só existe para Florianópolis.** Transcrição, 20:32 —
   *"eu tenho um repositório do MVP Floripa, é como se fosse uma base de conhecimento de
   legislação de Floripa"*; 20:46, Vinícius: *"então ela não existe para Milagres"*;
   Rachel: *"não vai ter nível Brasil"*. Fora de Floripa, a legislação tem de vir de busca
   sobre TEXTO PRIMÁRIO no site do município, com verificação de vigência.

2. **O Auditor precisa acessar o site da prefeitura.** Este módulo mantém o registro de
   onde procurar por município e monta as consultas; a busca em si é feita pelas
   ferramentas de servidor `web_search` / `web_fetch` (ver ferramentas.py).

REGRA QUE ATRAVESSA TUDO: nunca citar lei ou parâmetro de memória. A fonte primária do
zoneamento é a **Viabilidade Técnica Construtiva emitida para o terreno**; a legislação é
fundamento, e a vigência se reconfere a cada DD.
"""
from __future__ import annotations

import unicodedata
from typing import Any

# Domínios oficiais por município. `web_search` e `web_fetch` são restritos a estes
# quando o município é conhecido — evita que o agente cite blog de imobiliária como lei.
PORTAIS: dict[str, dict[str, Any]] = {
    "florianopolis": {
        "municipio": "Florianópolis", "uf": "SC",
        "dominios": ["pmf.sc.gov.br", "leismunicipais.com.br", "floram.pmf.sc.gov.br",
                     "geo.pmf.sc.gov.br", "cm.sc.gov.br", "alesc.sc.gov.br"],
        "base_estruturada": True,
        "portais": {
            "Consulta de Viabilidade / Fins de Construção":
                "https://www.pmf.sc.gov.br/servicos/",
            "Geoportal (zoneamento, APP, restrições)": "https://geo.pmf.sc.gov.br/",
            "FLORAM (ambiental, supressão, DANC/AuC)": "https://www.pmf.sc.gov.br/entidades/floram/",
        },
        "leis_chave": [
            "LC 482/2014 — Plano Diretor de Florianópolis (com alterações)",
            "LC 739/2023 e LC 755/2023 — zoneamento e OODC",
            "LC 707/2021 — licenciamento declaratório (art. 7º: restrição ambiental exclui)",
            "Lei 11.029/2023 + Decreto 25.400/2023 — EIV",
            "IN FLORAM 04/2022 — subsolo em bairros específicos",
        ],
        "armadilhas": [
            "Incentivos podem ser EXCLUDENTES: uso misto exclui o TOx1,3 do Art. 70-A (R3.a).",
            "Teto de CA da tabela costuma só ser atingível COM TDC — calcular o teto sem (R3.b).",
            "Transição do IE 0,5→0,7 na OODC: conferir a regra por DATA DE PROTOCOLO.",
            "Consulta Ambiental costuma valer 90 dias — informar o vencimento.",
        ],
    },
    "sao miguel dos milagres": {
        "municipio": "São Miguel dos Milagres", "uf": "AL",
        "dominios": ["saomigueldosmilagres.al.gov.br", "leismunicipais.com.br",
                     "ima.al.gov.br", "al.gov.br", "mpf.mp.br"],
        "base_estruturada": False,
        "portais": {
            "Prefeitura": "https://saomigueldosmilagres.al.gov.br/",
            "IMA/AL (licenciamento ambiental estadual)": "https://www.ima.al.gov.br/",
        },
        "leis_chave": [],
        "armadilhas": [
            "Alvarás suspensos no SOUS da Praia do Toque (recomendação do MPF) — "
            "confirmar situação atual antes de qualquer prazo de licenciamento.",
            "Litoral: conferir terreno de marinha (SPU) além do zoneamento municipal.",
        ],
    },
    "maragogi": {
        "municipio": "Maragogi", "uf": "AL",
        "dominios": ["maragogi.al.gov.br", "leismunicipais.com.br", "ima.al.gov.br"],
        "base_estruturada": False,
        "portais": {"Prefeitura": "https://www.maragogi.al.gov.br/"},
        "leis_chave": [], "armadilhas": [],
    },
    "japaratinga": {
        "municipio": "Japaratinga", "uf": "AL",
        "dominios": ["japaratinga.al.gov.br", "leismunicipais.com.br", "ima.al.gov.br"],
        "base_estruturada": False,
        "portais": {"Prefeitura": "https://japaratinga.al.gov.br/"},
        "leis_chave": [], "armadilhas": [],
    },
    "porto de pedras": {
        "municipio": "Porto de Pedras", "uf": "AL",
        "dominios": ["portodepedras.al.gov.br", "leismunicipais.com.br"],
        "base_estruturada": False,
        "portais": {"Prefeitura": "https://www.portodepedras.al.gov.br/"},
        "leis_chave": [],
        "armadilhas": ["Cartório de Porto de Pedras orientado pelo MPF a não registrar "
                       "incorporação sem servidão pública de acesso ao mar."],
    },
    "salvador": {
        "municipio": "Salvador", "uf": "BA",
        "dominios": ["salvador.ba.gov.br", "leismunicipais.com.br", "sedur.salvador.ba.gov.br"],
        "base_estruturada": False,
        "portais": {"SEDUR": "https://sedur.salvador.ba.gov.br/"},
        "leis_chave": ["PDDU 2016 — Art. 295 (fórmula da OODC)", "LOUOS"],
        "armadilhas": [],
    },
    "itacare": {
        "municipio": "Itacaré", "uf": "BA",
        "dominios": ["itacare.ba.gov.br", "leismunicipais.com.br", "inema.ba.gov.br"],
        "base_estruturada": False,
        "portais": {"Prefeitura": "https://www.itacare.ba.gov.br/"},
        "leis_chave": [], "armadilhas": [],
    },
}

# Sempre permitidos: bases legais nacionais e órgãos federais.
DOMINIOS_SEMPRE = [
    "planalto.gov.br",       # legislação federal (DL 9.760/1946, DL 2.398/1987, CF)
    "in.gov.br",             # Diário Oficial da União
    "leismunicipais.com.br", # compilado de legislação municipal
    "gov.br",                # órgãos federais (SPU, IPHAN, IBAMA)
]

# O que perguntar em CADA DD, independentemente do município. Deriva de R3 e R8.
CHECKLIST_LEGISLACAO = [
    ("zoneamento", "Qual o zoneamento do lote e quais os parâmetros (TO, CA, TP, recuos, "
                   "gabarito, usos permitidos)?"),
    ("outorga", "Há outorga onerosa (OODC)? Qual a fórmula vigente e o fator de "
                "planejamento/interesse? Há regra de transição por data de protocolo?"),
    ("incentivos", "Que incentivos existem (uso misto, TDC, arte pública, fruição, "
                   "sustentabilidade) e eles são CUMULATIVOS ou ALTERNATIVOS entre si?"),
    ("licenciamento", "Qual o rito de licenciamento e o que exclui do regime declaratório?"),
    ("eiv", "EIV é obrigatório para este porte/uso? Qual a norma?"),
    ("esgoto", "O licenciamento é condicionado a esgoto coletivo ou autônomo? Há ACP "
               "restringindo a bacia?"),
    ("ambiental", "Que restrições ambientais incidem (APP, UC, mangue, restinga, "
                  "supressão vegetal, compensação)?"),
    ("patrimonio", "Há tombamento, entorno tombado ou sítio arqueológico?"),
    ("bombeiro", "Qual a norma estadual do corpo de bombeiros e a classificação de "
                 "ocupação aplicável ao produto?"),
    ("vigencia", "Cada dispositivo citado está VIGENTE na data desta análise? Houve "
                 "alteração posterior?"),
]


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode("ascii")
    return s.lower().strip()


def perfil_municipio(municipio: str, uf: str = "") -> dict[str, Any]:
    """Registro do município, com fallback honesto quando não há registro."""
    chave = _norm(municipio)
    for k, v in PORTAIS.items():
        if k in chave or chave in k:
            return {**v, "conhecido": True}
    return {
        "municipio": municipio, "uf": uf, "conhecido": False,
        "base_estruturada": False,
        "dominios": [], "portais": {}, "leis_chave": [],
        "armadilhas": [],
        "nota": (f"Município '{municipio}' não está no registro de portais. Descubra o site "
                 f"oficial por busca (padrão usual: <municipio>.<uf>.gov.br) e trabalhe "
                 f"sobre TEXTO PRIMÁRIO — nunca sobre resumo de portal imobiliário."),
    }


def dominios_permitidos(municipio: str, uf: str = "") -> list[str]:
    """Allowlist para web_search/web_fetch. Vazia = sem restrição (município desconhecido)."""
    p = perfil_municipio(municipio, uf)
    if not p["conhecido"]:
        return []
    return sorted(set(p["dominios"]) | set(DOMINIOS_SEMPRE))


def orientar(municipio: str, uf: str = "", tema: str = "") -> dict[str, Any]:
    """
    Devolve ao agente o mapa da legislação daquele município: onde procurar, o que
    perguntar, o que costuma pegar, e o que ele NÃO pode fazer.
    """
    p = perfil_municipio(municipio, uf)
    checklist = ([q for k, q in CHECKLIST_LEGISLACAO if _norm(tema) in k or k in _norm(tema)]
                 if tema else [q for _, q in CHECKLIST_LEGISLACAO])

    return {
        "municipio": p["municipio"], "uf": p.get("uf") or uf,
        "municipio_conhecido": p["conhecido"],
        "tem_base_estruturada": p["base_estruturada"],
        "fonte": ("repositório MVP Legislação Florianópolis + portais oficiais"
                  if p["base_estruturada"] else
                  "sem base estruturada — usar web_search/web_fetch sobre texto primário"),
        "portais_oficiais": p["portais"],
        "dominios_confiaveis": dominios_permitidos(municipio, uf),
        "leis_chave_conhecidas": p["leis_chave"],
        "armadilhas_conhecidas": p["armadilhas"],
        "perguntar": checklist,
        "regras_inviolaveis": [
            "NUNCA citar lei ou parâmetro de memória — sempre do texto recuperado.",
            "A fonte oficial do zoneamento é a VIABILIDADE TÉCNICA CONSTRUTIVA emitida "
            "para ESTE terreno. A lei é fundamento; ela não substitui a consulta.",
            "Conferir VIGÊNCIA na data de hoje e se houve alteração posterior.",
            "Registrar a data da consulta em cada evidência de legislação.",
            "Blog, portal de notícia e site de imobiliária NÃO são fonte de lei.",
        ],
        "nota": p.get("nota", ""),
    }
